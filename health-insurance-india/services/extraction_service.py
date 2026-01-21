"""Extraction service for LLM-based metadata extraction"""

from typing import Dict, Any, Optional
from anthropic import Anthropic
from utils.config import Config
from utils.logger import get_logger
import json

logger = get_logger(__name__)


class ExtractionService:
    """Service for extracting metadata from policy documents using Claude"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL

    def extract_policy_metadata(self, document_text: str, document_name: str = "") -> Dict[str, Any]:
        """
        Extract structured metadata from policy document

        Args:
            document_text: Full text of policy document
            document_name: Name of document for context

        Returns:
            Dictionary containing extracted metadata
        """
        # Truncate text if too long (keep first 50k chars)
        if len(document_text) > 50000:
            document_text = document_text[:50000] + "\n\n[Document truncated...]"

        prompt = f"""Analyze this Indian health insurance policy document and extract key information in a structured format.

Document: {document_name}

Please extract the following information and return it as a JSON object:

{{
    "insurer_name": "Name of insurance company",
    "product_name": "Name of the insurance product",
    "uin_number": "Unique Identification Number (UIN)",
    "policy_type": "individual/family_floater/group/senior_citizen",
    "min_sum_insured": <minimum coverage amount in INR>,
    "max_sum_insured": <maximum coverage amount in INR>,
    "min_age": <minimum age for entry>,
    "max_age": <maximum age for entry>,
    "waiting_periods": {{
        "initial_waiting_period": <days>,
        "pre_existing_disease": <months>,
        "specific_diseases": {{
            "disease_name": <months>
        }}
    }},
    "key_features": [
        "Feature 1",
        "Feature 2"
    ],
    "major_exclusions": [
        "Exclusion 1",
        "Exclusion 2"
    ],
    "optional_covers": [
        "Add-on 1",
        "Add-on 2"
    ],
    "network_hospitals": <number of network hospitals>,
    "key_warnings": [
        "Important warning 1",
        "Important warning 2"
    ],
    "renewable": true/false,
    "cashless_available": true/false,
    "room_rent_limit": "description of room rent limits",
    "co_payment": "description of co-payment requirements",
    "sub_limits": "description of sub-limits"
}}

Document text:
{document_text}

Return ONLY the JSON object, no additional text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to parse JSON
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            metadata = json.loads(response_text.strip())

            logger.info(f"Extracted metadata from {document_name}")
            return metadata

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response_text}")
            return {}

        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return {}

    def summarize_section(self, section_text: str, section_name: str) -> str:
        """
        Generate a summary of a policy section

        Args:
            section_text: Text of the section
            section_name: Name of the section

        Returns:
            Summary text
        """
        prompt = f"""Summarize this section from a health insurance policy in simple, clear language.
Highlight the most important points that a customer should know.

Section: {section_name}

Text:
{section_text}

Provide a concise summary in bullet points."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            summary = response.content[0].text
            logger.info(f"Generated summary for section: {section_name}")
            return summary

        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return ""

    def extract_key_terms(self, document_text: str) -> Dict[str, str]:
        """
        Extract and explain key insurance terms from document

        Args:
            document_text: Document text

        Returns:
            Dictionary of terms and their explanations
        """
        # Truncate if needed
        if len(document_text) > 30000:
            document_text = document_text[:30000]

        prompt = f"""Extract important insurance terms from this policy document and provide simple explanations.

Focus on:
- Medical terms specific to this policy
- Insurance jargon that needs clarification
- Important definitions

Return as JSON:
{{
    "term1": "simple explanation",
    "term2": "simple explanation"
}}

Document:
{document_text}

Return ONLY the JSON object."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = response.content[0].text

            # Parse JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            terms = json.loads(response_text.strip())
            return terms

        except Exception as e:
            logger.error(f"Failed to extract terms: {e}")
            return {}

    def compare_documents(self, doc1_text: str, doc2_text: str, doc1_name: str, doc2_name: str) -> str:
        """
        Compare two policy documents

        Args:
            doc1_text: First document text
            doc2_text: Second document text
            doc1_name: First document name
            doc2_name: Second document name

        Returns:
            Comparison summary
        """
        # Truncate documents
        doc1_text = doc1_text[:20000]
        doc2_text = doc2_text[:20000]

        prompt = f"""Compare these two health insurance policies and highlight key differences.

Policy 1: {doc1_name}
Policy 2: {doc2_name}

Focus on:
- Coverage differences
- Exclusion differences
- Waiting period differences
- Premium/cost differences
- Key advantages of each

Provide a clear, structured comparison.

Policy 1:
{doc1_text}

Policy 2:
{doc2_text}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=3072,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            comparison = response.content[0].text
            logger.info(f"Generated comparison between {doc1_name} and {doc2_name}")
            return comparison

        except Exception as e:
            logger.error(f"Failed to generate comparison: {e}")
            return "Failed to generate comparison"
