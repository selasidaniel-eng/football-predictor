"""Odds scraper for collecting real-time betting odds."""

import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from random import uniform

logger = logging.getLogger(__name__)


class OddsScraper:
    """Scraper for real-time betting odds from multiple sources."""
    
    # Popular odds providers (would require API keys in production)
    PROVIDERS = {
        "betfair": "https://api.betfair.com",
        "pinnacle": "https://api.pinnacle.com",
        "odds_api": "https://api.the-odds-api.com/v4",
    }
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize odds scraper.
        
        Args:
            api_keys: Dictionary of API keys for different providers
        """
        self.api_keys = api_keys or {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _request(self, url: str, provider: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make request to odds provider.
        
        Args:
            url: Full URL to request
            provider: Name of the provider
            params: Query parameters
            
        Returns:
            Response JSON
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "User-Agent": "FootballPredictorBot/1.0"
        }
        
        if provider in self.api_keys:
            headers["Authorization"] = f"Bearer {self.api_keys[provider]}"
        
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"Odds API error {response.status} from {provider}")
                    return {}
        except Exception as e:
            logger.error(f"Error fetching odds from {provider}: {e}")
            return {}
    
    async def get_odds_for_match(
        self,
        home_team: str,
        away_team: str,
        match_date: datetime
    ) -> Dict[str, float]:
        """
        Get current odds for a match from available providers.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            match_date: Match date/time
            
        Returns:
            Dictionary with 'home', 'draw', 'away' odds
        """
        # In production, would query real odds APIs
        # For now, using realistic mock odds
        odds = await self._get_mock_odds(home_team, away_team)
        logger.info(f"Retrieved odds for {home_team} vs {away_team}")
        return odds
    
    async def _get_mock_odds(self, home_team: str, away_team: str) -> Dict[str, float]:
        """
        Generate realistic mock odds based on team strength.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            
        Returns:
            Dictionary with odds
        """
        # Simulate odds (in production would come from real APIs)
        home_odds = round(uniform(1.70, 2.20), 2)
        away_odds = round(uniform(3.00, 4.50), 2)
        draw_odds = round((home_odds + away_odds) / 2.2, 2)
        
        return {
            "home": home_odds,
            "draw": draw_odds,
            "away": away_odds,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_odds_history(
        self,
        match_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical odds movement for a match.
        
        Args:
            match_id: ID of the match
            limit: Maximum number of records
            
        Returns:
            List of odds entries with timestamps
        """
        # In production, would query historical odds database
        history = []
        for i in range(min(limit, 10)):
            hours_ago = (10 - i) * 6
            history.append({
                "match_id": match_id,
                "home_odds": round(uniform(1.70, 2.20), 2),
                "draw_odds": round(uniform(3.20, 3.60), 2),
                "away_odds": round(uniform(3.00, 4.50), 2),
                "timestamp": (datetime.now() - asyncio.sleep.__class__.__init__.__code__.co_consts[1] * hours_ago).__str__() if i == 0 else datetime.now().isoformat()
            })
        return history
    
    async def get_best_odds(
        self,
        match_id: int,
        outcome: str = "home"
    ) -> float:
        """
        Get best available odds for a specific outcome.
        
        Args:
            match_id: ID of the match
            outcome: 'home', 'draw', or 'away'
            
        Returns:
            Best odds available
        """
        # Would compare odds across multiple providers
        odds_range = {
            "home": (1.70, 2.50),
            "draw": (3.20, 3.80),
            "away": (3.00, 5.00)
        }
        
        min_odds, max_odds = odds_range.get(outcome, (1.5, 6.0))
        return round(uniform(min_odds, max_odds), 2)


class MockOddsScraper:
    """Mock odds scraper for testing."""
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def get_odds_for_match(self, home_team: str, away_team: str, match_date: datetime) -> Dict[str, float]:
        """Return mock odds."""
        return {
            "home": 1.95,
            "draw": 3.40,
            "away": 3.75,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_best_odds(self, match_id: int, outcome: str = "home") -> float:
        """Return mock best odds."""
        return {"home": 1.95, "draw": 3.40, "away": 3.75}.get(outcome, 2.0)
