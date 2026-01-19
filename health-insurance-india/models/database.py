"""Database models and initialization"""

from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from utils.config import Config

Base = declarative_base()


class Policy(Base):
    """Insurance policy model"""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True)
    insurer_name = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    uin_number = Column(String, unique=True)
    
    # Coverage details
    min_sum_insured = Column(Float)
    max_sum_insured = Column(Float)
    
    # Eligibility
    min_age = Column(Integer)
    max_age = Column(Integer)
    
    # Policy details (JSON fields)
    waiting_periods = Column(JSON)
    key_features = Column(JSON)
    major_exclusions = Column(JSON)
    optional_covers = Column(JSON)
    network_hospitals = Column(Integer)
    key_warnings = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "insurer_name": self.insurer_name,
            "product_name": self.product_name,
            "uin_number": self.uin_number,
            "min_sum_insured": self.min_sum_insured,
            "max_sum_insured": self.max_sum_insured,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "waiting_periods": self.waiting_periods,
            "key_features": self.key_features,
            "major_exclusions": self.major_exclusions,
            "optional_covers": self.optional_covers,
            "network_hospitals": self.network_hospitals,
            "key_warnings": self.key_warnings,
        }


class Document(Base):
    """Policy document model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, nullable=True)  # Can be null for user uploads
    
    # Document metadata
    insurer_name = Column(String, nullable=False)
    product_name = Column(String)
    document_type = Column(String)  # policy_wording, brochure, rate_card, etc.
    
    # File details
    file_path = Column(String, nullable=False)
    file_name = Column(String)
    page_count = Column(Integer)
    
    # Content
    full_text = Column(Text)
    sections = Column(JSON)  # {"section_name": "section_text"}
    
    # User uploads
    is_user_upload = Column(Boolean, default=False)
    
    # Metadata
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
            "page_count": self.page_count,
            "is_user_upload": self.is_user_upload,
        }


# Database setup
engine = None
SessionLocal = None


def init_db():
    """Initialize database"""
    global engine, SessionLocal
    
    Config.ensure_directories()
    
    engine = create_engine(
        Config.database_url,
        connect_args={"check_same_thread": False}
    )
    
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return engine


def get_db() -> Session:
    """Get database session"""
    global SessionLocal
    
    if SessionLocal is None:
        init_db()
    
    return SessionLocal()
