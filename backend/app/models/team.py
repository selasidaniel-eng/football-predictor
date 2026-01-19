"""Team model for storing football team information"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Team(Base):
    """Team model - represents a football team"""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=True)
    founded_year = Column(Integer, nullable=True)
    stadium = Column(String(255), nullable=True)
    home_advantage = Column(Float, default=0.0, nullable=False)  # Strength metric
    strength_rating = Column(Float, default=50.0, nullable=False)  # 0-100 scale
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    league = relationship("League", back_populates="teams")
    home_matches = relationship(
        "Match",
        back_populates="home_team",
        foreign_keys="Match.home_team_id",
        cascade="all, delete-orphan",
    )
    away_matches = relationship(
        "Match",
        back_populates="away_team",
        foreign_keys="Match.away_team_id",
        cascade="all, delete-orphan",
    )
    injuries = relationship("Injury", back_populates="team", cascade="all, delete-orphan")
    team_form = relationship(
        "TeamForm", back_populates="team", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Team {self.name}>"
