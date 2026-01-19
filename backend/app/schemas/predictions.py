"""
Schemas for Prediction and UserPrediction models.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse, BaseResponseWithTimestamp


# Prediction Schemas (ML Model Predictions)
class PredictionCreate(BaseModel):
    """Schema for creating a prediction."""
    match_id: int = Field(..., gt=0, description="Match ID")
    probability_home_win: float = Field(..., ge=0.0, le=1.0, description="Probability home wins")
    probability_draw: float = Field(..., ge=0.0, le=1.0, description="Probability of draw")
    probability_away_win: float = Field(..., ge=0.0, le=1.0, description="Probability away wins")
    expected_goals_home: Optional[float] = Field(None, ge=0.0, description="Expected goals home")
    expected_goals_away: Optional[float] = Field(None, ge=0.0, description="Expected goals away")
    model_confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence 0-1")
    model_version: Optional[str] = Field(None, max_length=50, description="Model version")


class PredictionUpdate(BaseModel):
    """Schema for updating a prediction."""
    probability_home_win: Optional[float] = Field(None, ge=0.0, le=1.0)
    probability_draw: Optional[float] = Field(None, ge=0.0, le=1.0)
    probability_away_win: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_goals_home: Optional[float] = Field(None, ge=0.0)
    expected_goals_away: Optional[float] = Field(None, ge=0.0)
    model_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class PredictionResponse(BaseResponseWithTimestamp):
    """Schema for prediction response."""
    match_id: int
    probability_home_win: float
    probability_draw: float
    probability_away_win: float
    expected_goals_home: Optional[float] = None
    expected_goals_away: Optional[float] = None
    model_confidence: float
    model_version: Optional[str] = None
    prediction_outcome: Optional[str] = None
    was_correct: Optional[bool] = None
    
    model_config = ConfigDict(from_attributes=True)


# UserPrediction Schemas (User Bets)
class UserPredictionCreate(BaseModel):
    """Schema for creating a user prediction/bet."""
    match_id: int = Field(..., gt=0, description="Match ID")
    prediction: str = Field(..., description="Prediction type (home_win/draw/away_win/over_2_5/under_2_5)")
    confidence_level: int = Field(..., ge=1, le=100, description="Confidence 1-100")
    odds_selected: Optional[Decimal] = Field(None, gt=0, description="Odds selected")
    stake_amount: Decimal = Field(..., gt=0, description="Stake amount")
    reasoning: Optional[str] = Field(None, max_length=1000, description="Reasoning for prediction")


class UserPredictionUpdate(BaseModel):
    """Schema for updating a user prediction."""
    prediction: Optional[str] = Field(None, description="Prediction type")
    confidence_level: Optional[int] = Field(None, ge=1, le=100)
    odds_selected: Optional[Decimal] = Field(None, gt=0)
    stake_amount: Optional[Decimal] = Field(None, gt=0)
    reasoning: Optional[str] = Field(None, max_length=1000)


class UserPredictionResponse(BaseResponseWithTimestamp):
    """Schema for user prediction response."""
    user_id: int
    match_id: int
    prediction: str
    confidence_level: int
    odds_selected: Optional[Decimal] = None
    stake_amount: Decimal
    potential_winnings: Optional[Decimal] = None
    status: str = "pending"
    result: Optional[str] = None
    is_correct: Optional[bool] = None
    reasoning: Optional[str] = None
    settled_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Additional Response Schemas
class PredictionStatsResponse(BaseResponse):
    """Schema for prediction statistics."""
    total_predictions: int
    correct_predictions: int
    accuracy: float
    average_confidence: float
    high_confidence_accuracy: float
    
    model_config = ConfigDict(from_attributes=True)


class UserBettingStatsResponse(BaseResponse):
    """Schema for user betting statistics."""
    user_id: int
    total_bets: int
    winning_bets: int
    losing_bets: int
    win_rate: float
    total_stake: Decimal
    total_winnings: Decimal
    net_profit: Decimal
    roi: float
    
    model_config = ConfigDict(from_attributes=True)
