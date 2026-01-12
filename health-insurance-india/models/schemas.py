"""Pydantic schemas for API validation"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PolicyBase(BaseModel):
    """Base policy schema"""
    insurer_name: str
    product_name: str
    uin_number: Optional[str] = None


class PolicyCreate(PolicyBase):
    """Schema for creating a policy"""
    min_sum_insured: Optional[int] = None
    max_sum_insured: Optional[int] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    waiting_periods: Optional[Dict[str, Any]] = None
    key_features: Optional[List[str]] = None
    major_exclusions: Optional[List[str]] = None
    optional_covers: Optional[List[str]] = None
    network_hospitals: Optional[int] = None
    key_warnings: Optional[List[str]] = None
    policy_type: Optional[str] = "individual"
    renewable: bool = True
    cashless_available: bool = True


class PolicyResponse(PolicyBase):
    """Schema for policy response"""
    id: int
    min_sum_insured: Optional[int]
    max_sum_insured: Optional[int]
    min_age: Optional[int]
    max_age: Optional[int]
    waiting_periods: Optional[Dict[str, Any]]
    key_features: Optional[List[str]]
    major_exclusions: Optional[List[str]]
    optional_covers: Optional[List[str]]
    network_hospitals: Optional[int]
    key_warnings: Optional[List[str]]
    policy_type: Optional[str]
    renewable: bool
    cashless_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Base document schema"""
    insurer_name: str
    product_name: Optional[str] = None
    document_type: str = "policy_wording"


class DocumentCreate(DocumentBase):
    """Schema for creating a document"""
    file_path: str
    source_url: Optional[str] = None
    is_user_uploaded: bool = False


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    policy_id: Optional[int]
    file_path: str
    file_name: Optional[str]
    file_size: Optional[int]
    page_count: Optional[int]
    processed: bool
    extraction_status: Optional[str]
    is_user_uploaded: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Chat message schema"""
    message: str
    policy_filter: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_id: str
    tokens_used: Optional[int] = None


class PolicyQuery(BaseModel):
    """Policy query schema"""
    query: str
    policy_ids: Optional[List[str]] = None
    section: Optional[str] = None


class ComparisonRequest(BaseModel):
    """Policy comparison request"""
    policy_ids: List[str] = Field(..., min_length=2)
    aspects: Optional[List[str]] = None


class ComparisonResponse(BaseModel):
    """Policy comparison response"""
    policies: List[str]
    comparison: str
    comparison_table: Optional[Dict[str, Any]] = None


class PremiumCalculationRequest(BaseModel):
    """Premium calculation request"""
    policy_id: str
    age: int = Field(..., ge=18, le=100)
    sum_insured: Optional[int] = Field(None, ge=100000)
    family_members: int = Field(1, ge=1, le=10)
    has_pre_existing: bool = False


class PremiumCalculationResponse(BaseModel):
    """Premium calculation response"""
    policy_name: str
    estimated_annual_premium: float
    breakdown: Dict[str, float]
    factors: Dict[str, Any]
    disclaimer: str


class DocumentUpload(BaseModel):
    """Document upload schema"""
    insurer: Optional[str] = None
    product: Optional[str] = None
    auto_extract: bool = True


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
