"""
API routes for League management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import League, Team, Match
from app.schemas import (
    LeagueCreate,
    LeagueUpdate,
    LeagueResponse,
    LeagueDetailResponse,
    PaginatedResponse,
    Message,
)
from .deps import get_db

router = APIRouter(prefix="/api/v1/leagues", tags=["leagues"])


@router.get("", response_model=PaginatedResponse[LeagueResponse])
async def list_leagues(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[LeagueResponse]:
    """
    Retrieve all leagues with pagination.
    
    Query Parameters:
    - skip: Number of leagues to skip (default 0)
    - limit: Number of leagues to return (default 10, max 100)
    
    Returns:
    - Paginated list of leagues
    """
    # Get total count
    count_result = await db.execute(select(func.count(League.id)))
    total = count_result.scalar()
    
    # Get paginated results
    result = await db.execute(
        select(League)
        .offset(skip)
        .limit(limit)
        .order_by(League.name)
    )
    leagues = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages,
        items=[LeagueResponse.model_validate(league) for league in leagues],
    )


@router.get("/{league_id}", response_model=LeagueDetailResponse)
async def get_league(
    league_id: int,
    db: AsyncSession = Depends(get_db),
) -> LeagueDetailResponse:
    """
    Retrieve a specific league with team and match counts.
    
    Parameters:
    - league_id: ID of the league to retrieve
    
    Returns:
    - Detailed league information with related statistics
    
    Raises:
    - 404: League not found
    """
    result = await db.execute(
        select(League).where(League.id == league_id)
    )
    league = result.scalars().first()
    
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found",
        )
    
    # Count related records
    teams_result = await db.execute(
        select(func.count(Team.id)).where(Team.league_id == league_id)
    )
    teams_count = teams_result.scalar()
    
    matches_result = await db.execute(
        select(func.count(Match.id)).where(Match.league_id == league_id)
    )
    matches_count = matches_result.scalar()
    
    response = LeagueDetailResponse.model_validate(league)
    response.teams_count = teams_count
    response.matches_count = matches_count
    
    return response


@router.post("", response_model=LeagueResponse, status_code=status.HTTP_201_CREATED)
async def create_league(
    league_data: LeagueCreate,
    db: AsyncSession = Depends(get_db),
) -> LeagueResponse:
    """
    Create a new league.
    
    Request Body:
    - name: League name (required, unique)
    - country: Country name (required)
    - season: Season year (required)
    - description: League description (optional)
    
    Returns:
    - The created league
    
    Raises:
    - 400: League name already exists
    """
    # Check if league with same name already exists
    existing = await db.execute(
        select(League).where(League.name == league_data.name)
    )
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with name '{league_data.name}' already exists",
        )
    
    # Create new league
    db_league = League(**league_data.model_dump())
    db.add(db_league)
    await db.commit()
    await db.refresh(db_league)
    
    return LeagueResponse.model_validate(db_league)


@router.put("/{league_id}", response_model=LeagueResponse)
async def update_league(
    league_id: int,
    league_data: LeagueUpdate,
    db: AsyncSession = Depends(get_db),
) -> LeagueResponse:
    """
    Update a league.
    
    Parameters:
    - league_id: ID of the league to update
    
    Request Body:
    - name: New league name (optional)
    - country: New country (optional)
    - season: New season (optional)
    - description: New description (optional)
    
    Returns:
    - The updated league
    
    Raises:
    - 404: League not found
    - 400: New league name already exists
    """
    result = await db.execute(
        select(League).where(League.id == league_id)
    )
    db_league = result.scalars().first()
    
    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found",
        )
    
    # Check if new name already exists (if provided)
    update_data = league_data.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != db_league.name:
        existing = await db.execute(
            select(League).where(League.name == update_data["name"])
        )
        if existing.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"League with name '{update_data['name']}' already exists",
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_league, field, value)
    
    await db.commit()
    await db.refresh(db_league)
    
    return LeagueResponse.model_validate(db_league)


@router.delete("/{league_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_league(
    league_id: int,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Delete a league and all its related data.
    
    Parameters:
    - league_id: ID of the league to delete
    
    Returns:
    - Success message
    
    Raises:
    - 404: League not found
    
    Note:
    - Deleting a league will cascade delete all teams and matches
    """
    result = await db.execute(
        select(League).where(League.id == league_id)
    )
    db_league = result.scalars().first()
    
    if not db_league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League with id {league_id} not found",
        )
    
    league_name = db_league.name
    await db.delete(db_league)
    await db.commit()
    
    return Message(message=f"League '{league_name}' deleted successfully")
