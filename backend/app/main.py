from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import init_db
from app.routes import threat_detection, user, stats, analyze, reports, scans
from contextlib import asynccontextmanager
import os
import threading


def _warmup_threat_feeds():
    try:
        from app.services.threat_intel import warmup_feeds
        warmup_feeds()
    except Exception:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    skip = os.getenv("PHISHEYE_SKIP_FEED_WARMUP", "").strip().lower() in {"1", "true", "yes"}
    if not skip:
        threading.Thread(target=_warmup_threat_feeds, daemon=True).start()
    yield


# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="PHISHEYE API",
    description=(
        "AI-powered multi-channel scam intelligence: links, messages, "
        "sender signals, psychological manipulation and community reports."
    ),
    version="2.0.0",
    lifespan=lifespan,
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
app.include_router(analyze.router)
app.include_router(reports.router)
app.include_router(scans.router)


# Root endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "PHISHEYE API Running",
        "version": "2.0.0",
        "product": "AI-powered multi-channel scam intelligence system",
        "endpoints": [
            "POST /api/v1/threat/check-url",
            "POST /api/v1/threat/check-message",
            "POST /api/v1/analyze/content",
            "POST /api/v1/analyze/url",
            "POST /api/v1/analyze/email",
            "POST /api/v1/analyze/qr",
            "POST /api/v1/analyze/screenshot",
            "POST /api/v1/report",
            "POST /api/v1/feedback",
            "GET /api/v1/reputation/domain/{domain}",
            "GET /api/v1/scans",
            "GET /api/v1/threat/intel-status",
            "GET /api/v1/stats/overview",
            "GET /api/v1/stats/sources",
            "GET /api/v1/stats/timeline"
        ]
    }


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
