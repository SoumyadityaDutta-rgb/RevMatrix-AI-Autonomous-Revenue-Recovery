"""
RevMatrix AI - Main FastAPI Application
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routers import recovery_api, voice_api, analytics_api
from app.config import settings

app = FastAPI(
    title="RevMatrix AI - Autonomous Revenue Recovery Engine",
    description="Autonomous Agentic Revenue Recovery Platform for Razorpay Buildathon (Track 03)",
    version=settings.APP_VERSION
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(recovery_api.router)
app.include_router(voice_api.router)
app.include_router(analytics_api.router)

# Static Files & Dashboard UI
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "RevMatrix AI Backend Active", "docs_url": "/docs"}

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "razorpay_mode": "live" if not settings.RAZORPAY_KEY_ID.startswith("rzp_test_revmatrix_demo") else "sandbox_mock"
    }
