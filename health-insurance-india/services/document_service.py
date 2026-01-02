"""Document service for document management"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pathlib import Path
import shutil
import requests
from models.database import Document, SearchIndex
from models.schemas import DocumentCreate
from utils.pdf_utils import PDFProcessor
from utils.logger import get_logger
from utils.config import Config

logger = get_logger(__name__)


class DocumentService:
    """Service for document operations"""

    def __init__(self, db: Session):
        self.db = db
        self.pdf_processor = PDFProcessor()

    def create(self, document_data: DocumentCreate) -> Document:
        """Create a new document record"""
        # Extract PDF metadata
        pdf_path = Path(document_data.file_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"Document not found: {pdf_path}")

        if not self.pdf_processor.validate_pdf(pdf_path):
            raise ValueError(f"Invalid PDF file: {pdf_path}")

        # Get metadata
        page_count = self.pdf_processor.get_page_count(pdf_path)
        file_size = pdf_path.stat().st_size

        # Extract text
        full_text = self.pdf_processor.extract_text(pdf_path)

        # Create document
        document = Document(
            insurer_name=document_data.insurer_name,
            product_name=document_data.product_name,
            document_type=document_data.document_type,
            file_path=str(pdf_path),
            file_name=pdf_path.name,
            file_size=file_size,
            page_count=page_count,
            full_text=full_text,
            source_url=document_data.source_url,
            is_user_uploaded=document_data.is_user_uploaded,
            processed=True,
            extraction_status="completed"
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        logger.info(f"Created document: {document.file_name} ({page_count} pages)")
        return document

    def get_by_id(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_all(self) -> List[Document]:
        """List all documents"""
        return self.db.query(Document).order_by(Document.created_at.desc()).all()

    def list_by_insurer(self, insurer_name: str) -> List[Document]:
        """List documents by insurer"""
        return self.db.query(Document).filter(
            Document.insurer_name.ilike(f"%{insurer_name}%")
        ).all()

    def list_by_policy(self, policy_id: int) -> List[Document]:
        """List documents for a policy"""
        return self.db.query(Document).filter(Document.policy_id == policy_id).all()

    def delete(self, document_id: int, delete_file: bool = False) -> bool:
        """Delete document"""
        document = self.get_by_id(document_id)
        if not document:
            return False

        # Delete file if requested
        if delete_file:
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")

        # Delete from database
        self.db.delete(document)
        self.db.commit()

        logger.info(f"Deleted document: {document.file_name}")
        return True

    def count(self) -> int:
        """Count total documents"""
        return self.db.query(Document).count()

    def add_user_document(
        self,
        path: str,
        insurer: Optional[str] = None,
        product: Optional[str] = None,
        auto_extract: bool = True
    ) -> int:
        """
        Add a user document (from file path or URL)

        Args:
            path: File path or URL
            insurer: Insurer name (optional, will be extracted if not provided)
            product: Product name (optional, will be extracted if not provided)
            auto_extract: Whether to auto-extract metadata using LLM

        Returns:
            Document ID
        """
        # Check if URL
        if path.startswith("http"):
            # Download the file
            save_path = self._download_document(path)
        else:
            # Copy to user_uploads
            source_path = Path(path)
            if not source_path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            save_path = Config.DOCUMENTS_DIR / "user_uploads" / source_path.name
            shutil.copy(source_path, save_path)

        # Create document
        doc_data = DocumentCreate(
            insurer_name=insurer or "User Uploaded",
            product_name=product,
            document_type="policy_wording",
            file_path=str(save_path),
            is_user_uploaded=True
        )

        document = self.create(doc_data)

        # Auto-extract metadata if requested
        if auto_extract and not insurer:
            # This would call extraction_service to extract metadata
            logger.info(f"Auto-extraction enabled for document {document.id}")
            # TODO: Call extraction service

        return document.id

    def _download_document(self, url: str) -> Path:
        """Download document from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Generate filename from URL
            filename = url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"

            save_path = Config.DOCUMENTS_DIR / "user_uploads" / filename

            # Save file
            save_path.write_bytes(response.content)

            logger.info(f"Downloaded document from {url}")
            return save_path

        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            raise

    def get_text(
        self,
        document_id: str,
        page_start: Optional[int] = None,
        page_end: Optional[int] = None
    ) -> str:
        """Get document text"""
        # Handle both ID and name
        if document_id.isdigit():
            document = self.get_by_id(int(document_id))
        else:
            # Search by filename
            document = self.db.query(Document).filter(
                Document.file_name.ilike(f"%{document_id}%")
            ).first()

        if not document:
            return ""

        # If page range specified, extract specific pages
        if page_start or page_end:
            pdf_path = Path(document.file_path)
            return self.pdf_processor.extract_text_by_page(
                pdf_path, page_start or 1, page_end
            )

        # Return full text
        return document.full_text or ""

    def search(
        self,
        query: str,
        policy_id: Optional[str] = None,
        section: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search across documents

        Args:
            query: Search query
            policy_id: Filter by policy ID
            section: Filter by section

        Returns:
            List of search results
        """
        results = []

        # Base query
        documents = self.db.query(Document)

        # Filter by policy if specified
        if policy_id:
            if policy_id.isdigit():
                documents = documents.filter(Document.policy_id == int(policy_id))
            else:
                # Search by product name
                documents = documents.filter(
                    Document.product_name.ilike(f"%{policy_id}%")
                )

        documents = documents.all()

        # Search in each document
        for doc in documents:
            if not doc.full_text:
                continue

            # Simple text search (case-insensitive)
            text_lower = doc.full_text.lower()
            query_lower = query.lower()

            if query_lower in text_lower:
                # Find context around match
                index = text_lower.find(query_lower)
                start = max(0, index - 200)
                end = min(len(text_lower), index + 200)
                context = doc.full_text[start:end]

                # Extract page number (rough estimate)
                page_num = doc.full_text[:index].count("--- Page") + 1

                results.append({
                    "document_id": doc.id,
                    "policy_name": doc.product_name,
                    "insurer": doc.insurer_name,
                    "section": section or "general",
                    "matched_text": context,
                    "page_number": page_num
                })

        logger.info(f"Found {len(results)} matches for query: {query}")
        return results

    def extract_section(self, policy_id: str, section_name: str) -> str:
        """
        Extract specific section from policy document

        Args:
            policy_id: Policy ID or name
            section_name: Section to extract (exclusions, coverage, etc.)

        Returns:
            Extracted section text
        """
        # Get documents for this policy
        if policy_id.isdigit():
            documents = self.list_by_policy(int(policy_id))
        else:
            documents = self.db.query(Document).filter(
                Document.product_name.ilike(f"%{policy_id}%")
            ).all()

        if not documents:
            return f"No documents found for policy: {policy_id}"

        # Search for section in documents
        section_keywords = {
            "exclusions": ["exclusion", "not covered", "not payable"],
            "coverage": ["coverage", "covered", "benefits", "what is covered"],
            "waiting_periods": ["waiting period", "waiting time"],
            "premiums": ["premium", "rate", "cost"],
            "claims": ["claim", "claim process", "how to claim"],
            "definitions": ["definition", "meaning", "terms"]
        }

        keywords = section_keywords.get(section_name.lower(), [section_name])

        extracted_text = ""
        for doc in documents:
            if not doc.full_text:
                continue

            # Split into sections
            lines = doc.full_text.split('\n')
            capturing = False
            section_lines = []

            for i, line in enumerate(lines):
                line_lower = line.lower()

                # Check if this line starts a relevant section
                if any(keyword in line_lower for keyword in keywords):
                    capturing = True
                    section_lines = [line]
                    continue

                # If capturing, add lines until we hit a new section
                if capturing:
                    # Stop if we hit a new major section
                    if line.isupper() and len(line) > 10:
                        break

                    section_lines.append(line)

                    # Stop after reasonable amount of text
                    if len(section_lines) > 100:
                        break

            if section_lines:
                extracted_text += '\n'.join(section_lines) + '\n\n'

        return extracted_text or f"Section '{section_name}' not found in policy documents"
