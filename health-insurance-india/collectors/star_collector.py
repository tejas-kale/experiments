"""Star Health collector"""

from typing import List, Dict
from collectors.base_collector import BaseCollector


class StarCollector(BaseCollector):
    """Collector for Star Health Insurance"""

    def get_insurer_name(self) -> str:
        return "Star Health"

    def get_base_url(self) -> str:
        return "https://www.starhealth.in"

    def find_policy_urls(self) -> List[Dict[str, str]]:
        """Find Star Health policy documents"""

        policies = [
            {
                'url': 'https://www.starhealth.in/sites/default/files/Star-Comprehensive-Insurance-Policy-Wording.pdf',
                'product': 'Star Comprehensive Insurance Policy',
                'type': 'policy_wording',
                'filename': 'star_comprehensive_policy_wording.pdf'
            },
            {
                'url': 'https://www.starhealth.in/sites/default/files/Young-Star-Insurance-Policy-Wording.pdf',
                'product': 'Young Star Insurance Policy',
                'type': 'policy_wording',
                'filename': 'young_star_policy_wording.pdf'
            },
            {
                'url': 'https://www.starhealth.in/sites/default/files/Senior-Citizens-Red-Carpet-Health-Insurance-Policy-Wording.pdf',
                'product': 'Senior Citizens Red Carpet',
                'type': 'policy_wording',
                'filename': 'senior_citizens_red_carpet_policy_wording.pdf'
            }
        ]

        try:
            self.logger.info("Fetching from Star Health website...")

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
