"""
API routes for Prediction management (ML predictions).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Prediction, Match, User
from app.schemas import (
    PredictionCreate,
    PredictionUpdate,
    PredictionResponse,
    PaginatedResponse,
    Message,
)
from .deps import get_db

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


@router.get("", response_model=PaginatedResponse[PredictionResponse])
async def list_predictions(
    db: AsyncSession = Depends(get_db),
    match_id: int = Query(None, description="Filter by match ID"),
    model_version: str = Query(None, description="Filter by model version"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[PredictionResponse]:
    """
    Retrieve all ML model predictions with optional filtering.
    
    Query Parameters:
    - match_id: Filter by match (optional)
    - model_version: Filter by model version (optional)
    - skip: Number of predictions to skip (default 0)
    - limit: Number to return (default 10, max 100)
    
    Returns:
    - Paginated list of predictions
    """
    query = select(Prediction)
    
    if match_id:
        query = query.where(Prediction.match_id == match_id)
    
    if model_version:
        query = query.where(Prediction.model_version == model_version)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Prediction.id)).select_from(Prediction)
    )
    total = count_result.scalar()
    
    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(Prediction.created_at.desc())
    )
    predictions = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages,
        items=[PredictionResponse.model_validate(p) for p in predictions],
    )


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """
    Retrieve a specific prediction.
    
    Parameters:
    - prediction_id: ID of the prediction
    
    Returns:
    - Prediction details
    
    Raises:
    - 404: Prediction not found
    """
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with id {prediction_id} not found",
        )
    
    return PredictionResponse.model_validate(prediction)


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_data: PredictionCreate,
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """
    Create a new ML prediction.
    
    Request Body:
    - match_id: Match ID (required)
    - probability_home_win: Home win probability 0-1 (required)
    - probability_draw: Draw probability 0-1 (required)
    - probability_away_win: Away win probability 0-1 (required)
    - expected_goals_home: Expected home goals (optional)
    - expected_goals_away: Expected away goals (optional)
    - model_confidence: Model confidence 0-1 (required)
    - model_version: Model version (optional)
    
    Returns:
    - Created prediction
    
    Raises:
    - 400: Match not found or invalid probabilities
    """
    # Verify match exists
    match_result = await db.execute(
        select(Match).where(Match.id == prediction_data.match_id)
    )
    if not match_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match with id {prediction_data.match_id} not found",
        )
    
    # Validate probabilities sum to 1.0 (approximately)
    total_prob = (
        prediction_data.probability_home_win
        + prediction_data.probability_draw
        + prediction_data.probability_away_win
    )
    if abs(total_prob - 1.0) > 0.01:  # Allow small floating point errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Probabilities must sum to 1.0",
        )
    
    # Create new prediction
    db_prediction = Prediction(**prediction_data.model_dump())
    db.add(db_prediction)
    await db.commit()
    await db.refresh(db_prediction)
    
    return PredictionResponse.model_validate(db_prediction)


@router.put("/{prediction_id}", response_model=PredictionResponse)
async def update_prediction(
    prediction_id: int,
    prediction_data: PredictionUpdate,
    db: AsyncSession = Depends(get_db),
) -> PredictionResponse:
    """
    Update an ML prediction (before match finishes).
    
    Parameters:
    - prediction_id: ID of the prediction
    
    Request Body:
    - probability_home_win: Updated home win probability (optional)
    - probability_draw: Updated draw probability (optional)
    - probability_away_win: Updated away win probability (optional)
    - expected_goals_home: Updated expected goals (optional)
    - expected_goals_away: Updated expected goals (optional)
    - model_confidence: Updated confidence (optional)
    
    Returns:
    - Updated prediction
    
    Raises:
    - 404: Prediction not found
    - 400: Invalid probabilities
    """
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    db_prediction = result.scalars().first()
    
    if not db_prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with id {prediction_id} not found",
        )
    
    # Update fields
    update_data = prediction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prediction, field, value)
    
    await db.commit()
    await db.refresh(db_prediction)
    
    return PredictionResponse.model_validate(db_prediction)


@router.delete("/{prediction_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Delete a prediction.
    
    Parameters:
    - prediction_id: ID of the prediction to delete
    
    Returns:
    - Success message
    
    Raises:
    - 404: Prediction not found
    """
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    db_prediction = result.scalars().first()
    
    if not db_prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction with id {prediction_id} not found",
        )
    
    await db.delete(db_prediction)
    await db.commit()
    
    return Message(message="Prediction deleted successfully")
