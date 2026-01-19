"""League model for storing football league information"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class League(Base):
    """League model - represents a football league"""

    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    country = Column(String(100), nullable=False)
    season = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    teams = relationship("Team", back_populates="league", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="league", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<League {self.name} ({self.country})>"
