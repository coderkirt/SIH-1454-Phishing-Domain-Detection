"""FastAPI application for the PHISHEYE Standalone RAG Service.

Exposes:
- POST /api/explain-scan: Grounded threat explanation with citations and playbook matching
- GET  /api/health: Health check, collection stats, and index metrics
- GET  /api/cache/stats: In-memory LRU/TTL cache hit-rate and capacity telemetry
- POST /api/cache/clear: Administrative cache purge endpoint
- GET  /: Root service status and API documentation index
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.cache import make_cache_key, scan_cache
from app.chroma_store import get_or_create_collection
from app.config import settings
from app.corpus import load_corpus
from app.generator import generate_explanation
from app.retrieval import HybridRetriever
from app.schemas import ExplainScanRequest, ExplainScanResponse, HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("phisheye.rag_service")

# Global retriever instance
_retriever: Optional[HybridRetriever] = None
_corpus_doc_count: int = 0
_indexed_chunks_count: int = 0
_start_time: float = 0.0


def get_retriever() -> HybridRetriever:
    """Retrieve the initialized HybridRetriever singleton."""
    global _retriever
    if _retriever is None:
        logger.info("Initializing HybridRetriever singleton...")
        _retriever = HybridRetriever(
            k_rrf=settings.RRF_K,
            w_dense=settings.DENSE_WEIGHT,
            w_sparse=settings.SPARSE_WEIGHT,
        )
    return _retriever


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown lifecycle for the RAG service."""
    global _retriever, _corpus_doc_count, _indexed_chunks_count, _start_time
    _start_time = time.time()
    logger.info("Starting PHISHEYE Standalone RAG Service...")

    try:
        # Load corpus and check ChromaDB
        docs = load_corpus()
        _corpus_doc_count = len(docs)
        collection = get_or_create_collection()
        _indexed_chunks_count = collection.count()

        # Initialize retriever
        _retriever = get_retriever()
        logger.info(
            "RAG Service initialized successfully: %d corpus docs, %d indexed chunks in ChromaDB",
            _corpus_doc_count,
            _indexed_chunks_count,
        )
    except Exception as exc:
        logger.error("Error during RAG service startup: %s", exc, exc_info=True)

    yield

    logger.info("Shutting down PHISHEYE Standalone RAG Service...")


app = FastAPI(
    title="PHISHEYE RAG Service",
    description=(
        "Standalone Grounded Explainability & Threat Intelligence Service for the "
        "PHISHEYE Phishing Domain Detection Platform. Combines hybrid dense/sparse "
        "retrieval with Reciprocal Rank Fusion (RRF), structured attack playbooks, "
        "anti-hallucination citation resolution, and in-memory LRU/TTL caching."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for local cross-service communication and web dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Service Index")
async def root() -> Dict[str, Any]:
    """Root endpoint providing service metadata and documentation links."""
    return {
        "service": "PHISHEYE Standalone RAG Service",
        "status": "online",
        "version": "1.0.0",
        "port": settings.PORT,
        "docs_url": "/docs",
        "health_url": "/api/health",
        "explain_scan_url": "/api/explain-scan",
    }


@app.get("/api/health", response_model=HealthResponse, summary="Health & Index Status")
async def health_check() -> HealthResponse:
    """Return service health, corpus document counts, and ChromaDB indexed chunk statistics."""
    global _corpus_doc_count, _indexed_chunks_count
    try:
        collection = get_or_create_collection()
        chunks_count = collection.count()
    except Exception:
        chunks_count = _indexed_chunks_count

    return HealthResponse(
        status="ok",
        service="phisheye-rag-service",
        version="1.0.0",
        indexed_chunks=chunks_count,
        corpus_documents=_corpus_doc_count,
    )


@app.get("/api/cache/stats", summary="Cache Telemetry")
async def cache_stats() -> Dict[str, Any]:
    """Return in-memory LRU and TTL scan explanation cache health metrics."""
    return scan_cache.stats()


@app.post("/api/cache/clear", summary="Clear Explanation Cache")
async def clear_cache() -> Dict[str, Any]:
    """Administrative endpoint to purge all cached scan explanations."""
    scan_cache.clear()
    return {"status": "cleared", "message": "Explanation cache successfully purged"}


@app.post(
    "/api/explain-scan",
    response_model=ExplainScanResponse,
    summary="Generate Grounded Threat Explanation",
    status_code=status.HTTP_200_OK,
)
async def explain_scan(request: ExplainScanRequest) -> ExplainScanResponse:
    """Generate a transparent, verifiable threat explanation for a completed or active scan.

    Execution Pipeline:
    1. Check in-memory LRU/TTL cache using deterministic request hash.
    2. Synthesize multi-faceted query from URL, content, detected brands, and threat tags.
    3. Execute filtered hybrid retrieval combining ChromaDB dense embeddings and BM25 with RRF.
    4. Apply soft signal boosting for detected brand names and threat tags.
    5. Resolve citations and synthesize structured output (deterministic offline or live Gemini).
    6. Cache response and return structured ExplainScanResponse with latency telemetry.
    """
    t_start = time.perf_counter()

    # 1. Cache lookup
    cache_key = make_cache_key(request)
    cached_resp = scan_cache.get(cache_key)
    if cached_resp is not None:
        cached_resp.latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
        return cached_resp

    # 2. Build retrieval query
    query_parts = []
    if request.content_text and request.content_text.strip():
        query_parts.append(request.content_text.strip())
    if request.scan_url and request.scan_url.strip():
        query_parts.append(request.scan_url.strip())
    if not query_parts:
        if request.detected_brands:
            query_parts.extend(request.detected_brands)
        if request.threat_tags:
            query_parts.extend(request.threat_tags)

    query = " ".join(query_parts) if query_parts else "phishing scam indicators"

    # 3. Retrieve knowledge chunks via HybridRetriever
    retriever = get_retriever()
    channels = [request.channel] if request.channel else None
    
    retrieved_chunks = retriever.retrieve(
        query=query,
        brands=request.detected_brands,
        threat_tags=request.threat_tags,
        channels=channels,
        top_k=request.top_k,
    )

    # 4. Generate grounded explanation
    response = await generate_explanation(request, retrieved_chunks)

    # 5. Measure latency and update cache
    total_elapsed_ms = (time.perf_counter() - t_start) * 1000
    response.latency_ms = round(total_elapsed_ms, 2)
    response.cached = False

    scan_cache.set(cache_key, response)

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
