"""
API routes for User management and authentication.
"""

from datetime import timedelta
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserProfile
from app.schemas import (
    UserRegister,
    UserResponse,
    UserDetailResponse,
    UserChangePassword,
    UserUpdate,
    Message,
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)
from app.core.config import get_settings
from .deps import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
settings = get_settings()


# Token response schema
class TokenResponse(BaseModel):
    """Response containing access token and user info."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class LoginRequest(BaseModel):
    """Login request with username and password."""
    username: str
    password: str


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.
    
    Request Body:
    - username: Username (required, 3-50 chars)
    - email: Email address (required, unique)
    - password: Password (required, min 8 chars)
    - first_name: First name (optional)
    - last_name: Last name (optional)
    
    Returns:
    - The created user
    
    Raises:
    - 400: Username or email already exists
    """
    # Check if username already exists
    username_result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if username_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    email_result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if email_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_active=True,
        is_verified=False,  # Email verification would happen here
    )
    db.add(db_user)
    await db.flush()  # Get the user ID without committing
    
    # Create user profile
    user_profile = UserProfile(user_id=db_user.id)
    db.add(user_profile)
    await db.commit()
    await db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login user and get access token.
    
    Request Body:
    - username: Username (required)
    - password: Password (required)
    
    Returns:
    - Access token and user information
    
    Raises:
    - 401: Invalid username or password
    """
    # Find user by username
    result = await db.execute(
        select(User).where(User.username == login_data.username)
    )
    user = result.scalars().first()
    
    # Verify user and password
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserDetailResponse)
async def get_current_user(
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> UserDetailResponse:
    """
    Get current authenticated user's profile.
    
    Headers:
    - Authorization: Bearer <token> (required)
    
    Returns:
    - Current user's detailed profile
    
    Raises:
    - 401: Invalid or missing token
    """
    # Extract token from header (in production, use FastAPI's HTTPBearer)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode token
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload["sub"])
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return UserDetailResponse.model_validate(user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update current user's profile.
    
    Headers:
    - Authorization: Bearer <token> (required)
    
    Request Body:
    - first_name: First name (optional)
    - last_name: Last name (optional)
    - bio: Biography (optional)
    
    Returns:
    - Updated user profile
    
    Raises:
    - 401: Invalid or missing token
    """
    # Verify token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = int(payload["sub"])
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    db_user = result.scalars().first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    
    return UserResponse.model_validate(db_user)


@router.post("/change-password", response_model=Message)
async def change_password(
    password_data: UserChangePassword,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Change user's password.
    
    Headers:
    - Authorization: Bearer <token> (required)
    
    Request Body:
    - old_password: Current password (required)
    - new_password: New password (required, min 8 chars)
    - confirm_password: Confirm new password (required)
    
    Returns:
    - Success message
    
    Raises:
    - 401: Invalid token
    - 400: Old password incorrect or passwords don't match
    """
    # Verify token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = int(payload["sub"])
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    db_user = result.scalars().first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    
    # Verify passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match",
        )
    
    # Update password
    db_user.password_hash = hash_password(password_data.new_password)
    await db.commit()
    
    return Message(message="Password changed successfully")


# User management endpoints (admin only - TODO: add admin checks)
@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
) -> UserDetailResponse:
    """
    Get a user's public profile.
    
    Parameters:
    - user_id: ID of the user to retrieve
    
    Returns:
    - User's detailed profile (limited public info)
    
    Raises:
    - 404: User not found
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    
    return UserDetailResponse.model_validate(user)


@router.delete("/{user_id}", response_model=Message, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Delete a user account.
    
    Parameters:
    - user_id: ID of the user to delete
    
    Headers:
    - Authorization: Bearer <token> (required, must be own account)
    
    Returns:
    - Success message
    
    Raises:
    - 401: Invalid token or not authorized
    - 404: User not found
    """
    # Verify token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    current_user_id = int(payload["sub"])
    
    # Check authorization (can only delete own account)
    if current_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own account",
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    db_user = result.scalars().first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    
    username = db_user.username
    await db.delete(db_user)
    await db.commit()
    
    return Message(message=f"User '{username}' deleted successfully")
