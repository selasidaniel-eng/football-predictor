"""
Schemas for League model - request validation and response serialization.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseResponse, BaseResponseWithTimestamp


class LeagueCreate(BaseModel):
    """Schema for creating a new league."""
    name: str = Field(..., min_length=1, max_length=255, description="League name")
    country: str = Field(..., min_length=1, max_length=100, description="Country")
    season: int = Field(..., ge=1900, le=2100, description="Season year")
    description: Optional[str] = Field(None, max_length=1000, description="League description")


class LeagueUpdate(BaseModel):
    """Schema for updating a league."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    season: Optional[int] = Field(None, ge=1900, le=2100)
    description: Optional[str] = Field(None, max_length=1000)


class LeagueResponse(BaseResponseWithTimestamp):
    """Schema for league response."""
    name: str
    country: str
    season: int
    description: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class LeagueDetailResponse(LeagueResponse):
    """Extended league response with relationships."""
    teams_count: int = 0
    matches_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


# Schemas for Team model
class TeamCreate(BaseModel):
    """Schema for creating a new team."""
    name: str = Field(..., min_length=1, max_length=255, description="Team name")
    league_id: int = Field(..., gt=0, description="League ID")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    city: Optional[str] = Field(None, max_length=100, description="City")
    founded_year: Optional[int] = Field(None, ge=1800, le=2100, description="Year founded")
    stadium: Optional[str] = Field(None, max_length=255, description="Stadium name")
    home_advantage: Optional[float] = Field(None, ge=0.0, le=2.0, description="Home advantage multiplier")
    strength_rating: Optional[int] = Field(None, ge=0, le=100, description="Strength rating 0-100")


class TeamUpdate(BaseModel):
    """Schema for updating a team."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    league_id: Optional[int] = Field(None, gt=0)
    country: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1800, le=2100)
    stadium: Optional[str] = Field(None, max_length=255)
    home_advantage: Optional[float] = Field(None, ge=0.0, le=2.0)
    strength_rating: Optional[int] = Field(None, ge=0, le=100)


class TeamResponse(BaseResponseWithTimestamp):
    """Schema for team response."""
    name: str
    league_id: int
    country: Optional[str] = None
    city: Optional[str] = None
    founded_year: Optional[int] = None
    stadium: Optional[str] = None
    home_advantage: float = 1.0
    strength_rating: int = 50
    
    model_config = ConfigDict(from_attributes=True)


class TeamDetailResponse(TeamResponse):
    """Extended team response with relationships."""
    league: Optional[LeagueResponse] = None
    home_matches_count: int = 0
    away_matches_count: int = 0
    injuries_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)
