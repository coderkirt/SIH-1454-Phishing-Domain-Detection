from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import init_db
from app.routes import threat_detection, user, stats

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="CyberGuard API",
    description="AI-powered threat detection platform",
    version="1.0.0"
)

# Add CORS middleware (allow all origins for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(threat_detection.router)
app.include_router(user.router)
app.include_router(stats.router)


# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "CyberGuard API Running",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/v1/threat/check-url",
            "POST /api/v1/threat/check-message",
            "GET /api/v1/threat/stats",
            "GET /api/v1/threat/recent-urls",
            "POST /api/v1/user/signup",
            "POST /api/v1/user/login",
            "GET /api/v1/user/profile",
            "GET /api/v1/stats/overview",
            "GET /api/v1/stats/threat-types",
            "GET /api/v1/stats/risk-distribution",
            "GET /api/v1/stats/daily-summary"
        ]
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
