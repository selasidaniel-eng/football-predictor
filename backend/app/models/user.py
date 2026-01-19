"""User model for storing user account information"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """User model - represents a user account"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    is_active = Column(Integer, default=1, nullable=False)  # 1 = active, 0 = inactive
    is_verified = Column(Integer, default=0, nullable=False)  # Email verified
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    user_predictions = relationship(
        "UserPrediction", back_populates="user", cascade="all, delete-orphan"
    )
    user_profile = relationship(
        "UserProfile", back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
