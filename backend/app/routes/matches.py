"""
API routes for Match management.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Match, Team, League
from app.schemas import (
    MatchCreate,
    MatchUpdate,
    MatchResponse,
    MatchDetailResponse,
    PaginatedResponse,
    Message,
)
from .deps import get_db

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])


@router.get("", response_model=PaginatedResponse[MatchResponse])
async def list_matches(
    db: AsyncSession = Depends(get_db),
    league_id: int = Query(None, description="Filter by league ID"),
    team_id: int = Query(None, description="Filter by team (home or away)"),
    status_filter: str = Query(None, description="Filter by status (scheduled/live/finished)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[MatchResponse]:
    """
    Retrieve all matches with optional filtering.
    
    Query Parameters:
    - league_id: Filter by league ID (optional)
    - team_id: Filter by team ID (home or away) (optional)
    - status_filter: Filter by match status (optional)
    - skip: Number of matches to skip (default 0)
    - limit: Number of matches to return (default 10, max 100)
    
    Returns:
    - Paginated list of matches
    """
    query = select(Match)
    
    if league_id:
        query = query.where(Match.league_id == league_id)
    
    if team_id:
        query = query.where(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
    
    if status_filter:
        query = query.where(Match.status == status_filter)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Match.id)).select_from(Match).where(query.whereclause)
    )
    total = count_result.scalar()
    
    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Match.match_date.desc())
    )
    matches = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages,
        items=[MatchResponse.model_validate(match) for match in matches],
    )


@router.get("/{match_id}", response_model=MatchDetailResponse)
async def get_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
) -> MatchDetailResponse:
    """
    Retrieve a specific match with detailed information.
    
    Parameters:
    - match_id: ID of the match to retrieve
    
    Returns:
    - Detailed match information with teams and prediction count
    
    Raises:
    - 404: Match not found
    """
    result = await db.execute(
        select(Match)
        .where(Match.id == match_id)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
        )
    )
    match = result.scalars().first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with id {match_id} not found",
        )
    
    # Count predictions
    from app.models import Prediction
    pred_result = await db.execute(
        select(func.count(Prediction.id)).where(Prediction.match_id == match_id)
    )
    predictions_count = pred_result.scalar()
    
    response = MatchDetailResponse.model_validate(match)
    if match.home_team:
        response.home_team = {
            "id": match.home_team.id,
            "name": match.home_team.name,
        }
    if match.away_team:
        response.away_team = {
            "id": match.away_team.id,
            "name": match.away_team.name,
        }
    response.predictions_count = predictions_count
    
    return response


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(
    match_data: MatchCreate,
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    """
    Create a new match.
    
    Request Body:
    - league_id: League ID (required)
    - home_team_id: Home team ID (required)
    - away_team_id: Away team ID (required)
    - match_date: Match date and time (required)
    - match_week: Match week number (optional)
    - venue: Venue name (optional)
    - referee: Referee name (optional)
    
    Returns:
    - The created match
    
    Raises:
    - 400: Invalid league or team IDs
    - 400: Home and away teams are the same
    """
    # Verify league exists
    league_result = await db.execute(
        select(League).where(League.id == match_data.league_id)
    )
    if not league_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with id {match_data.league_id} not found",
        )
    
    # Verify teams exist
    home_team_result = await db.execute(
        select(Team).where(Team.id == match_data.home_team_id)
    )
    if not home_team_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Home team with id {match_data.home_team_id} not found",
        )
    
    away_team_result = await db.execute(
        select(Team).where(Team.id == match_data.away_team_id)
    )
    if not away_team_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Away team with id {match_data.away_team_id} not found",
        )
    
    # Verify teams are different
    if match_data.home_team_id == match_data.away_team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Home and away teams cannot be the same",
        )
    
    # Create new match
    db_match = Match(**match_data.model_dump())
    db.add(db_match)
    await db.commit()
    await db.refresh(db_match)
    
    return MatchResponse.model_validate(db_match)


@router.put("/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: AsyncSession = Depends(get_db),
) -> MatchResponse:
    """
    Update a match (typically to record final result).
    
    Parameters:
    - match_id: ID of the match to update
    
    Request Body:
    - home_goals: Home team goals (optional)
    - away_goals: Away team goals (optional)
    - is_finished: Match finished flag (optional)
    - status: Match status (optional)
    - odds_home_win: Home win odds (optional)
    - odds_draw: Draw odds (optional)
    - odds_away_win: Away win odds (optional)
    
    Returns:
    - The updated match
    
    Raises:
    - 404: Match not found
    """
    result = await db.execute(
        select(Match).where(Match.id == match_id)
    )
    db_match = result.scalars().first()
    
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with id {match_id} not found",
        )
    
    # Update fields
    update_data = match_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_match, field, value)
    
    await db.commit()
    await db.refresh(db_match)
    
    return MatchResponse.model_validate(db_match)


@router.delete("/{match_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Delete a match.
    
    Parameters:
    - match_id: ID of the match to delete
    
    Returns:
    - Success message
    
    Raises:
    - 404: Match not found
    
    Note:
    - Deleting a match will cascade delete related predictions and user predictions
    """
    result = await db.execute(
        select(Match).where(Match.id == match_id)
    )
    db_match = result.scalars().first()
    
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with id {match_id} not found",
        )
    
    match_date = db_match.match_date
    await db.delete(db_match)
    await db.commit()
    
    return Message(message=f"Match on {match_date} deleted successfully")
