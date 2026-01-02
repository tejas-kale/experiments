"""ICICI Lombard collector"""

from typing import List, Dict
from collectors.base_collector import BaseCollector


class ICICICollector(BaseCollector):
    """Collector for ICICI Lombard Health Insurance"""

    def get_insurer_name(self) -> str:
        return "ICICI Lombard"

    def get_base_url(self) -> str:
        return "https://www.icicilombard.com"

    def find_policy_urls(self) -> List[Dict[str, str]]:
        """Find ICICI Lombard policy documents"""

        policies = [
            {
                'url': 'https://www.icicilombard.com/docs/default-source/health-insurance/complete-health-insurance/complete-health-insurance-policy-wording.pdf',
                'product': 'Complete Health Insurance',
                'type': 'policy_wording',
                'filename': 'complete_health_insurance_policy_wording.pdf'
            },
            {
                'url': 'https://www.icicilombard.com/docs/default-source/health-insurance/health-advantedge/health-advantedge-policy-wording.pdf',
                'product': 'Health AdvantEdge',
                'type': 'policy_wording',
                'filename': 'health_advantedge_policy_wording.pdf'
            }
        ]

        try:
            self.logger.info("Fetching from ICICI Lombard website...")

            soup = self.fetch_page(f"{self.get_base_url()}/health-insurance")

            if soup:
                for link in soup.find_all('a', href=lambda x: x and '.pdf' in x.lower()):
                    href = link.get('href')
                    if not href:
                        continue

                    if href.startswith('/'):
                        href = self.get_base_url() + href
                    elif not href.startswith('http'):
                        continue

                    product_name = link.get_text(strip=True) or 'Unknown Product'
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
