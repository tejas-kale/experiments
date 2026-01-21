"""HDFC ERGO collector"""

from typing import List, Dict
from collectors.base_collector import BaseCollector


class HDFCCollector(BaseCollector):
    """Collector for HDFC ERGO Health Insurance"""

    def get_insurer_name(self) -> str:
        return "HDFC ERGO"

    def get_base_url(self) -> str:
        return "https://www.hdfcergo.com"

    def find_policy_urls(self) -> List[Dict[str, str]]:
        """Find HDFC ERGO policy documents"""

        policies = [
            {
                'url': 'https://www.hdfcergo.com/docs/default-source/health-insurance/my-health-suraksha/my-health-suraksha-gold-policy-wordings.pdf',
                'product': 'My Health Suraksha Gold',
                'type': 'policy_wording',
                'filename': 'my_health_suraksha_gold_policy_wording.pdf'
            },
            {
                'url': 'https://www.hdfcergo.com/docs/default-source/health-insurance/optima-secure/optima-secure-policy-wording.pdf',
                'product': 'Optima Secure',
                'type': 'policy_wording',
                'filename': 'optima_secure_policy_wording.pdf'
            },
            {
                'url': 'https://www.hdfcergo.com/docs/default-source/health-insurance/health-wallet/energy-policy-wording.pdf',
                'product': 'Energy',
                'type': 'policy_wording',
                'filename': 'energy_policy_wording.pdf'
            }
        ]

        # Try dynamic fetch
        try:
            self.logger.info("Attempting to fetch from HDFC ERGO website...")

            soup = self.fetch_page(f"{self.get_base_url()}/health-insurance")

            if soup:
                # Find all PDF links
                for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                    href = link.get('href')
                    if not href:
                        continue

                    # Make absolute URL
                    if href.startswith('/'):
                        href = self.get_base_url() + href
                    elif not href.startswith('http'):
                        continue

                    # Extract product name
                    product_name = link.get_text(strip=True) or href.split('/')[-2].replace('-', ' ').title()

                    # Document type
                    doc_type = 'brochure' if 'brochure' in href.lower() else 'policy_wording'

                    filename = href.split('/')[-1]

                    if not any(p['url'] == href for p in policies):
                        policies.append({
                            'url': href,
                            'product': product_name,
                            'type': doc_type,
                            'filename': filename
                        })

        except Exception as e:
            self.logger.warning(f"Dynamic fetch failed: {e}")

        return policies
