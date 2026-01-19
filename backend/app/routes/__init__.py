"""
API routes package - includes all route modules.
"""

from .leagues import router as leagues_router
from .teams import router as teams_router
from .matches import router as matches_router

__all__ = [
    "leagues_router",
    "teams_router",
    "matches_router",
]
