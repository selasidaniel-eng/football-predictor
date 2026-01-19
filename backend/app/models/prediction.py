"""Prediction model for storing AI predictions"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Prediction(Base):
    """Prediction model - stores ML model predictions for matches"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    
    # Prediction probabilities
    probability_home_win = Column(Float, nullable=False)  # 0-1
    probability_draw = Column(Float, nullable=False)  # 0-1
    probability_away_win = Column(Float, nullable=False)  # 0-1
    
    # Expected goals
    expected_goals_home = Column(Float, nullable=True)  # xG
    expected_goals_away = Column(Float, nullable=True)  # xG
    
    # Confidence metrics
    model_confidence = Column(Float, nullable=False)  # 0-1
    model_version = Column(String(50), nullable=False, default="v1.0")
    
    # Prediction result
    prediction_outcome = Column(String(50), nullable=True)  # home_win, draw, away_win
    was_correct = Column(Integer, nullable=True)  # 1 = correct, 0 = incorrect
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction match_id={self.match_id} confidence={self.model_confidence}>"
