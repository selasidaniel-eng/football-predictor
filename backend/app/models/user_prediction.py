"""UserPrediction model for storing user's saved predictions and bets"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class UserPrediction(Base):
    """UserPrediction model - tracks user's saved predictions and betting"""

    __tablename__ = "user_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    
    # User's prediction
    prediction = Column(String(50), nullable=False)  # home_win, draw, away_win, over_2_5, under_2_5
    confidence_level = Column(Integer, default=50, nullable=False)  # 1-100
    
    # Odds and betting
    odds_selected = Column(Float, nullable=True)
    stake_amount = Column(Float, nullable=True)  # Actual bet amount
    potential_winnings = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), default="pending", nullable=False)  # pending, won, lost, voided
    result = Column(String(50), nullable=True)  # home_win, draw, away_win (actual result)
    is_correct = Column(Integer, nullable=True)  # 1 = correct, 0 = incorrect
    
    # Notes and reasoning
    reasoning = Column(Text, nullable=True)  # Why did user make this prediction
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    settled_at = Column(DateTime, nullable=True)  # When result was determined

    # Relationships
    user = relationship("User", back_populates="user_predictions")
    match = relationship("Match", back_populates="user_predictions")

    def __repr__(self):
        return f"<UserPrediction user_id={self.user_id} match_id={self.match_id}>"
