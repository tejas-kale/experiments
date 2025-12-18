"""Database models using SQLAlchemy"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from pathlib import Path
from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()

class Policy(Base):
    """Insurance policy model"""
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    insurer_name = Column(String(200), nullable=False, index=True)
    product_name = Column(String(300), nullable=False, index=True)
    uin_number = Column(String(100), unique=True, index=True)

    # Coverage details
    min_sum_insured = Column(Integer)  # In INR
    max_sum_insured = Column(Integer)  # In INR
    min_age = Column(Integer)
    max_age = Column(Integer)

    # Policy details (JSON fields)
    waiting_periods = Column(JSON)  # {"initial": 30, "pre_existing": 24, "specific": {...}}
    key_features = Column(JSON)  # List of key features
    major_exclusions = Column(JSON)  # List of exclusions
    optional_covers = Column(JSON)  # List of add-on covers
    network_hospitals = Column(Integer)  # Count
    key_warnings = Column(JSON)  # Important warnings/caveats

    # Premium information
    base_premium_adult = Column(Float)
    base_premium_child = Column(Float)

    # Metadata
    policy_type = Column(String(100))  # individual, family_floater, group, etc.
    renewable = Column(Boolean, default=True)
    cashless_available = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "insurer_name": self.insurer_name,
            "product_name": self.product_name,
            "uin_number": self.uin_number,
            "sum_insured": {
                "min": self.min_sum_insured,
                "max": self.max_sum_insured
            },
            "age_eligibility": {
                "min": self.min_age,
                "max": self.max_age
            },
            "waiting_periods": self.waiting_periods,
            "key_features": self.key_features,
            "major_exclusions": self.major_exclusions,
            "optional_covers": self.optional_covers,
            "network_hospitals": self.network_hospitals,
            "key_warnings": self.key_warnings,
            "policy_type": self.policy_type,
            "renewable": self.renewable,
            "cashless_available": self.cashless_available
        }


class Document(Base):
    """Document model for policy PDFs and other documents"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(Integer, index=True)  # Foreign key to Policy (nullable for user docs)

    # Document info
    insurer_name = Column(String(200), nullable=False, index=True)
    product_name = Column(String(300), index=True)
    document_type = Column(String(100))  # policy_wording, brochure, claim_form, etc.

    # File details
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(300))
    file_size = Column(Integer)  # In bytes
    page_count = Column(Integer)

    # Content
    full_text = Column(Text)  # Full extracted text
    metadata_json = Column(JSON)  # Extracted metadata

    # Source
    source_url = Column(String(500))  # Original download URL
    is_user_uploaded = Column(Boolean, default=False)

    # Processing
    processed = Column(Boolean, default=False)
    extraction_status = Column(String(50))  # pending, processing, completed, failed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "policy_id": self.policy_id,
            "insurer_name": self.insurer_name,
            "product_name": self.product_name,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "page_count": self.page_count,
            "is_user_uploaded": self.is_user_uploaded,
            "processed": self.processed,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class SearchIndex(Base):
    """Search index for quick text searches"""
    __tablename__ = "search_index"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False, index=True)
    policy_id = Column(Integer, index=True)

    # Search fields
    section = Column(String(200), index=True)  # exclusions, coverage, waiting_periods, etc.
    page_number = Column(Integer)
    text_content = Column(Text)
    text_summary = Column(Text)  # AI-generated summary

    # Metadata for better search
    keywords = Column(JSON)  # Extracted keywords

    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationHistory(Base):
    """Store conversation history for context"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(100), index=True)

    role = Column(String(20))  # user, assistant, system
    content = Column(Text)

    # Metadata
    tokens_used = Column(Integer)
    tools_used = Column(JSON)  # List of tools called

    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
engine = None
SessionLocal = None

def init_db():
    """Initialize database"""
    global engine, SessionLocal

    # Ensure data directory exists
    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create engine
    db_path = Config.DATA_DIR / "policies.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    logger.info(f"Database initialized at {db_path}")

def get_db() -> Session:
    """Get database session"""
    global SessionLocal

    if SessionLocal is None:
        init_db()

    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.close()
        raise

def close_db(db: Session):
    """Close database session"""
    db.close()
