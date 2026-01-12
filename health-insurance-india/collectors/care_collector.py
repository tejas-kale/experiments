"""Care Health collector"""

from typing import List, Dict
from collectors.base_collector import BaseCollector


class CareCollector(BaseCollector):
    """Collector for Care Health Insurance (formerly Religare)"""

    def get_insurer_name(self) -> str:
        return "Care Health"

    def get_base_url(self) -> str:
        return "https://www.careinsurance.com"

    def find_policy_urls(self) -> List[Dict[str, str]]:
        """Find Care Health policy documents"""

        policies = [
            {
                'url': 'https://www.careinsurance.com/upload/ProductBrochure/Care_Advantage_Policy_Wordings.pdf',
                'product': 'Care Advantage',
                'type': 'policy_wording',
                'filename': 'care_advantage_policy_wording.pdf'
            },
            {
                'url': 'https://www.careinsurance.com/upload/ProductBrochure/Care_Supreme_Policy_Wording.pdf',
                'product': 'Care Supreme',
                'type': 'policy_wording',
                'filename': 'care_supreme_policy_wording.pdf'
            },
            {
                'url': 'https://www.careinsurance.com/upload/ProductBrochure/Care_Freedom_Policy_Wording.pdf',
                'product': 'Care Freedom',
                'type': 'policy_wording',
                'filename': 'care_freedom_policy_wording.pdf'
            }
        ]

        try:
            self.logger.info("Fetching from Care Health website...")

            soup = self.fetch_page(f"{self.get_base_url()}/health-insurance-plans")

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
