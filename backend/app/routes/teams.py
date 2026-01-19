"""
API routes for Team management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Team, League, Match, Injury
from app.schemas import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamDetailResponse,
    LeagueResponse,
    PaginatedResponse,
    Message,
)
from .deps import get_db

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("", response_model=PaginatedResponse[TeamResponse])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    league_id: int = Query(None, description="Filter by league ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[TeamResponse]:
    """
    Retrieve all teams with optional filtering by league.
    
    Query Parameters:
    - league_id: Filter teams by league (optional)
    - skip: Number of teams to skip (default 0)
    - limit: Number of teams to return (default 10, max 100)
    
    Returns:
    - Paginated list of teams
    """
    query = select(Team)
    
    if league_id:
        query = query.where(Team.league_id == league_id)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Team.id)).select_from(Team)
        if not league_id
        else select(func.count(Team.id)).where(Team.league_id == league_id)
    )
    total = count_result.scalar()
    
    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Team.name)
    )
    teams = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages,
        items=[TeamResponse.model_validate(team) for team in teams],
    )


@router.get("/{team_id}", response_model=TeamDetailResponse)
async def get_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
) -> TeamDetailResponse:
    """
    Retrieve a specific team with detailed information.
    
    Parameters:
    - team_id: ID of the team to retrieve
    
    Returns:
    - Detailed team information with league and match counts
    
    Raises:
    - 404: Team not found
    """
    result = await db.execute(
        select(Team)
        .where(Team.id == team_id)
        .options(selectinload(Team.league))
    )
    team = result.scalars().first()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found",
        )
    
    # Count related records
    home_matches_result = await db.execute(
        select(func.count(Match.id)).where(Match.home_team_id == team_id)
    )
    home_matches = home_matches_result.scalar()
    
    away_matches_result = await db.execute(
        select(func.count(Match.id)).where(Match.away_team_id == team_id)
    )
    away_matches = away_matches_result.scalar()
    
    injuries_result = await db.execute(
        select(func.count(Injury.id)).where(Injury.team_id == team_id)
    )
    injuries = injuries_result.scalar()
    
    response = TeamDetailResponse.model_validate(team)
    response.league = LeagueResponse.model_validate(team.league) if team.league else None
    response.home_matches_count = home_matches
    response.away_matches_count = away_matches
    response.injuries_count = injuries
    
    return response


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    team_data: TeamCreate,
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """
    Create a new team.
    
    Request Body:
    - name: Team name (required)
    - league_id: League ID (required)
    - country: Country (optional)
    - city: City (optional)
    - founded_year: Year founded (optional)
    - stadium: Stadium name (optional)
    - home_advantage: Home advantage multiplier (optional, default 1.0)
    - strength_rating: Strength rating 0-100 (optional, default 50)
    
    Returns:
    - The created team
    
    Raises:
    - 400: League not found
    """
    # Verify league exists
    league_result = await db.execute(
        select(League).where(League.id == team_data.league_id)
    )
    if not league_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"League with id {team_data.league_id} not found",
        )
    
    # Create new team
    db_team = Team(**team_data.model_dump())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    
    return TeamResponse.model_validate(db_team)


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: AsyncSession = Depends(get_db),
) -> TeamResponse:
    """
    Update a team.
    
    Parameters:
    - team_id: ID of the team to update
    
    Request Body:
    - name: New team name (optional)
    - league_id: New league ID (optional)
    - country: New country (optional)
    - city: New city (optional)
    - founded_year: New founded year (optional)
    - stadium: New stadium (optional)
    - home_advantage: New home advantage (optional)
    - strength_rating: New strength rating (optional)
    
    Returns:
    - The updated team
    
    Raises:
    - 404: Team not found
    - 400: Invalid league_id
    """
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    db_team = result.scalars().first()
    
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found",
        )
    
    # Verify new league if provided
    update_data = team_data.model_dump(exclude_unset=True)
    if "league_id" in update_data:
        league_result = await db.execute(
            select(League).where(League.id == update_data["league_id"])
        )
        if not league_result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"League with id {update_data['league_id']} not found",
            )
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_team, field, value)
    
    await db.commit()
    await db.refresh(db_team)
    
    return TeamResponse.model_validate(db_team)


@router.delete("/{team_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Delete a team.
    
    Parameters:
    - team_id: ID of the team to delete
    
    Returns:
    - Success message
    
    Raises:
    - 404: Team not found
    
    Note:
    - Deleting a team will cascade delete related matches and injuries
    """
    result = await db.execute(
        select(Team).where(Team.id == team_id)
    )
    db_team = result.scalars().first()
    
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Team with id {team_id} not found",
        )
    
    team_name = db_team.name
    await db.delete(db_team)
    await db.commit()
    
    return Message(message=f"Team '{team_name}' deleted successfully")
