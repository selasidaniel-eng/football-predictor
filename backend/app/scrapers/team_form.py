"""Team form calculator for computing team performance metrics."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Match

logger = logging.getLogger(__name__)


class TeamFormCalculator:
    """Calculator for team form and performance metrics."""
    
    def __init__(self):
        """Initialize team form calculator."""
        self.cache: Dict[int, Dict[str, Any]] = {}
    
    async def calculate_team_form(
        self,
        session: AsyncSession,
        team_id: int,
        matches_limit: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate team form based on recent matches.
        
        Args:
            session: Database session
            team_id: Team ID
            matches_limit: Number of recent matches to analyze
            
        Returns:
            Team form statistics
        """
        # Get recent matches
        recent_matches = await self._get_recent_matches(session, team_id, matches_limit)
        
        if not recent_matches:
            return self._empty_form()
        
        form = {
            "team_id": team_id,
            "last_updated": datetime.now().isoformat(),
            "matches_analyzed": len(recent_matches),
        }
        
        # Calculate results
        form.update(self._calculate_results(recent_matches, team_id))
        
        # Calculate statistics
        form.update(self._calculate_statistics(recent_matches, team_id))
        
        # Calculate form
        form.update(self._calculate_form(recent_matches, team_id))
        
        # Calculate trend
        form.update(self._calculate_trend(recent_matches, team_id))
        
        return form
    
    async def _get_recent_matches(
        self,
        session: AsyncSession,
        team_id: int,
        limit: int
    ) -> List[Match]:
        """Get recent finished matches for a team."""
        result = await session.execute(
            select(Match)
            .filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
                Match.status == "FINISHED"
            )
            .order_by(Match.match_date.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    def _empty_form(self) -> Dict[str, Any]:
        """Return empty form structure."""
        return {
            "team_id": None,
            "matches_analyzed": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "form_rating": 5.0,
            "recent_form": "NNNNN",  # No matches
            "trend": "STABLE",
            "goals_for": 0,
            "goals_against": 0,
            "goal_difference": 0
        }
    
    def _calculate_results(self, matches: List[Match], team_id: int) -> Dict[str, int]:
        """Calculate win/draw/loss counts."""
        wins = draws = losses = 0
        
        for match in matches:
            is_home = match.home_team_id == team_id
            
            if match.home_goals is None or match.away_goals is None:
                continue
            
            team_goals = match.home_goals if is_home else match.away_goals
            opponent_goals = match.away_goals if is_home else match.home_goals
            
            if team_goals > opponent_goals:
                wins += 1
            elif team_goals < opponent_goals:
                losses += 1
            else:
                draws += 1
        
        total = wins + draws + losses
        
        return {
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "win_rate": (wins / total * 100) if total > 0 else 0,
            "total_matches": total
        }
    
    def _calculate_statistics(self, matches: List[Match], team_id: int) -> Dict[str, float]:
        """Calculate goal and point statistics."""
        goals_for = 0
        goals_against = 0
        points = 0
        
        for match in matches:
            is_home = match.home_team_id == team_id
            
            if match.home_goals is None or match.away_goals is None:
                continue
            
            team_goals = match.home_goals if is_home else match.away_goals
            opponent_goals = match.away_goals if is_home else match.home_goals
            
            goals_for += team_goals
            goals_against += opponent_goals
            
            if team_goals > opponent_goals:
                points += 3
            elif team_goals == opponent_goals:
                points += 1
        
        total_matches = len([m for m in matches if m.home_goals is not None])
        
        return {
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goals_for - goals_against,
            "goals_per_match": (goals_for / total_matches) if total_matches > 0 else 0,
            "points": points,
            "points_per_match": (points / total_matches) if total_matches > 0 else 0
        }
    
    def _calculate_form(self, matches: List[Match], team_id: int) -> Dict[str, Any]:
        """Calculate current form rating and string."""
        # Get last 5 matches for form string
        form_string = ""
        form_score = 0
        
        for match in matches[:5]:
            is_home = match.home_team_id == team_id
            
            if match.home_goals is None or match.away_goals is None:
                continue
            
            team_goals = match.home_goals if is_home else match.away_goals
            opponent_goals = match.away_goals if is_home else match.home_goals
            
            if team_goals > opponent_goals:
                form_string = "W" + form_string
                form_score += 3
            elif team_goals < opponent_goals:
                form_string = "L" + form_string
                form_score += 0
            else:
                form_string = "D" + form_string
                form_score += 1
        
        # Pad form string to 5 characters
        form_string = form_string.ljust(5, 'N')[:5]
        
        # Calculate form rating (0-10)
        form_rating = min(10, (form_score / 5 * 10 / 3)) if len(form_string.replace('N', '')) > 0 else 5.0
        
        return {
            "recent_form": form_string,
            "form_rating": round(form_rating, 2)
        }
    
    def _calculate_trend(self, matches: List[Match], team_id: int) -> Dict[str, str]:
        """Calculate form trend (improving, declining, stable)."""
        if len(matches) < 4:
            return {"trend": "INSUFFICIENT_DATA"}
        
        # Compare first 3 matches vs last 3 matches
        first_period_points = 0
        second_period_points = 0
        
        for i, match in enumerate(matches):
            is_home = match.home_team_id == team_id
            
            if match.home_goals is None or match.away_goals is None:
                continue
            
            team_goals = match.home_goals if is_home else match.away_goals
            opponent_goals = match.away_goals if is_home else match.home_goals
            
            points = 3 if team_goals > opponent_goals else (1 if team_goals == opponent_goals else 0)
            
            if i < 3:
                first_period_points += points
            elif i < 6:
                second_period_points += points
        
        if second_period_points > first_period_points + 2:
            trend = "IMPROVING"
        elif second_period_points < first_period_points - 2:
            trend = "DECLINING"
        else:
            trend = "STABLE"
        
        return {"trend": trend}
    
    async def compare_teams(
        self,
        session: AsyncSession,
        home_team_id: int,
        away_team_id: int
    ) -> Dict[str, Any]:
        """
        Compare form of two teams.
        
        Args:
            session: Database session
            home_team_id: Home team ID
            away_team_id: Away team ID
            
        Returns:
            Comparison statistics
        """
        home_form = await self.calculate_team_form(session, home_team_id)
        away_form = await self.calculate_team_form(session, away_team_id)
        
        return {
            "home_team": home_form,
            "away_team": away_form,
            "home_advantage": home_form["form_rating"] - away_form["form_rating"],
            "prediction": self._predict_outcome(home_form, away_form)
        }
    
    def _predict_outcome(self, home_form: Dict[str, Any], away_form: Dict[str, Any]) -> Dict[str, float]:
        """Simple outcome prediction based on form."""
        home_strength = home_form.get("form_rating", 5.0) + 0.5  # Home advantage
        away_strength = away_form.get("form_rating", 5.0)
        
        total = home_strength + away_strength + 5
        
        home_prob = home_strength / total
        away_prob = away_strength / total
        draw_prob = 5 / total
        
        return {
            "home_win_probability": round(home_prob, 3),
            "draw_probability": round(draw_prob, 3),
            "away_win_probability": round(away_prob, 3)
        }


class MockTeamFormCalculator:
    """Mock team form calculator for testing."""
    
    async def calculate_team_form(self, session: AsyncSession, team_id: int, matches_limit: int = 10) -> Dict[str, Any]:
        """Return mock team form."""
        return {
            "team_id": team_id,
            "last_updated": datetime.now().isoformat(),
            "matches_analyzed": 5,
            "wins": 3,
            "draws": 1,
            "losses": 1,
            "form_rating": 7.5,
            "recent_form": "WDWWL",
            "trend": "STABLE",
            "goals_for": 12,
            "goals_against": 5,
            "goal_difference": 7
        }
    
    async def compare_teams(self, session: AsyncSession, home_team_id: int, away_team_id: int) -> Dict[str, Any]:
        """Return mock comparison."""
        return {
            "home_team": {"team_id": home_team_id, "form_rating": 7.5},
            "away_team": {"team_id": away_team_id, "form_rating": 6.2},
            "prediction": {"home_win_probability": 0.45, "draw_probability": 0.28, "away_win_probability": 0.27}
        }
