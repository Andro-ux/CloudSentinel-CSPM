from pathlib import Path
import logging

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.session import Base, engine
from backend.api.app import create_app
from backend.scheduler.scanner import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("cloudsentinel")

APP_VERSION = "1.0.0"

app = create_app()


@app.on_event("startup")
def startup():
    logger.info("Starting CloudSentinel...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")
    start_scheduler()
    logger.info("Scheduler started.")


@app.on_event("shutdown")
def shutdown():
    logger.info("CloudSentinel shutting down.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )