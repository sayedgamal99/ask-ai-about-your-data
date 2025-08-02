import os
import logging
from dotenv import load_dotenv

# Get project root path (go up 2 levels from config.py: config -> src -> project_root)
ROOT_PATH = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

load_dotenv(os.path.join(ROOT_PATH, ".env"), override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Settings:
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")

    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5599")
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5599"))

    # Assets Directory
    ASSETS_DIR = os.path.join(ROOT_PATH, "assets")

    @classmethod
    def get_ollama_url(cls):
        return f"{cls.OLLAMA_BASE_URL}/api/chat"
