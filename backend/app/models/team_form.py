"""TeamForm model for storing cached team form metrics"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer

from ..database import Base


class TeamForm(Base):
    """TeamForm model - caches rolling form metrics for performance"""

    __tablename__ = "team_form"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, unique=True, index=True)
    
    # Last 5 matches
    wins_last_5 = Column(Integer, default=0, nullable=False)
    draws_last_5 = Column(Integer, default=0, nullable=False)
    losses_last_5 = Column(Integer, default=0, nullable=False)
    goals_for_last_5 = Column(Integer, default=0, nullable=False)
    goals_against_last_5 = Column(Integer, default=0, nullable=False)
    
    # Last 10 matches
    wins_last_10 = Column(Integer, default=0, nullable=False)
    draws_last_10 = Column(Integer, default=0, nullable=False)
    losses_last_10 = Column(Integer, default=0, nullable=False)
    goals_for_last_10 = Column(Integer, default=0, nullable=False)
    goals_against_last_10 = Column(Integer, default=0, nullable=False)
    
    # Season aggregate
    wins_season = Column(Integer, default=0, nullable=False)
    draws_season = Column(Integer, default=0, nullable=False)
    losses_season = Column(Integer, default=0, nullable=False)
    goals_for_season = Column(Integer, default=0, nullable=False)
    goals_against_season = Column(Integer, default=0, nullable=False)
    
    # Performance metrics
    average_goals_per_match = Column(Float, default=0.0, nullable=False)
    average_goals_conceded = Column(Float, default=0.0, nullable=False)
    form_rating = Column(Float, default=50.0, nullable=False)  # 0-100 scale
    consistency_score = Column(Float, default=50.0, nullable=False)  # Volatility measure
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TeamForm team_id={self.team_id} rating={self.form_rating}>"
