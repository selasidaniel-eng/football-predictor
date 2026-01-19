"""
Schemas for Match, User, and Injury models.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from .base import BaseResponse, BaseResponseWithTimestamp


# Match Schemas
class MatchCreate(BaseModel):
    """Schema for creating a new match."""
    league_id: int = Field(..., gt=0, description="League ID")
    home_team_id: int = Field(..., gt=0, description="Home team ID")
    away_team_id: int = Field(..., gt=0, description="Away team ID")
    match_date: datetime = Field(..., description="Match date and time")
    match_week: Optional[int] = Field(None, ge=1, le=38, description="Match week")
    venue: Optional[str] = Field(None, max_length=255, description="Venue")
    referee: Optional[str] = Field(None, max_length=255, description="Referee name")


class MatchUpdate(BaseModel):
    """Schema for updating a match."""
    home_goals: Optional[int] = Field(None, ge=0, description="Home team goals")
    away_goals: Optional[int] = Field(None, ge=0, description="Away team goals")
    is_finished: Optional[bool] = Field(None, description="Match finished")
    status: Optional[str] = Field(None, description="Match status")
    odds_home_win: Optional[Decimal] = Field(None, gt=0, description="Home win odds")
    odds_draw: Optional[Decimal] = Field(None, gt=0, description="Draw odds")
    odds_away_win: Optional[Decimal] = Field(None, gt=0, description="Away win odds")


class MatchResponse(BaseResponseWithTimestamp):
    """Schema for match response."""
    league_id: int
    home_team_id: int
    away_team_id: int
    match_date: datetime
    match_week: Optional[int] = None
    home_goals: Optional[int] = None
    away_goals: Optional[int] = None
    is_finished: bool = False
    odds_home_win: Optional[Decimal] = None
    odds_draw: Optional[Decimal] = None
    odds_away_win: Optional[Decimal] = None
    status: str = "scheduled"
    venue: Optional[str] = None
    referee: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MatchDetailResponse(MatchResponse):
    """Extended match response with relationships."""
    home_team: Optional['TeamResponseSimple'] = None
    away_team: Optional['TeamResponseSimple'] = None
    predictions_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class TeamResponseSimple(BaseResponse):
    """Simplified team response for nested objects."""
    name: str
    
    model_config = ConfigDict(from_attributes=True)


# User Schemas
class UserRegister(BaseModel):
    """Schema for user registration."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 chars)")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)


class UserChangePassword(BaseModel):
    """Schema for changing password."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    confirm_password: str = Field(..., description="Confirm new password")


class UserResponse(BaseResponseWithTimestamp):
    """Schema for user response."""
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """Extended user response with statistics."""
    profile: Optional['UserProfileResponse'] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseResponseWithTimestamp):
    """Schema for user profile response."""
    user_id: int
    total_predictions: int = 0
    correct_predictions: int = 0
    win_rate: Optional[float] = None
    total_stake: Optional[Decimal] = None
    total_winnings: Optional[Decimal] = None
    net_profit: Optional[Decimal] = None
    roi: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


# Injury Schemas
class InjuryCreate(BaseModel):
    """Schema for creating an injury record."""
    team_id: int = Field(..., gt=0, description="Team ID")
    player_name: str = Field(..., min_length=1, max_length=255, description="Player name")
    position: Optional[str] = Field(None, max_length=50, description="Player position")
    severity: str = Field("moderate", description="Injury severity")
    injury_date: datetime = Field(..., description="Injury date")
    expected_return: Optional[datetime] = Field(None, description="Expected return date")
    description: Optional[str] = Field(None, max_length=1000)
    impact_score: Optional[int] = Field(None, ge=1, le=10, description="Impact score 1-10")


class InjuryUpdate(BaseModel):
    """Schema for updating an injury record."""
    severity: Optional[str] = Field(None, description="Injury severity")
    expected_return: Optional[datetime] = Field(None)
    status: Optional[str] = Field(None, description="Injury status")
    description: Optional[str] = Field(None, max_length=1000)
    impact_score: Optional[int] = Field(None, ge=1, le=10)


class InjuryResponse(BaseResponseWithTimestamp):
    """Schema for injury response."""
    team_id: int
    player_name: str
    position: Optional[str] = None
    severity: str
    injury_date: datetime
    expected_return: Optional[datetime] = None
    status: str = "injured"
    description: Optional[str] = None
    impact_score: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)
