"""Document service for managing policy documents"""

from typing import List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from models.database import Document
import PyMuPDF


class DocumentService:
    """Service for document operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_all(self) -> List[Document]:
        """List all documents"""
        return self.db.query(Document).all()
    
    def get_by_id(self, doc_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def get_by_policy_id(self, policy_id: int) -> List[Document]:
        """Get all documents for a policy"""
        return self.db.query(Document).filter(Document.policy_id == policy_id).all()
    
    def create(self, **kwargs) -> Document:
        """Create new document"""
        document = Document(**kwargs)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def add_user_document(
        self, 
        path: str, 
        insurer: Optional[str] = None,
        product: Optional[str] = None,
        auto_extract: bool = True
    ) -> int:
        """Add a user-uploaded document"""
        file_path = Path(path)
        
        # Extract text from PDF
        text = ""
        page_count = 0
        
        if file_path.suffix.lower() == '.pdf':
            try:
                doc = PyMuPDF.open(str(file_path))
                page_count = len(doc)
                for page in doc:
                    text += page.get_text()
                doc.close()
            except Exception as e:
                raise ValueError(f"Failed to read PDF: {e}")
        
        # Create document
        document = self.create(
            insurer_name=insurer or "Unknown",
            product_name=product or "User Document",
            document_type="user_upload",
            file_path=str(file_path),
            file_name=file_path.name,
            page_count=page_count,
            full_text=text,
            is_user_upload=True
        )
        
        return document.id
    
    def search(
        self, 
        query: str, 
        policy_id: Optional[str] = None,
        section: Optional[str] = None
    ) -> List[dict]:
        """Search in document text"""
        documents = self.list_all()
        
        if policy_id:
            try:
                pid = int(policy_id)
                documents = [d for d in documents if d.policy_id == pid]
            except ValueError:
                pass
        
        results = []
        for doc in documents:
            if not doc.full_text:
                continue
            
            # Simple text search
            text = doc.full_text.lower()
            query_lower = query.lower()
            
            if query_lower in text:
                # Extract context around match
                idx = text.find(query_lower)
                start = max(0, idx - 100)
                end = min(len(text), idx + len(query) + 100)
                context = doc.full_text[start:end]
                
                results.append({
                    "policy_name": doc.product_name,
                    "section": section or "General",
                    "matched_text": context,
                    "page_number": 1  # Simplified
                })
        
        return results
    
    def extract_section(self, policy_id: str, section_name: str) -> str:
        """Extract specific section from policy document"""
        try:
            pid = int(policy_id)
            documents = self.get_by_policy_id(pid)
        except ValueError:
            documents = self.list_all()
        
        for doc in documents:
            if doc.sections and section_name in doc.sections:
                return doc.sections[section_name]
            
            # Fallback: search in full text
            if doc.full_text and section_name.lower() in doc.full_text.lower():
                return doc.full_text
        
        return f"Section '{section_name}' not found"
    
    def get_text(
        self, 
        document_id: str, 
        page_start: Optional[int] = None,
        page_end: Optional[int] = None
    ) -> str:
        """Get document text"""
        try:
            doc_id = int(document_id)
            doc = self.get_by_id(doc_id)
            if doc:
                return doc.full_text or ""
        except ValueError:
            pass
        
        return ""
    
    def extract_metadata(self, doc_id: int) -> dict:
        """Extract metadata from document using AI (placeholder)"""
        # This would use Claude to extract metadata
        # For now, return basic info
        doc = self.get_by_id(doc_id)
        if doc:
            return {
                "insurer": doc.insurer_name,
                "product": doc.product_name,
                "type": doc.document_type
            }
        return {}
    
    def count(self) -> int:
        """Count total documents"""
        return self.db.query(Document).count()
