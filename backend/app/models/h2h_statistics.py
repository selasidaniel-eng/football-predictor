"""H2HStatistics model for storing head-to-head records"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer

from ..database import Base


class H2HStatistics(Base):
    """H2HStatistics model - caches head-to-head statistics between teams"""

    __tablename__ = "h2h_statistics"

    id = Column(Integer, primary_key=True, index=True)
    team_a_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    team_b_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    
    # Head-to-head record (team_a perspective)
    total_matches = Column(Integer, default=0, nullable=False)
    team_a_wins = Column(Integer, default=0, nullable=False)
    draws = Column(Integer, default=0, nullable=False)
    team_b_wins = Column(Integer, default=0, nullable=False)
    
    # Goals
    team_a_goals = Column(Integer, default=0, nullable=False)
    team_b_goals = Column(Integer, default=0, nullable=False)
    
    # Recent H2H (last 5)
    recent_team_a_wins = Column(Integer, default=0, nullable=False)
    recent_draws = Column(Integer, default=0, nullable=False)
    recent_team_b_wins = Column(Integer, default=0, nullable=False)
    recent_team_a_goals = Column(Integer, default=0, nullable=False)
    recent_team_b_goals = Column(Integer, default=0, nullable=False)
    
    # Home/Away advantage in H2H
    team_a_home_wins = Column(Integer, default=0, nullable=False)
    team_a_away_wins = Column(Integer, default=0, nullable=False)
    team_a_home_draws = Column(Integer, default=0, nullable=False)
    team_a_away_draws = Column(Integer, default=0, nullable=False)
    
    # Statistical metrics
    team_a_win_rate = Column(Float, default=0.0, nullable=False)
    team_b_win_rate = Column(Float, default=0.0, nullable=False)
    average_goals_per_match = Column(Float, default=0.0, nullable=False)
    
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<H2HStatistics team_a={self.team_a_id} vs team_b={self.team_b_id}>"
