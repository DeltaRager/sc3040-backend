"""
FastAPI Backend with Supabase Authentication
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from protected_routes import router as protected_router
from leaderboard_routes import router as leaderboard_router
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="SignLingo API",
    description="Backend API for SignLingo - Sign Language Learning Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes with error handling
try:
    app.include_router(protected_router)
    app.include_router(leaderboard_router)
    logger.info("Routes loaded successfully")
except Exception as e:
    logger.error(f"Error loading routes: {e}")
    raise

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "SignLingo API is running!", "version": "1.0.0"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.environment}

# Example public endpoint (no authentication required)
@app.get("/api/public")
async def public_endpoint():
    return {"message": "This is a public endpoint - no authentication required"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
