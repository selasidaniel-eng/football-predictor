"""
API Schemas - Request validation and response serialization models.
"""

# Base schemas
from .base import (
    BaseResponse,
    BaseResponseWithTimestamp,
    TimestampedBase,
    PaginatedResponse,
    ErrorResponse,
    SuccessResponse,
    Message,
)

# League and Team schemas
from .league import (
    LeagueCreate,
    LeagueUpdate,
    LeagueResponse,
    LeagueDetailResponse,
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamDetailResponse,
)

# Core models schemas
from .models import (
    MatchCreate,
    MatchUpdate,
    MatchResponse,
    MatchDetailResponse,
    UserRegister,
    UserUpdate,
    UserChangePassword,
    UserResponse,
    UserDetailResponse,
    UserProfileResponse,
    InjuryCreate,
    InjuryUpdate,
    InjuryResponse,
)

# Prediction schemas
from .predictions import (
    PredictionCreate,
    PredictionUpdate,
    PredictionResponse,
    UserPredictionCreate,
    UserPredictionUpdate,
    UserPredictionResponse,
    PredictionStatsResponse,
    UserBettingStatsResponse,
)

__all__ = [
    # Base
    "BaseResponse",
    "BaseResponseWithTimestamp",
    "TimestampedBase",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "Message",
    # League & Team
    "LeagueCreate",
    "LeagueUpdate",
    "LeagueResponse",
    "LeagueDetailResponse",
    "TeamCreate",
    "TeamUpdate",
    "TeamResponse",
    "TeamDetailResponse",
    # Core Models
    "MatchCreate",
    "MatchUpdate",
    "MatchResponse",
    "MatchDetailResponse",
    "UserRegister",
    "UserUpdate",
    "UserChangePassword",
    "UserResponse",
    "UserDetailResponse",
    "UserProfileResponse",
    "InjuryCreate",
    "InjuryUpdate",
    "InjuryResponse",
    # Predictions
    "PredictionCreate",
    "PredictionUpdate",
    "PredictionResponse",
    "UserPredictionCreate",
    "UserPredictionUpdate",
    "UserPredictionResponse",
    "PredictionStatsResponse",
    "UserBettingStatsResponse",
]
