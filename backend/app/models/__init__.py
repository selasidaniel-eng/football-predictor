"""Database models for the Football Predictor application"""

from .league import League
from .team import Team
from .match import Match
from .user import User
from .injury import Injury
from .prediction import Prediction
from .team_form import TeamForm
from .h2h_statistics import H2HStatistics
from .weather_data import WeatherData
from .user_prediction import UserPrediction
from .user_profile import UserProfile

__all__ = [
    "League",
    "Team",
    "Match",
    "User",
    "Injury",
    "Prediction",
    "TeamForm",
    "H2HStatistics",
    "WeatherData",
    "UserPrediction",
    "UserProfile",
]
