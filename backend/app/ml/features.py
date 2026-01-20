"""Feature engineering pipeline for ML models."""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging

from app.models import Match, Team, Injury, Odds
from app.ml.config import FeatureConfig

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Engineer features from raw data."""
    
    def __init__(self, config: Optional[FeatureConfig] = None):
        self.config = config or FeatureConfig.default()
        self.feature_names = []
    
    async def extract_features(
        self,
        db: AsyncSession,
        matches: List[Match],
        target_date: Optional[datetime] = None
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Extract features for matches.
        
        Args:
            db: Database session
            matches: List of matches
            target_date: Date to compute features relative to
            
        Returns:
            Feature matrix and feature names
        """
        features_list = []
        
        for match in matches:
            features = await self._extract_match_features(
                db, match, target_date
            )
            if features is not None:
                features_list.append(features)
        
        if not features_list:
            return np.array([]), []
        
        # Convert to numpy array
        X = np.array(features_list)
        
        return X, self.feature_names
    
    async def _extract_match_features(
        self,
        db: AsyncSession,
        match: Match,
        target_date: Optional[datetime] = None
    ) -> Optional[List[float]]:
        """Extract features for a single match."""
        try:
            target_date = target_date or match.match_date
            
            features = []
            feature_names = []
            
            # 1. Team-based features
            home_features = await self._get_team_features(
                db, match.home_team_id, target_date
            )
            away_features = await self._get_team_features(
                db, match.away_team_id, target_date
            )
            
            if home_features is None or away_features is None:
                return None
            
            features.extend(home_features[0])
            feature_names.extend([f"home_{n}" for n in home_features[1]])
            
            features.extend(away_features[0])
            feature_names.extend([f"away_{n}" for n in away_features[1]])
            
            # 2. Form features (team form difference)
            home_form = await self._get_team_form(
                db, match.home_team_id, target_date
            )
            away_form = await self._get_team_form(
                db, match.away_team_id, target_date
            )
            
            features.extend([home_form, away_form, home_form - away_form])
            feature_names.extend(["home_form", "away_form", "form_diff"])
            
            # 3. Head-to-head features
            h2h_features = await self._get_head_to_head(
                db, match.home_team_id, match.away_team_id, target_date
            )
            features.extend(h2h_features[0])
            feature_names.extend(h2h_features[1])
            
            # 4. Injury features
            home_injuries = await self._get_injury_count(
                db, match.home_team_id, target_date
            )
            away_injuries = await self._get_injury_count(
                db, match.away_team_id, target_date
            )
            
            features.extend([home_injuries, away_injuries])
            feature_names.extend(["home_injuries", "away_injuries"])
            
            # 5. Odds features
            if match.odds:
                odds_features = self._get_odds_features(match.odds)
                features.extend(odds_features[0])
                feature_names.extend(odds_features[1])
            else:
                features.extend([1.0, 1.0, 1.0])
                feature_names.extend(["odd_home", "odd_draw", "odd_away"])
            
            # 6. Rest days
            home_rest = await self._get_rest_days(
                db, match.home_team_id, match.match_date
            )
            away_rest = await self._get_rest_days(
                db, match.away_team_id, match.match_date
            )
            
            features.extend([home_rest, away_rest])
            feature_names.extend(["home_rest_days", "away_rest_days"])
            
            # Update global feature names (only once)
            if not self.feature_names:
                self.feature_names = feature_names
            
            return features
        
        except Exception as e:
            logger.error(f"Error extracting features for match {match.id}: {e}")
            return None
    
    async def _get_team_features(
        self,
        db: AsyncSession,
        team_id: int,
        target_date: datetime
    ) -> Optional[Tuple[List[float], List[str]]]:
        """Get team-based features."""
        try:
            # Get team stats from last N matches
            result = await db.execute(
                select(Match).filter(
                    ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                    Match.status == "FINISHED",
                    Match.match_date < target_date
                ).order_by(Match.match_date.desc()).limit(self.config.form_window)
            )
            recent_matches = result.scalars().all()
            
            if not recent_matches:
                # Return neutral stats for teams with no history
                return [
                    [0.5, 0.5, 0.0, 0.0, 1.0, 1.0],
                    ["win_rate", "draw_rate", "goals_scored_avg", "goals_conceded_avg", "possession", "passing_acc"]
                ]
            
            wins = 0
            draws = 0
            goals_for = 0
            goals_against = 0
            
            for match in recent_matches:
                if match.home_team_id == team_id:
                    goals_for += match.home_score or 0
                    goals_against += match.away_score or 0
                    
                    if match.home_score > match.away_score:
                        wins += 1
                    elif match.home_score == match.away_score:
                        draws += 1
                else:
                    goals_for += match.away_score or 0
                    goals_against += match.home_score or 0
                    
                    if match.away_score > match.home_score:
                        wins += 1
                    elif match.away_score == match.home_score:
                        draws += 1
            
            matches_count = len(recent_matches)
            win_rate = wins / matches_count if matches_count > 0 else 0
            draw_rate = draws / matches_count if matches_count > 0 else 0
            goals_scored_avg = goals_for / matches_count if matches_count > 0 else 0
            goals_conceded_avg = goals_against / matches_count if matches_count > 0 else 0
            
            return [
                [
                    win_rate,
                    draw_rate,
                    goals_scored_avg,
                    goals_conceded_avg,
                    0.5,  # Placeholder for possession
                    0.8   # Placeholder for passing accuracy
                ],
                ["win_rate", "draw_rate", "goals_scored_avg", "goals_conceded_avg", "possession", "passing_acc"]
            ]
        
        except Exception as e:
            logger.error(f"Error getting team features: {e}")
            return None
    
    async def _get_team_form(
        self,
        db: AsyncSession,
        team_id: int,
        target_date: datetime
    ) -> float:
        """Get team form (points from recent matches)."""
        try:
            result = await db.execute(
                select(Match).filter(
                    ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                    Match.status == "FINISHED",
                    Match.match_date < target_date
                ).order_by(Match.match_date.desc()).limit(self.config.form_window)
            )
            recent_matches = result.scalars().all()
            
            points = 0
            for match in recent_matches:
                if match.home_team_id == team_id:
                    if match.home_score > match.away_score:
                        points += 3
                    elif match.home_score == match.away_score:
                        points += 1
                else:
                    if match.away_score > match.home_score:
                        points += 3
                    elif match.away_score == match.home_score:
                        points += 1
            
            return float(points)
        
        except Exception as e:
            logger.error(f"Error getting team form: {e}")
            return 0.0
    
    async def _get_head_to_head(
        self,
        db: AsyncSession,
        home_id: int,
        away_id: int,
        target_date: datetime
    ) -> Tuple[List[float], List[str]]:
        """Get head-to-head features."""
        try:
            result = await db.execute(
                select(Match).filter(
                    (
                        ((Match.home_team_id == home_id) & (Match.away_team_id == away_id)) |
                        ((Match.home_team_id == away_id) & (Match.away_team_id == home_id))
                    ),
                    Match.status == "FINISHED",
                    Match.match_date < target_date
                ).order_by(Match.match_date.desc()).limit(self.config.head_to_head_window)
            )
            h2h_matches = result.scalars().all()
            
            home_wins = 0
            away_wins = 0
            draws = 0
            home_goals = 0
            away_goals = 0
            
            for match in h2h_matches:
                if match.home_team_id == home_id:
                    home_goals += match.home_score or 0
                    away_goals += match.away_score or 0
                    
                    if match.home_score > match.away_score:
                        home_wins += 1
                    elif match.home_score < match.away_score:
                        away_wins += 1
                    else:
                        draws += 1
                else:
                    home_goals += match.away_score or 0
                    away_goals += match.home_score or 0
                    
                    if match.away_score > match.home_score:
                        home_wins += 1
                    elif match.away_score < match.home_score:
                        away_wins += 1
                    else:
                        draws += 1
            
            matches_count = len(h2h_matches)
            if matches_count == 0:
                return [
                    [0.5, 0.5, 0.0],
                    ["h2h_home_win_rate", "h2h_away_win_rate", "h2h_avg_total_goals"]
                ]
            
            return [
                [
                    home_wins / matches_count,
                    away_wins / matches_count,
                    (home_goals + away_goals) / matches_count
                ],
                ["h2h_home_win_rate", "h2h_away_win_rate", "h2h_avg_total_goals"]
            ]
        
        except Exception as e:
            logger.error(f"Error getting h2h: {e}")
            return [[0.5, 0.5, 0.0], ["h2h_home_win_rate", "h2h_away_win_rate", "h2h_avg_total_goals"]]
    
    async def _get_injury_count(
        self,
        db: AsyncSession,
        team_id: int,
        target_date: datetime
    ) -> float:
        """Get current injury count."""
        try:
            date_threshold = target_date - timedelta(days=self.config.injury_window)
            result = await db.execute(
                select(func.count(Injury.id)).filter(
                    Injury.team_id == team_id,
                    Injury.start_date <= target_date,
                    (Injury.end_date.is_(None)) | (Injury.end_date >= target_date)
                )
            )
            count = result.scalar() or 0
            return float(min(count, 5))  # Cap at 5 key injuries
        
        except Exception as e:
            logger.error(f"Error getting injury count: {e}")
            return 0.0
    
    def _get_odds_features(self, odds: Odds) -> Tuple[List[float], List[str]]:
        """Get odds-based features."""
        return [
            [
                float(odds.home_win or 1.0),
                float(odds.draw or 1.0),
                float(odds.away_win or 1.0)
            ],
            ["odd_home", "odd_draw", "odd_away"]
        ]
    
    async def _get_rest_days(
        self,
        db: AsyncSession,
        team_id: int,
        match_date: datetime
    ) -> float:
        """Get days of rest before match."""
        try:
            result = await db.execute(
                select(Match).filter(
                    ((Match.home_team_id == team_id) | (Match.away_team_id == team_id)),
                    Match.status == "FINISHED",
                    Match.match_date < match_date
                ).order_by(Match.match_date.desc()).limit(1)
            )
            last_match = result.scalars().first()
            
            if last_match:
                rest_days = (match_date - last_match.match_date).days
                return float(min(rest_days, 14))  # Cap at 14 days
            
            return 14.0  # Default to max rest if no previous match
        
        except Exception as e:
            logger.error(f"Error getting rest days: {e}")
            return 7.0
