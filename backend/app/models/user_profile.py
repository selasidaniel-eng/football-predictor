"""UserProfile model for storing user profile and statistics"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text

from ..database import Base


class UserProfile(Base):
    """UserProfile model - extended user statistics and preferences"""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Statistics
    total_predictions = Column(Integer, default=0, nullable=False)
    correct_predictions = Column(Integer, default=0, nullable=False)
    win_rate = Column(Float, default=0.0, nullable=False)  # percentage
    
    # Betting statistics
    total_stake = Column(Float, default=0.0, nullable=False)
    total_winnings = Column(Float, default=0.0, nullable=False)
    net_profit = Column(Float, default=0.0, nullable=False)
    roi = Column(Float, default=0.0, nullable=False)  # Return on investment %
    
    # Preferences
    favorite_leagues = Column(Text, nullable=True)  # JSON string of league IDs
    favorite_teams = Column(Text, nullable=True)  # JSON string of team IDs
    preferred_bet_types = Column(Text, nullable=True)  # JSON array
    max_stake = Column(Float, default=100.0, nullable=False)
    
    # Tracking
    streak_wins = Column(Integer, default=0, nullable=False)
    streak_losses = Column(Integer, default=0, nullable=False)
    best_streak_wins = Column(Integer, default=0, nullable=False)
    
    # Calculated metrics
    average_odds = Column(Float, default=0.0, nullable=False)
    prediction_accuracy_trend = Column(Float, default=0.0, nullable=False)  # 7-day trend
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserProfile user_id={self.user_id} win_rate={self.win_rate}%>"
