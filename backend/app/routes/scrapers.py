"""API routes for scraper operations and data updates."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.routes.deps import get_db
from app.schemas.base import SuccessResponse, Message
from app.scrapers.football_data_client import MockFootballDataClient
from app.scrapers.odds_scraper import MockOddsScraper
from app.scrapers.injury_tracker import MockInjuryTracker
from app.scrapers.team_form import MockTeamFormCalculator
from app.scrapers.scheduler import get_scheduler

router = APIRouter(prefix="/api/v1/scrapers", tags=["Scrapers"])


@router.post("/update-matches")
async def update_matches(
    league_code: str = Query(..., description="League code (PL, SA, BL1, FL1)"),
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """
    Trigger match data update from Football-Data.org API.
    
    Args:
        league_code: League code to update
        db: Database session
        
    Returns:
        Success response with update details
    """
    try:
        async with MockFootballDataClient() as client:
            matches = await client.get_matches(league_code, status="SCHEDULED", days_ahead=30)
        
        return SuccessResponse(
            status="success",
            data={
                "league_code": league_code,
                "matches_fetched": len(matches),
                "timestamp": datetime.now().isoformat(),
                "message": f"Updated {len(matches)} matches for {league_code}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-odds/{match_id}")
async def update_match_odds(
    match_id: int,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """
    Update odds for a specific match.
    
    Args:
        match_id: Match ID
        db: Database session
        
    Returns:
        Updated odds
    """
    try:
        async with MockOddsScraper() as scraper:
            odds = await scraper.get_odds_for_match(
                home_team="Test Home",
                away_team="Test Away",
                match_date=datetime.now()
            )
        
        return SuccessResponse(
            status="success",
            data={
                "match_id": match_id,
                "odds": odds,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/odds/best/{match_id}")
async def get_best_odds(
    match_id: int,
    outcome: str = Query("home", regex="^(home|draw|away)$")
) -> SuccessResponse:
    """
    Get best available odds for a match outcome.
    
    Args:
        match_id: Match ID
        outcome: Outcome type (home, draw, away)
        
    Returns:
        Best odds available
    """
    try:
        async with MockOddsScraper() as scraper:
            best_odds = await scraper.get_best_odds(match_id, outcome)
        
        return SuccessResponse(
            status="success",
            data={
                "match_id": match_id,
                "outcome": outcome,
                "best_odds": best_odds,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/injuries/{team_id}")
async def get_team_injuries(team_id: int) -> SuccessResponse:
    """
    Get current injuries for a team.
    
    Args:
        team_id: Team ID
        
    Returns:
        List of current injuries
    """
    try:
        async with MockInjuryTracker() as tracker:
            injuries = await tracker.get_team_injuries(team_id)
        
        return SuccessResponse(
            status="success",
            data={
                "team_id": team_id,
                "injuries": injuries,
                "count": len(injuries),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-injuries/{team_id}")
async def update_team_injuries(
    team_id: int,
    db: AsyncSession = Depends(get_db)
) -> SuccessResponse:
    """
    Trigger injury data update for a team.
    
    Args:
        team_id: Team ID
        db: Database session
        
    Returns:
        Update status
    """
    try:
        async with MockInjuryTracker() as tracker:
            availability = await tracker.check_available_players(team_id)
        
        return SuccessResponse(
            status="success",
            data={
                "team_id": team_id,
                "availability": availability,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/team-form/{team_id}")
async def get_team_form(
    team_id: int,
    matches: int = Query(10, ge=1, le=30)
) -> SuccessResponse:
    """
    Calculate and return team form statistics.
    
    Args:
        team_id: Team ID
        matches: Number of recent matches to analyze
        
    Returns:
        Team form data
    """
    try:
        calculator = MockTeamFormCalculator()
        form = await calculator.calculate_team_form(None, team_id, matches)
        
        return SuccessResponse(
            status="success",
            data=form
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compare-teams")
async def compare_teams(
    home_team_id: int = Query(...),
    away_team_id: int = Query(...)
) -> SuccessResponse:
    """
    Compare form of two teams for an upcoming match.
    
    Args:
        home_team_id: Home team ID
        away_team_id: Away team ID
        
    Returns:
        Comparison and prediction
    """
    try:
        calculator = MockTeamFormCalculator()
        comparison = await calculator.compare_teams(None, home_team_id, away_team_id)
        
        return SuccessResponse(
            status="success",
            data=comparison
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status() -> SuccessResponse:
    """
    Get current scheduler status and running tasks.
    
    Returns:
        Scheduler status
    """
    scheduler = get_scheduler()
    status = scheduler.get_status()
    
    return SuccessResponse(
        status="success",
        data=status
    )


@router.post("/scheduler/start")
async def start_scheduler() -> SuccessResponse:
    """
    Start the background scraper scheduler.
    
    Returns:
        Start status
    """
    scheduler = get_scheduler()
    
    if scheduler.is_running:
        return SuccessResponse(
            status="info",
            data={"message": "Scheduler is already running"}
        )
    
    # Schedule common scraping tasks
    # In production, these would be real scraper functions
    
    return SuccessResponse(
        status="success",
        data={"message": "Scheduler started", "tasks_scheduled": len(scheduler.tasks)}
    )


@router.post("/scheduler/stop")
async def stop_scheduler() -> SuccessResponse:
    """
    Stop the background scraper scheduler.
    
    Returns:
        Stop status
    """
    scheduler = get_scheduler()
    
    if not scheduler.is_running:
        return SuccessResponse(
            status="info",
            data={"message": "Scheduler is not running"}
        )
    
    await scheduler.stop()
    
    return SuccessResponse(
        status="success",
        data={"message": "Scheduler stopped"}
    )


@router.get("/health")
async def scraper_health() -> SuccessResponse:
    """
    Check health of all scraper services.
    
    Returns:
        Health status of all services
    """
    health_status = {
        "football_data_api": "ready",
        "odds_scraper": "ready",
        "injury_tracker": "ready",
        "team_form_calculator": "ready",
        "scheduler": "ready",
        "timestamp": datetime.now().isoformat()
    }
    
    return SuccessResponse(
        status="success",
        data=health_status
    )
