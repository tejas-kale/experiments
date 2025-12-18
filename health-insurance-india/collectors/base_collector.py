"""Base collector for insurance document collection"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import time
from utils.logger import get_logger
from utils.config import Config
from utils.pdf_utils import PDFProcessor

logger = get_logger(__name__)


class BaseCollector(ABC):
    """Abstract base class for insurance document collectors"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.pdf_processor = PDFProcessor()

    @abstractmethod
    def get_insurer_name(self) -> str:
        """Return insurer name"""
        pass

    @abstractmethod
    def get_base_url(self) -> str:
        """Return insurer's base URL"""
        pass

    @abstractmethod
    def find_policy_urls(self) -> List[Dict[str, str]]:
        """
        Find all policy document URLs

        Returns:
            List of dicts with 'url', 'product', 'type', 'filename'
        """
        pass

    def download_pdf(self, url: str, save_path: Path) -> bool:
        """
        Download PDF file

        Args:
            url: PDF URL
            save_path: Path to save file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Downloading: {url}")

            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Check if content is PDF
            content_type = response.headers.get('content-type', '')
            if 'pdf' not in content_type.lower() and not url.endswith('.pdf'):
                self.logger.warning(f"URL may not be PDF: {url} (Content-Type: {content_type})")

            # Save file
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(response.content)

            # Validate PDF
            if not self.pdf_processor.validate_pdf(save_path):
                self.logger.error(f"Downloaded file is not a valid PDF: {save_path}")
                save_path.unlink()
                return False

            self.logger.info(f"Downloaded: {save_path.name} ({len(response.content)} bytes)")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False

        except Exception as e:
            self.logger.error(f"Error downloading {url}: {e}")
            return False

    def extract_text(self, pdf_path: Path) -> str:
        """
        Extract text from PDF

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        return self.pdf_processor.extract_text(pdf_path)

    def collect(self) -> List[Dict]:
        """
        Main collection method

        Returns:
            List of collected documents with metadata
        """
        self.logger.info(f"Starting collection for {self.get_insurer_name()}")

        # Find policy URLs
        policy_urls = self.find_policy_urls()
        self.logger.info(f"Found {len(policy_urls)} documents")

        # Download and process
        collected = []
        for i, policy in enumerate(policy_urls, 1):
            self.logger.info(f"Processing {i}/{len(policy_urls)}: {policy.get('product', 'Unknown')}")

            # Create save path
            insurer_dir = Config.DOCUMENTS_DIR / self.get_insurer_name().lower().replace(' ', '_')
            save_path = insurer_dir / policy['filename']

            # Skip if already exists
            if save_path.exists():
                self.logger.info(f"Already exists, skipping: {save_path.name}")

                # Still add to collected list
                collected.append({
                    'insurer': self.get_insurer_name(),
                    'product': policy.get('product', 'Unknown'),
                    'document_type': policy.get('type', 'policy_wording'),
                    'file_path': str(save_path),
                    'source_url': policy['url'],
                    'text': None  # Don't re-extract
                })
                continue

            # Download PDF
            if self.download_pdf(policy['url'], save_path):
                # Extract text
                text = self.extract_text(save_path)

                collected.append({
                    'insurer': self.get_insurer_name(),
                    'product': policy.get('product', 'Unknown'),
                    'document_type': policy.get('type', 'policy_wording'),
                    'file_path': str(save_path),
                    'source_url': policy['url'],
                    'text': text
                })

                # Rate limiting
                time.sleep(1)

        self.logger.info(f"Collection complete: {len(collected)} documents")
        return collected

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a web page

        Args:
            url: URL to fetch

        Returns:
            BeautifulSoup object or None
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            return BeautifulSoup(response.content, 'lxml')

        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None


class CollectorFactory:
    """Factory to create collectors for different insurers"""

    @staticmethod
    def create(insurer_name: str) -> BaseCollector:
        """
        Create collector for specific insurer

        Args:
            insurer_name: Insurer name (case-insensitive)

        Returns:
            Collector instance

        Raises:
            ValueError: If insurer not supported
        """
        from collectors.sbi_collector import SBICollector
        from collectors.hdfc_collector import HDFCCollector
        from collectors.icici_collector import ICICICollector
        from collectors.star_collector import StarCollector
        from collectors.care_collector import CareCollector

        collectors = {
            'sbi': SBICollector,
            'sbi_general': SBICollector,
            'hdfc': HDFCCollector,
            'hdfc_ergo': HDFCCollector,
            'icici': ICICICollector,
            'icici_lombard': ICICICollector,
            'star': StarCollector,
            'star_health': StarCollector,
            'care': CareCollector,
            'care_health': CareCollector,
        }

        collector_class = collectors.get(insurer_name.lower())
        if not collector_class:
            raise ValueError(f"No collector for: {insurer_name}")

        return collector_class()

    @staticmethod
    def list_all() -> List[str]:
        """List all supported insurers"""
        return [
            'sbi_general',
            'hdfc_ergo',
            'icici_lombard',
            'star_health',
            'care_health'
        ]
