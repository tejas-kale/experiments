"""FastAPI server for Health Insurance India"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from agents.insurance_agent import InsuranceAgent
from services.document_service import DocumentService
from services.policy_service import PolicyService
from models.database import get_db
from utils.config import Config

app = FastAPI(
    title="Health Insurance India API",
    description="Query Indian health insurance policies using AI agents",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
config = Config()
agent = InsuranceAgent(api_key=config.anthropic_api_key)


# Pydantic models
class ChatRequest(BaseModel):
    message: str
    policy_filter: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []
    conversation_id: str


class PolicyQuery(BaseModel):
    query: str
    policy_ids: Optional[List[str]] = None


class ComparisonRequest(BaseModel):
    policy_ids: List[str]
    aspects: Optional[List[str]] = None


# Endpoints
@app.get("/")
def root():
    return {
        "name": "Health Insurance India API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/policies")
def list_policies():
    """List all available policies"""
    db = get_db()
    policies = PolicyService(db).list_all()
    
    return {
        "count": len(policies),
        "policies": [
            {
                "id": p.id,
                "insurer": p.insurer_name,
                "product": p.product_name,
                "uin": p.uin_number,
                "sum_insured_range": {
                    "min": p.min_sum_insured,
                    "max": p.max_sum_insured
                }
            }
            for p in policies
        ]
    }


@app.get("/policies/{policy_id}")
def get_policy(policy_id: str):
    """Get specific policy details"""
    db = get_db()
    policy = PolicyService(db).get_by_id_or_name(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return {
        "id": policy.id,
        "insurer": policy.insurer_name,
        "product": policy.product_name,
        "details": policy.to_dict()
    }


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Chat with insurance agent"""
    
    # Reset if new conversation
    if not request.conversation_id:
        agent.reset_conversation()
    
    response = agent.chat(request.message)
    
    return ChatResponse(
        response=response,
        sources=[],
        conversation_id=request.conversation_id or "new"
    )


@app.post("/query")
def query_policies(request: PolicyQuery):
    """Query policies with specific question"""
    
    response = agent.chat(request.query)
    
    return {
        "query": request.query,
        "answer": response
    }


@app.post("/compare")
def compare_policies(request: ComparisonRequest):
    """Compare multiple policies"""
    
    question = f"Compare these policies: {', '.join(request.policy_ids)}"
    if request.aspects:
        question += f" focusing on: {', '.join(request.aspects)}"
    
    response = agent.chat(question)
    
    return {
        "policies": request.policy_ids,
        "comparison": response
    }


@app.get("/documents")
def list_documents():
    """List all documents"""
    db = get_db()
    documents = DocumentService(db).list_all()
    
    return {
        "count": len(documents),
        "documents": [d.to_dict() for d in documents]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
