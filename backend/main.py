from pathlib import Path
import logging

from dotenv import load_dotenv

# Load environment variables before importing the application
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.session import Base, engine
from backend.api.routes import router as api_router
from backend.scheduler.scanner import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("cloudsentinel")

APP_VERSION = "0.4.0"

app = FastAPI(
    title="CloudSentinel",
    description="AWS Cloud Security Monitoring Platform",
    version=APP_VERSION,
)


@app.on_event("startup")
def startup():

    logger.info("Starting CloudSentinel...")

    # Create database tables
    Base.metadata.create_all(bind=engine)

    logger.info("Database initialized.")

    # Start background scheduler
    start_scheduler()

    logger.info("Scheduler started.")


@app.on_event("shutdown")
def shutdown():
    logger.info("CloudSentinel shutting down.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )