"""Feature engineering pipeline for ML models."""

from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime, timedelta
import logging
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Match, Team, Injury
from app.ml import FeatureSet

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for football match prediction."""
    
    def __init__(self, lookback_matches: int = 10):
        """
        Initialize feature engineer.
        
        Args:
            lookback_matches: Number of recent matches to consider
        """
        self.lookback_matches = lookback_matches
        self.feature_names = [
            # Team form features
            "home_form_rating",
            "away_form_rating",
            "home_recent_form",
            "away_recent_form",
            "home_win_rate",
            "away_win_rate",
            
            # Strength features
            "home_strength_rating",
            "away_strength_rating",
            "home_advantage_rating",
            
            # Goal features
            "home_goals_per_match",
            "away_goals_per_match",
            "home_goals_against_per_match",
            "away_goals_against_per_match",
            "home_goal_difference",
            "away_goal_difference",
            
            # Head-to-head features
            "h2h_home_wins",
            "h2h_draws",
            "h2h_away_wins",
            "h2h_home_goals",
            "h2h_away_goals",
            
            # Injury features
            "home_injury_count",
            "away_injury_count",
            "home_injury_impact",
            "away_injury_impact",
            
            # Market features
            "home_odds",
            "draw_odds",
            "away_odds",
            "implied_probability_home",
            "implied_probability_draw",
            "implied_probability_away",
        ]
    
    async def extract_features(
        self,
        session: AsyncSession,
        match: Match
    ) -> Dict[str, float]:
        """
        Extract features for a match.
        
        Args:
            session: Database session
            match: Match object
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Get home and away teams
        home_team = match.home_team
        away_team = match.away_team
        
        # Team form features
        home_form = await self._extract_team_form(session, home_team.id)
        away_form = await self._extract_team_form(session, away_team.id)
        
        features.update({
            "home_form_rating": home_form.get("form_rating", 5.0),
            "away_form_rating": away_form.get("form_rating", 5.0),
            "home_recent_form": self._encode_form_string(home_form.get("recent_form", "NNNNN")),
            "away_recent_form": self._encode_form_string(away_form.get("recent_form", "NNNNN")),
            "home_win_rate": home_form.get("win_rate", 0.0),
            "away_win_rate": away_form.get("win_rate", 0.0),
        })
        
        # Strength features
        features.update({
            "home_strength_rating": home_team.strength_rating or 70.0,
            "away_strength_rating": away_team.strength_rating or 70.0,
            "home_advantage_rating": home_team.home_advantage or 1.0,
        })
        
        # Goal features
        home_goals = home_form.get("goals_for", 0)
        home_goals_against = home_form.get("goals_against", 0)
        away_goals = away_form.get("goals_for", 0)
        away_goals_against = away_form.get("goals_against", 0)
        total_home = home_form.get("total_matches", 1)
        total_away = away_form.get("total_matches", 1)
        
        features.update({
            "home_goals_per_match": home_goals / total_home if total_home > 0 else 0,
            "away_goals_per_match": away_goals / total_away if total_away > 0 else 0,
            "home_goals_against_per_match": home_goals_against / total_home if total_home > 0 else 0,
            "away_goals_against_per_match": away_goals_against / total_away if total_away > 0 else 0,
            "home_goal_difference": home_form.get("goal_difference", 0),
            "away_goal_difference": away_form.get("goal_difference", 0),
        })
        
        # Head-to-head features
        h2h = await self._extract_h2h_features(session, home_team.id, away_team.id)
        features.update({
            "h2h_home_wins": h2h.get("home_wins", 0),
            "h2h_draws": h2h.get("draws", 0),
            "h2h_away_wins": h2h.get("away_wins", 0),
            "h2h_home_goals": h2h.get("home_goals", 0),
            "h2h_away_goals": h2h.get("away_goals", 0),
        })
        
        # Injury features
        home_injuries = await self._extract_team_injuries(session, home_team.id)
        away_injuries = await self._extract_team_injuries(session, away_team.id)
        
        features.update({
            "home_injury_count": home_injuries["count"],
            "away_injury_count": away_injuries["count"],
            "home_injury_impact": home_injuries["impact_score"],
            "away_injury_impact": away_injuries["impact_score"],
        })
        
        # Market features (odds)
        total_odds = (match.home_odds or 1.5) + (match.draw_odds or 3.5) + (match.away_odds or 4.0)
        
        features.update({
            "home_odds": match.home_odds or 1.5,
            "draw_odds": match.draw_odds or 3.5,
            "away_odds": match.away_odds or 4.0,
            "implied_probability_home": 1 / (match.home_odds or 1.5) / total_odds * 3,
            "implied_probability_draw": 1 / (match.draw_odds or 3.5) / total_odds * 3,
            "implied_probability_away": 1 / (match.away_odds or 4.0) / total_odds * 3,
        })
        
        return features
    
    async def _extract_team_form(self, session: AsyncSession, team_id: int) -> Dict[str, Any]:
        """Extract form features for a team."""
        # Get recent matches
        result = await session.execute(
            select(Match)
            .filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
                Match.status == "FINISHED"
            )
            .order_by(Match.match_date.desc())
            .limit(self.lookback_matches)
        )
        matches = result.scalars().all()
        
        if not matches:
            return {
                "form_rating": 5.0,
                "recent_form": "NNNNN",
                "win_rate": 0.0,
                "goals_for": 0,
                "goals_against": 0,
                "goal_difference": 0,
                "total_matches": 0
            }
        
        wins = draws = losses = 0
        goals_for = goals_against = 0
        form_str = ""
        
        for match in matches:
            is_home = match.home_team_id == team_id
            team_goals = match.home_goals if is_home else match.away_goals
            opponent_goals = match.away_goals if is_home else match.home_goals
            
            if team_goals is None or opponent_goals is None:
                continue
            
            goals_for += team_goals
            goals_against += opponent_goals
            
            if team_goals > opponent_goals:
                wins += 1
                form_str = "W" + form_str
            elif team_goals < opponent_goals:
                losses += 1
                form_str = "L" + form_str
            else:
                draws += 1
                form_str = "D" + form_str
        
        form_str = form_str.ljust(5, 'N')[:5]
        total = wins + draws + losses
        
        return {
            "form_rating": (wins * 3 + draws) / total / 3 * 10 if total > 0 else 5.0,
            "recent_form": form_str,
            "win_rate": (wins / total * 100) if total > 0 else 0.0,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "total_matches": total
        }
    
    async def _extract_h2h_features(
        self,
        session: AsyncSession,
        home_team_id: int,
        away_team_id: int
    ) -> Dict[str, Any]:
        """Extract head-to-head features between two teams."""
        result = await session.execute(
            select(Match).filter(
                (
                    (Match.home_team_id == home_team_id) & (Match.away_team_id == away_team_id)
                ) | (
                    (Match.home_team_id == away_team_id) & (Match.away_team_id == home_team_id)
                ),
                Match.status == "FINISHED"
            ).order_by(Match.match_date.desc()).limit(10)
        )
        matches = result.scalars().all()
        
        home_wins = draws = away_wins = 0
        home_goals = away_goals = 0
        
        for match in matches:
            is_home_playing_home = match.home_team_id == home_team_id
            team_goals = match.home_goals if is_home_playing_home else match.away_goals
            opponent_goals = match.away_goals if is_home_playing_home else match.home_goals
            
            if team_goals is None or opponent_goals is None:
                continue
            
            home_goals += team_goals
            away_goals += opponent_goals
            
            if is_home_playing_home:
                if team_goals > opponent_goals:
                    home_wins += 1
                elif team_goals == opponent_goals:
                    draws += 1
                else:
                    away_wins += 1
            else:
                if team_goals > opponent_goals:
                    away_wins += 1
                elif team_goals == opponent_goals:
                    draws += 1
                else:
                    home_wins += 1
        
        return {
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "home_goals": home_goals,
            "away_goals": away_goals,
        }
    
    async def _extract_team_injuries(self, session: AsyncSession, team_id: int) -> Dict[str, Any]:
        """Extract injury features for a team."""
        result = await session.execute(
            select(Injury).filter(
                Injury.team_id == team_id,
                Injury.expected_return > datetime.now()
            )
        )
        injuries = result.scalars().all()
        
        impact_score = sum(inj.impact_score or 5 for inj in injuries)
        
        return {
            "count": len(injuries),
            "impact_score": impact_score
        }
    
    def _encode_form_string(self, form_str: str) -> float:
        """Encode form string to numerical value."""
        # WWWWW = 10, LLLLL = 0
        weights = [5, 3, 2, 1, 1]  # Recency weighting
        score = 0
        
        for i, char in enumerate(form_str):
            if char == 'W':
                score += 3 * weights[i]
            elif char == 'D':
                score += 1 * weights[i]
        
        total_weight = sum(weights)
        return (score / total_weight / 3 * 10) if total_weight > 0 else 5.0
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names."""
        return self.feature_names
