"""SBI General Insurance collector"""

from typing import List, Dict
from collectors.base_collector import BaseCollector


class SBICollector(BaseCollector):
    """Collector for SBI General Insurance"""

    def get_insurer_name(self) -> str:
        return "SBI General"

    def get_base_url(self) -> str:
        return "https://www.sbigeneral.in"

    def find_policy_urls(self) -> List[Dict[str, str]]:
        """
        Find SBI health insurance policy documents

        Returns:
            List of policy document metadata
        """
        # In a real implementation, this would scrape the SBI website
        # For now, returning known policy document URLs
        policies = [
            {
                'url': 'https://www.sbigeneral.in/portal/documents/policy-wording/health/Arogya_Premier_Policy_Wording.pdf',
                'product': 'Arogya Premier',
                'type': 'policy_wording',
                'filename': 'arogya_premier_policy_wording.pdf'
            },
            {
                'url': 'https://www.sbigeneral.in/portal/documents/policy-wording/health/Arogya_Supreme_Policy_Wording.pdf',
                'product': 'Arogya Supreme',
                'type': 'policy_wording',
                'filename': 'arogya_supreme_policy_wording.pdf'
            },
            {
                'url': 'https://www.sbigeneral.in/portal/documents/brochures/health/Arogya_Premier_Brochure.pdf',
                'product': 'Arogya Premier',
                'type': 'brochure',
                'filename': 'arogya_premier_brochure.pdf'
            }
        ]

        # Try to fetch from website dynamically
        try:
            self.logger.info("Attempting to fetch policy documents from SBI website...")

            # Fetch health insurance page
            soup = self.fetch_page(f"{self.get_base_url()}/health-insurance")

            if soup:
                # Look for PDF links
                pdf_links = soup.find_all('a', href=lambda x: x and '.pdf' in x.lower())

                for link in pdf_links:
                    href = link.get('href')
                    if not href:
                        continue

                    # Make absolute URL
                    if href.startswith('/'):
                        href = self.get_base_url() + href
                    elif not href.startswith('http'):
                        continue

                    # Extract product name from link text or URL
                    product_name = link.get_text(strip=True) or href.split('/')[-1].replace('.pdf', '')

                    # Determine document type
                    doc_type = 'brochure' if 'brochure' in href.lower() else 'policy_wording'

                    # Create filename
                    filename = href.split('/')[-1]

                    # Add if not already in list
                    if not any(p['url'] == href for p in policies):
                        policies.append({
                            'url': href,
                            'product': product_name,
                            'type': doc_type,
                            'filename': filename
                        })

                self.logger.info(f"Found {len(policies)} policy documents")

        except Exception as e:
            self.logger.warning(f"Could not fetch from website dynamically: {e}")
            self.logger.info("Using predefined policy list")

        return policies
