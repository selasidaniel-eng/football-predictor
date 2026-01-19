"""Main FastAPI application entry point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events"""
    # Startup
    print("🚀 Football Predictor API starting...")
    yield
    # Shutdown
    print("🛑 Football Predictor API shutting down...")


# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    description="Machine learning sports prediction API",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# API v1 routes (placeholder structure)
@app.get("/api/v1")
async def api_v1_root():
    """API v1 root endpoint"""
    return {
        "message": "Football Predictor API v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "matches": "/api/v1/matches",
            "predictions": "/api/v1/predictions",
            "users": "/api/v1/users",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
