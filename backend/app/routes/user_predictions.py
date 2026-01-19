"""
API routes for UserPrediction management (user bets and predictions).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import UserPrediction, User, Match
from app.schemas import (
    UserPredictionCreate,
    UserPredictionUpdate,
    UserPredictionResponse,
    PaginatedResponse,
    Message,
)
from .deps import get_db

router = APIRouter(prefix="/api/v1/user-predictions", tags=["user-predictions"])


@router.get("", response_model=PaginatedResponse[UserPredictionResponse])
async def list_user_predictions(
    db: AsyncSession = Depends(get_db),
    user_id: int = Query(None, description="Filter by user ID"),
    status_filter: str = Query(None, description="Filter by status (pending/won/lost)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
) -> PaginatedResponse[UserPredictionResponse]:
    """
    Retrieve user predictions with optional filtering.
    
    Query Parameters:
    - user_id: Filter by user (optional)
    - status_filter: Filter by status (optional)
    - skip: Number of predictions to skip (default 0)
    - limit: Number to return (default 10, max 100)
    
    Returns:
    - Paginated list of user predictions
    """
    query = select(UserPrediction)
    
    if user_id:
        query = query.where(UserPrediction.user_id == user_id)
    
    if status_filter:
        query = query.where(UserPrediction.status == status_filter)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(UserPrediction.id)).select_from(UserPrediction)
    )
    total = count_result.scalar()
    
    # Get paginated results
    result = await db.execute(
        query.offset(skip).limit(limit).order_by(UserPrediction.created_at.desc())
    )
    predictions = result.scalars().all()
    
    total_pages = (total + limit - 1) // limit
    
    return PaginatedResponse(
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages,
        items=[UserPredictionResponse.model_validate(p) for p in predictions],
    )


@router.get("/{prediction_id}", response_model=UserPredictionResponse)
async def get_user_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserPredictionResponse:
    """
    Retrieve a specific user prediction.
    
    Parameters:
    - prediction_id: ID of the user prediction
    
    Returns:
    - User prediction details
    
    Raises:
    - 404: Prediction not found
    """
    result = await db.execute(
        select(UserPrediction).where(UserPrediction.id == prediction_id)
    )
    prediction = result.scalars().first()
    
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User prediction with id {prediction_id} not found",
        )
    
    return UserPredictionResponse.model_validate(prediction)


@router.post("", response_model=UserPredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_user_prediction(
    prediction_data: UserPredictionCreate,
    db: AsyncSession = Depends(get_db),
) -> UserPredictionResponse:
    """
    Create a new user prediction (place a bet).
    
    Request Body:
    - user_id: User ID (required)
    - match_id: Match ID (required)
    - prediction: Prediction type (required) - home_win/draw/away_win/over_2_5/under_2_5
    - confidence_level: Confidence 1-100 (required)
    - odds_selected: Odds selected (optional)
    - stake_amount: Stake amount (required, must be > 0)
    - reasoning: Explanation of prediction (optional)
    
    Returns:
    - Created user prediction
    
    Raises:
    - 400: Invalid match, user not found, or invalid data
    """
    # Verify user exists
    user_result = await db.execute(
        select(User).where(User.id == prediction_data.user_id)
    )
    if not user_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with id {prediction_data.user_id} not found",
        )
    
    # Verify match exists
    match_result = await db.execute(
        select(Match).where(Match.id == prediction_data.match_id)
    )
    if not match_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Match with id {prediction_data.match_id} not found",
        )
    
    # Calculate potential winnings
    potential_winnings = None
    if prediction_data.odds_selected:
        potential_winnings = prediction_data.stake_amount * prediction_data.odds_selected
    
    # Create new user prediction
    db_prediction = UserPrediction(
        **prediction_data.model_dump(),
        potential_winnings=potential_winnings,
        status="pending",
    )
    db.add(db_prediction)
    await db.commit()
    await db.refresh(db_prediction)
    
    return UserPredictionResponse.model_validate(db_prediction)


@router.put("/{prediction_id}", response_model=UserPredictionResponse)
async def update_user_prediction(
    prediction_id: int,
    prediction_data: UserPredictionUpdate,
    db: AsyncSession = Depends(get_db),
) -> UserPredictionResponse:
    """
    Update a user prediction (before match finishes).
    
    Parameters:
    - prediction_id: ID of the prediction
    
    Request Body:
    - prediction: Updated prediction type (optional)
    - confidence_level: Updated confidence (optional)
    - odds_selected: Updated odds (optional)
    - stake_amount: Updated stake (optional)
    - reasoning: Updated reasoning (optional)
    
    Returns:
    - Updated user prediction
    
    Raises:
    - 404: Prediction not found
    """
    result = await db.execute(
        select(UserPrediction).where(UserPrediction.id == prediction_id)
    )
    db_prediction = result.scalars().first()
    
    if not db_prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User prediction with id {prediction_id} not found",
        )
    
    # Prevent updating settled predictions
    if db_prediction.status in ["won", "lost", "voided"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a settled prediction",
        )
    
    # Update fields
    update_data = prediction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prediction, field, value)
    
    # Recalculate potential winnings if odds or stake updated
    if "stake_amount" in update_data or "odds_selected" in update_data:
        stake = update_data.get("stake_amount", db_prediction.stake_amount)
        odds = update_data.get("odds_selected", db_prediction.odds_selected)
        if odds:
            db_prediction.potential_winnings = stake * odds
    
    await db.commit()
    await db.refresh(db_prediction)
    
    return UserPredictionResponse.model_validate(db_prediction)


@router.post("/{prediction_id}/settle", response_model=UserPredictionResponse)
async def settle_prediction(
    prediction_id: int,
    result_data: dict,  # {'result': 'won'|'lost'|'voided', 'is_correct': true|false}
    db: AsyncSession = Depends(get_db),
) -> UserPredictionResponse:
    """
    Settle a prediction after match finishes.
    
    Parameters:
    - prediction_id: ID of the prediction
    
    Request Body:
    - result: Result of prediction (won/lost/voided)
    - is_correct: Whether prediction was correct
    
    Returns:
    - Settled prediction
    
    Raises:
    - 404: Prediction not found
    - 400: Already settled
    """
    result = await db.execute(
        select(UserPrediction).where(UserPrediction.id == prediction_id)
    )
    db_prediction = result.scalars().first()
    
    if not db_prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User prediction with id {prediction_id} not found",
        )
    
    if db_prediction.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prediction is already settled",
        )
    
    # Update prediction
    db_prediction.status = result_data.get("result", "voided")
    db_prediction.is_correct = result_data.get("is_correct")
    db_prediction.result = result_data.get("result")
    
    # Set settled timestamp
    from datetime import datetime
    db_prediction.settled_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_prediction)
    
    return UserPredictionResponse.model_validate(db_prediction)


@router.delete("/{prediction_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_user_prediction(
    prediction_id: int,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Delete a user prediction (before settlement).
    
    Parameters:
    - prediction_id: ID of the prediction to delete
    
    Returns:
    - Success message
    
    Raises:
    - 404: Prediction not found
    - 400: Cannot delete settled prediction
    """
    result = await db.execute(
        select(UserPrediction).where(UserPrediction.id == prediction_id)
    )
    db_prediction = result.scalars().first()
    
    if not db_prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User prediction with id {prediction_id} not found",
        )
    
    if db_prediction.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a settled prediction",
        )
    
    await db.delete(db_prediction)
    await db.commit()
    
    return Message(message="User prediction deleted successfully")
