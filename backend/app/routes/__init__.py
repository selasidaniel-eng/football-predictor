"""
API routes package - includes all route modules.
"""

from .leagues import router as leagues_router
from .teams import router as teams_router
from .matches import router as matches_router
from .auth import router as auth_router
from .predictions import router as predictions_router
from .user_predictions import router as user_predictions_router

__all__ = [
    "leagues_router",
    "teams_router",
    "matches_router",
    "auth_router",
    "predictions_router",
    "user_predictions_router",
]
