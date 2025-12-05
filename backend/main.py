"""
Data Poisoning Detection Tool - Main FastAPI Application.

A production-grade tool for detecting data poisoning, backdoor triggers,
and assessing training collapse risk.

All data is SYNTHETIC and SAFE for educational purposes.
"""

from pathlib import Path
from typing import Any, Dict, Union

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import (
    clean_router,
    collapse_router,
    poison_router,
    report_router,
    scan_router,
)
from backend.utils import logger

# Application metadata
APP_TITLE = "Data Poisoning Detection Tool"
APP_VERSION = "1.0.2"
APP_DESCRIPTION = """
🛡️ **Data Poisoning Detection Tool**

A comprehensive platform for detecting training data poisoning attacks:

- **Spectral Signatures Analysis**: PCA/SVD-based outlier detection
- **Activation Clustering**: Neural network activation analysis
- **Trigger Pattern Detection**: Backdoor trigger identification
- **Influence Function Estimation**: Harmful sample detection
- **Collapse Risk Assessment**: Training safety evaluation

All datasets are **synthetic** and **safe** for educational purposes.
"""

# Initialize FastAPI
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(scan_router)
app.include_router(poison_router)
app.include_router(clean_router)
app.include_router(collapse_router)
app.include_router(report_router)

# Static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "version": APP_VERSION, "service": APP_TITLE}


@app.get("/dashboard", response_model=None)
async def serve_dashboard() -> Union[FileResponse, Dict[str, str]]:
    """Serve the dashboard HTML."""
    dashboard_path = frontend_path / "index.html"
    if dashboard_path.exists():
        return FileResponse(str(dashboard_path))
    return {"error": "Dashboard not found", "path": str(dashboard_path)}


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "dashboard": "/dashboard",
            "scan": "/scan",
            "detect_poison": "/detect_poison",
            "clean": "/clean",
            "collapse_risk": "/collapse_risk",
            "report": "/report",
        },
        "safety_notice": "All data is synthetic. No real attacks or PII.",
    }


if __name__ == "__main__":
    logger.info(f"Starting {APP_TITLE} v{APP_VERSION}")
    uvicorn.run(
        "backend.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
