"""Base collector for insurance document collection"""

from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import PyMuPDF
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)


class BaseCollector(ABC):
    """Abstract base class for insurance document collectors"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
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
        """Find all policy document URLs"""
        pass
    
    def download_pdf(self, url: str, save_path: Path) -> bool:
        """Download PDF file"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(response.content)
            
            self.logger.info(f"Downloaded: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return False
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF"""
        try:
            doc = PyMuPDF.open(str(pdf_path))
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
            
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""
    
    def collect(self) -> List[Dict]:
        """Main collection method"""
        self.logger.info(f"Starting collection for {self.get_insurer_name()}")
        
        # Find URLs
        policy_urls = self.find_policy_urls()
        self.logger.info(f"Found {len(policy_urls)} documents")
        
        # Download and process
        collected = []
        for policy in policy_urls:
            save_path = Path(f"data/documents/{self.get_insurer_name()}/{policy['filename']}")
            
            if self.download_pdf(policy['url'], save_path):
                text = self.extract_text(save_path)
                
                collected.append({
                    'insurer': self.get_insurer_name(),
                    'product': policy.get('product', 'Unknown'),
                    'document_type': policy.get('type', 'policy_wording'),
                    'file_path': str(save_path),
                    'text': text
                })
        
        return collected


class CollectorFactory:
    """Factory to create collectors"""
    
    @staticmethod
    def create(insurer_name: str) -> BaseCollector:
        """Create collector for specific insurer"""
        # Import collectors here to avoid circular imports
        collectors = {}
        
        collector_class = collectors.get(insurer_name.lower())
        if not collector_class:
            raise ValueError(f"No collector for: {insurer_name}")
        
        return collector_class()
    
    @staticmethod
    def list_all() -> List[str]:
        """List all supported insurers"""
        return ['star', 'hdfc', 'icici', 'care', 'bajaj']
