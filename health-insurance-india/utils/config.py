"""Configuration management"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Keys
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    documents_dir = data_dir / "documents"
    database_path = data_dir / "policies.db"
    
    # Database
    database_url = f"sqlite:///{database_path}"
    
    # Anthropic
    model_name = "claude-sonnet-4-20250514"
    max_tokens = 4096
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist"""
        cls.data_dir.mkdir(parents=True, exist_ok=True)
        cls.documents_dir.mkdir(parents=True, exist_ok=True)
