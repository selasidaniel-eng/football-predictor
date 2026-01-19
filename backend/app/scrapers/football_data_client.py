"""Football-Data.org API client for fetching real match and team data."""

import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FootballDataClient:
    """Client for Football-Data.org API."""
    
    BASE_URL = "https://api.football-data.org/v4"
    
    # League codes for popular leagues
    LEAGUE_CODES = {
        "Premier League": "PL",
        "La Liga": "SA",
        "Serie A": "SA",
        "Bundesliga": "BL1",
        "Ligue 1": "FL1",
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Football-Data client.
        
        Args:
            api_key: Football-Data.org API key (free tier available)
        """
        self.api_key = api_key
        self.headers = {
            "X-Auth-Token": api_key or "demo_key",
            "User-Agent": "FootballPredictorBot/1.0"
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make authenticated request to Football-Data API.
        
        Args:
            endpoint: API endpoint (e.g., '/competitions/PL/matches')
            params: Query parameters
            
        Returns:
            Response JSON data
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            async with self.session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("API rate limit hit, waiting before retry...")
                    await asyncio.sleep(60)
                    return await self._request(endpoint, params)
                else:
                    logger.error(f"API error {response.status}: {await response.text()}")
                    return {}
        except asyncio.TimeoutError:
            logger.error(f"Timeout requesting {endpoint}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return {}
    
    async def get_matches(
        self,
        league_code: str,
        status: str = "SCHEDULED",
        days_ahead: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming or past matches for a league.
        
        Args:
            league_code: League code (e.g., 'PL' for Premier League)
            status: Match status filter (SCHEDULED, LIVE, FINISHED)
            days_ahead: Number of days to look ahead
            
        Returns:
            List of match data
        """
        date_from = datetime.now().date()
        date_to = (datetime.now() + timedelta(days=days_ahead)).date()
        
        params = {
            "status": status,
            "dateFrom": date_from.isoformat(),
            "dateTo": date_to.isoformat(),
        }
        
        data = await self._request(f"/competitions/{league_code}/matches", params)
        return data.get("matches", [])
    
    async def get_teams(self, league_code: str) -> List[Dict[str, Any]]:
        """
        Get all teams in a league.
        
        Args:
            league_code: League code
            
        Returns:
            List of team data
        """
        data = await self._request(f"/competitions/{league_code}/teams")
        return data.get("teams", [])
    
    async def get_team(self, team_id: int) -> Dict[str, Any]:
        """
        Get detailed info for a specific team.
        
        Args:
            team_id: Football-Data team ID
            
        Returns:
            Team data
        """
        return await self._request(f"/teams/{team_id}")
    
    async def get_squad(self, team_id: int) -> List[Dict[str, Any]]:
        """
        Get squad (players) for a team.
        
        Args:
            team_id: Football-Data team ID
            
        Returns:
            List of players
        """
        data = await self._request(f"/teams/{team_id}")
        return data.get("squad", [])
    
    async def get_standings(self, league_code: str) -> Dict[str, Any]:
        """
        Get league standings/table.
        
        Args:
            league_code: League code
            
        Returns:
            Standings data
        """
        return await self._request(f"/competitions/{league_code}/standings")
    
    async def get_match_details(self, match_id: int) -> Dict[str, Any]:
        """
        Get detailed info for a specific match.
        
        Args:
            match_id: Football-Data match ID
            
        Returns:
            Match details
        """
        return await self._request(f"/matches/{match_id}")


# Fallback mock client for testing without API key
class MockFootballDataClient:
    """Mock Football-Data client for testing."""
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def get_matches(self, league_code: str, status: str = "SCHEDULED", days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Return mock matches."""
        return [
            {
                "id": 1,
                "utcDate": (datetime.now() + timedelta(days=7)).isoformat(),
                "status": "SCHEDULED",
                "homeTeam": {"id": 1, "name": "Team A"},
                "awayTeam": {"id": 2, "name": "Team B"},
                "score": {"fullTime": {"home": None, "away": None}},
            }
        ]
    
    async def get_teams(self, league_code: str) -> List[Dict[str, Any]]:
        """Return mock teams."""
        return [
            {"id": 1, "name": "Team A", "shortName": "TA", "area": {"name": "England"}},
            {"id": 2, "name": "Team B", "shortName": "TB", "area": {"name": "England"}},
        ]
    
    async def get_standings(self, league_code: str) -> Dict[str, Any]:
        """Return mock standings."""
        return {
            "standings": [
                {
                    "type": "TOTAL",
                    "table": [
                        {"position": 1, "team": {"id": 1, "name": "Team A"}, "points": 30, "played": 10},
                    ]
                }
            ]
        }
