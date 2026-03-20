from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import DEBUG, API_HOST, API_PORT
from core.database import init_db
from scheduler.job_scheduler import start_scheduler, stop_scheduler
from api.auth import router as auth_router
from api.integrations import router as integrations_router
from api.posts import router as posts_router

app = FastAPI(
    title="SMF Social v2 API",
    version="2.0.0",
    description="Standalone social media automation platform"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(integrations_router)
app.include_router(posts_router)

@app.on_event("startup")
def startup_event():
    """Initialize database and scheduler on startup."""
    init_db()
    start_scheduler()
    print("✅ Server ready")

@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown."""
    stop_scheduler()

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, reload=DEBUG)
