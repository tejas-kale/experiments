"""FastAPI application for Health Insurance India"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from pathlib import Path

from agents.insurance_agent import InsuranceAgent
from services.document_service import DocumentService
from services.policy_service import PolicyService
from models.database import get_db, close_db
from models.schemas import (
    ChatMessage,
    ChatResponse,
    PolicyQuery,
    ComparisonRequest,
    ComparisonResponse,
    PremiumCalculationRequest,
    PremiumCalculationResponse,
    PolicyResponse,
    DocumentResponse,
    ErrorResponse
)
from utils.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Health Insurance India API",
    description="Query and compare Indian health insurance policies using AI agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
try:
    agent = InsuranceAgent(api_key=Config.ANTHROPIC_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize agent: {e}")
    agent = None

# Conversation storage (in production, use Redis or database)
conversations = {}


# Dependency to get DB session
def get_database():
    db = get_db()
    try:
        yield db
    finally:
        close_db(db)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "name": "Health Insurance India API",
        "version": "1.0.0",
        "description": "Query Indian health insurance policies using AI agents",
        "docs": "/docs",
        "status": "operational"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "database": "connected"
    }


# Policy Endpoints

@app.get("/policies", response_model=List[PolicyResponse])
def list_policies(
    insurer: Optional[str] = None,
    db: Session = Depends(get_database)
):
    """
    List all available policies

    Args:
        insurer: Filter by insurer name (optional)
    """
    try:
        policy_service = PolicyService(db)

        if insurer:
            policies = policy_service.list_by_insurer(insurer)
        else:
            policies = policy_service.list_all()

        return policies

    except Exception as e:
        logger.error(f"Error listing policies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/policies/{policy_id}", response_model=PolicyResponse)
def get_policy(
    policy_id: str,
    db: Session = Depends(get_database)
):
    """Get specific policy details by ID, UIN, or name"""
    try:
        policy_service = PolicyService(db)
        policy = policy_service.get_by_id_or_name(policy_id)

        if not policy:
            raise HTTPException(status_code=404, detail=f"Policy not found: {policy_id}")

        return policy

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Document Endpoints

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents(
    insurer: Optional[str] = None,
    db: Session = Depends(get_database)
):
    """List all documents"""
    try:
        doc_service = DocumentService(db)

        if insurer:
            documents = doc_service.list_by_insurer(insurer)
        else:
            documents = doc_service.list_all()

        return documents

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_database)
):
    """Get specific document details"""
    try:
        doc_service = DocumentService(db)
        document = doc_service.get_by_id(document_id)

        if not document:
            raise HTTPException(status_code=404, detail=f"Document not found: {document_id}")

        return document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    insurer: Optional[str] = None,
    product: Optional[str] = None,
    db: Session = Depends(get_database)
):
    """Upload user document"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Save file
        upload_dir = Config.DOCUMENTS_DIR / "user_uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / file.filename

        # Write file
        content = await file.read()
        file_path.write_bytes(content)

        # Add to database
        doc_service = DocumentService(db)
        doc_id = doc_service.add_user_document(
            path=str(file_path),
            insurer=insurer,
            product=product,
            auto_extract=True
        )

        return {
            "document_id": doc_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Document uploaded and processed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent/Chat Endpoints

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatMessage):
    """
    Chat with insurance agent

    Args:
        request: Chat message with optional conversation ID
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Please check server configuration."
        )

    try:
        # Get or create conversation
        conv_id = request.conversation_id or "default"

        # Load conversation history if exists
        if conv_id in conversations:
            agent.load_conversation_history(conversations[conv_id])
        else:
            agent.reset_conversation()

        # Get response
        response = agent.chat(request.message)

        # Save conversation history
        conversations[conv_id] = agent.get_conversation_history()

        return ChatResponse(
            response=response,
            sources=[],  # Could be extracted from agent tools
            conversation_id=conv_id
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
def query_policies(request: PolicyQuery):
    """
    Query policies with specific question

    Args:
        request: Query request with question and optional filters
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )

    try:
        # Reset conversation for single query
        response = agent.chat(request.query, reset_history=True)

        return {
            "query": request.query,
            "answer": response
        }

    except Exception as e:
        logger.error(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
def compare_policies(request: ComparisonRequest):
    """
    Compare multiple policies

    Args:
        request: Comparison request with policy IDs and optional aspects
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )

    try:
        question = f"Compare these policies in detail: {', '.join(request.policy_ids)}"

        if request.aspects:
            question += f" focusing on: {', '.join(request.aspects)}"

        response = agent.chat(question, reset_history=True)

        return ComparisonResponse(
            policies=request.policy_ids,
            comparison=response
        )

    except Exception as e:
        logger.error(f"Error in comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calculate-premium", response_model=PremiumCalculationResponse)
def calculate_premium(request: PremiumCalculationRequest):
    """
    Calculate estimated premium

    Args:
        request: Premium calculation request with policy and user details
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )

    try:
        # Use agent's calculate_premium tool
        from agents.tools import calculate_premium as calc_tool

        result = calc_tool(
            policy_id=request.policy_id,
            age=request.age,
            sum_insured=request.sum_insured,
            family_members=request.family_members
        )

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Calculation failed"))

        return PremiumCalculationResponse(
            policy_name=result["policy"],
            estimated_annual_premium=result["estimated_annual_premium"],
            breakdown=result["breakdown"],
            factors=result["factors"],
            disclaimer=result["disclaimer"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating premium: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/insurers")
def list_insurers():
    """List supported insurers"""
    from collectors.base_collector import CollectorFactory

    return {
        "count": len(CollectorFactory.list_all()),
        "insurers": CollectorFactory.list_all()
    }


@app.delete("/conversations/{conversation_id}")
def reset_conversation(conversation_id: str):
    """Reset/delete a conversation"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": "Conversation reset successfully"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=str(exc.status_code)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            code="500"
        ).model_dump()
    )


# Startup/shutdown events

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting Health Insurance India API")

    # Initialize database
    from models.database import init_db
    init_db()

    logger.info("API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Health Insurance India API")


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True,
        log_level="info"
    )
