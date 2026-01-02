"""PDF processing utilities"""

import fitz  # PyMuPDF
import pdfplumber
from pathlib import Path
from typing import Optional, Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)

class PDFProcessor:
    """Handle PDF operations"""

    @staticmethod
    def extract_text(pdf_path: Path) -> str:
        """
        Extract all text from PDF using PyMuPDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""

            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                text += f"\n--- Page {page_num} ---\n"
                text += page_text

            doc.close()
            logger.info(f"Extracted text from {pdf_path.name} ({doc.page_count} pages)")
            return text

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""

    @staticmethod
    def extract_text_by_page(pdf_path: Path, page_start: int = 1, page_end: Optional[int] = None) -> str:
        """
        Extract text from specific page range

        Args:
            pdf_path: Path to PDF file
            page_start: Starting page (1-indexed)
            page_end: Ending page (inclusive, None for last page)

        Returns:
            Extracted text from specified pages
        """
        try:
            doc = fitz.open(pdf_path)

            if page_end is None:
                page_end = doc.page_count

            # Convert to 0-indexed
            page_start = max(0, page_start - 1)
            page_end = min(doc.page_count, page_end)

            text = ""
            for page_num in range(page_start, page_end):
                page = doc[page_num]
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page.get_text()

            doc.close()
            return text

        except Exception as e:
            logger.error(f"Failed to extract pages {page_start}-{page_end} from {pdf_path}: {e}")
            return ""

    @staticmethod
    def get_metadata(pdf_path: Path) -> Dict:
        """
        Extract PDF metadata

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary containing metadata
        """
        try:
            doc = fitz.open(pdf_path)

            metadata = {
                "page_count": doc.page_count,
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
            }

            doc.close()
            return metadata

        except Exception as e:
            logger.error(f"Failed to extract metadata from {pdf_path}: {e}")
            return {}

    @staticmethod
    def extract_tables(pdf_path: Path, page_num: Optional[int] = None) -> List[List[List[str]]]:
        """
        Extract tables from PDF using pdfplumber

        Args:
            pdf_path: Path to PDF file
            page_num: Specific page number (1-indexed), None for all pages

        Returns:
            List of tables (each table is a list of rows, each row is a list of cells)
        """
        try:
            tables = []

            with pdfplumber.open(pdf_path) as pdf:
                if page_num:
                    # Extract from specific page
                    page = pdf.pages[page_num - 1]
                    page_tables = page.extract_tables()
                    tables.extend(page_tables)
                else:
                    # Extract from all pages
                    for page in pdf.pages:
                        page_tables = page.extract_tables()
                        if page_tables:
                            tables.extend(page_tables)

            logger.info(f"Extracted {len(tables)} tables from {pdf_path.name}")
            return tables

        except Exception as e:
            logger.error(f"Failed to extract tables from {pdf_path}: {e}")
            return []

    @staticmethod
    def search_text(pdf_path: Path, query: str) -> List[Dict]:
        """
        Search for text in PDF

        Args:
            pdf_path: Path to PDF file
            query: Search query

        Returns:
            List of matches with page numbers and context
        """
        try:
            doc = fitz.open(pdf_path)
            matches = []

            for page_num, page in enumerate(doc, 1):
                text = page.get_text()

                if query.lower() in text.lower():
                    # Find context around match
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            # Get context (3 lines before and after)
                            start = max(0, i - 3)
                            end = min(len(lines), i + 4)
                            context = '\n'.join(lines[start:end])

                            matches.append({
                                "page": page_num,
                                "line": line.strip(),
                                "context": context
                            })

            doc.close()
            logger.info(f"Found {len(matches)} matches for '{query}' in {pdf_path.name}")
            return matches

        except Exception as e:
            logger.error(f"Failed to search in {pdf_path}: {e}")
            return []

    @staticmethod
    def validate_pdf(pdf_path: Path) -> bool:
        """
        Validate if file is a valid PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if valid PDF, False otherwise
        """
        try:
            doc = fitz.open(pdf_path)
            valid = doc.page_count > 0
            doc.close()
            return valid

        except Exception:
            return False

    @staticmethod
    def get_page_count(pdf_path: Path) -> int:
        """Get number of pages in PDF"""
        try:
            doc = fitz.open(pdf_path)
            count = doc.page_count
            doc.close()
            return count

        except Exception:
            return 0
