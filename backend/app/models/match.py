"""Match model for storing football match information"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship

from ..database import Base


class Match(Base):
    """Match model - represents a football match"""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    home_team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False, index=True
    )
    away_team_id = Column(
        Integer, ForeignKey("teams.id"), nullable=False, index=True
    )
    match_date = Column(DateTime, nullable=False, index=True)
    match_week = Column(Integer, nullable=True)  # Matchday/week number
    
    # Match result
    home_goals = Column(Integer, nullable=True)
    away_goals = Column(Integer, nullable=True)
    is_finished = Column(Boolean, default=False, nullable=False)
    
    # Betting odds (display only)
    odds_home_win = Column(Float, nullable=True)
    odds_draw = Column(Float, nullable=True)
    odds_away_win = Column(Float, nullable=True)
    
    # Additional info
    status = Column(String(50), default="scheduled", nullable=False)  # scheduled, live, finished
    venue = Column(String(255), nullable=True)
    referee = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    league = relationship("League", back_populates="matches")
    home_team = relationship(
        "Team",
        back_populates="home_matches",
        foreign_keys=[home_team_id],
    )
    away_team = relationship(
        "Team",
        back_populates="away_matches",
        foreign_keys=[away_team_id],
    )
    predictions = relationship(
        "Prediction", back_populates="match", cascade="all, delete-orphan"
    )
    weather_data = relationship(
        "WeatherData", back_populates="match", cascade="all, delete-orphan"
    )
    user_predictions = relationship(
        "UserPrediction", back_populates="match", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Match {self.home_team.name} vs {self.away_team.name} ({self.match_date})>"
