"""Injury model for storing player injury information"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from ..database import Base


class Injury(Base):
    """Injury model - tracks player injuries"""

    __tablename__ = "injuries"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    
    player_name = Column(String(255), nullable=False, index=True)
    position = Column(String(50), nullable=True)  # e.g., "striker", "midfielder"
    severity = Column(String(50), default="minor", nullable=False)  # minor, moderate, severe
    
    injury_date = Column(DateTime, nullable=False)
    expected_return = Column(DateTime, nullable=True)
    status = Column(String(50), default="injured", nullable=False)  # injured, recovered, doubtful
    
    description = Column(Text, nullable=True)
    impact_score = Column(Integer, default=5, nullable=False)  # 1-10 importance to team
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Injury {self.player_name} ({self.status})>"
