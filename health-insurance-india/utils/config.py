"""Configuration management for Health Insurance CLI"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    METADATA_DIR = DATA_DIR / "metadata"

    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/policies.db")

    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Anthropic Settings
    ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 4096

    # Document Processing
    MAX_PDF_SIZE_MB = 50
    SUPPORTED_FORMATS = [".pdf"]

    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.DOCUMENTS_DIR.mkdir(exist_ok=True)
        cls.METADATA_DIR.mkdir(exist_ok=True)

        # Create insurer directories
        insurers = [
            "sbi_general",
            "hdfc_ergo",
            "icici_lombard",
            "star_health",
            "care_health",
            "bajaj_allianz",
            "max_bupa",
            "niva_bupa",
            "aditya_birla",
            "manipalcigna",
            "user_uploads"
        ]

        for insurer in insurers:
            (cls.DOCUMENTS_DIR / insurer).mkdir(exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Please set it in .env file or environment."
            )

        cls.ensure_directories()
        return True

# Initialize on import
Config.ensure_directories()
