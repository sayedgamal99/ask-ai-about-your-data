import subprocess
import requests
import logging
from fastapi import FastAPI
from src.api.endpoints import router
from src.configs.config import Settings
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ask AI About Your Data",
    description="Upload CSV dataset and ask questions in natural language to get some insights about your data",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, be more specific
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


@app.on_event("startup")
async def on_startup():
    """Initialize application on startup"""
    logger.info("Starting Ask AI About Your Data application...")

    # Simple check and start Ollama if needed
    try:
        response = requests.get(
            f"{Settings.OLLAMA_BASE_URL}/api/tags", timeout=3)
        logger.info("✅ Ollama is running!")
    except:
        logger.info("Starting Ollama...")
        subprocess.Popen(["ollama", "serve"], shell=True)
        logger.info("✅ Ollama started!")

    logger.info("Application startup completed")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to Ask AI About Your Data API",
        "description": "Upload a CSV file and ask questions in natural language",
        "version": "2.0.0",
        "endpoints": {
            "upload_file": "/upload",
            "ask_question": "/answer"
        }
    }
