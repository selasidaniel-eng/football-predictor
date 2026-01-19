"""
Base schemas for common response patterns and utilities.
"""

from datetime import datetime
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class TimestampedBase(BaseModel):
    """Base schema with timestamp fields."""
    created_at: datetime
    updated_at: datetime


class BaseResponse(BaseModel):
    """Base response schema with ID."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class BaseResponseWithTimestamp(BaseResponse, TimestampedBase):
    """Base response schema with ID and timestamps."""
    pass


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[T]


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
    status_code: int = 400


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response wrapper."""
    success: bool = True
    message: str
    data: Optional[T] = None


class Message(BaseModel):
    """Simple message response."""
    message: str
