"""Custom tools for insurance agent"""

from typing import Dict, Any, List, Optional
from models.database import get_db
from services.document_service import DocumentService
from services.policy_service import PolicyService
from utils.logger import get_logger

logger = get_logger(__name__)


def list_all_policies(**kwargs) -> Dict[str, Any]:
    """List all available insurance policies"""
    try:
        db = get_db()
        policy_service = PolicyService(db)
        policies = policy_service.list_all()

        db.close()

        return {
            "success": True,
            "count": len(policies),
            "policies": [
                {
                    "id": p.id,
                    "insurer": p.insurer_name,
                    "product": p.product_name,
                    "uin": p.uin_number,
                    "sum_insured_range": f"₹{p.min_sum_insured:,} - ₹{p.max_sum_insured:,}" if p.min_sum_insured else "N/A",
                    "age_range": f"{p.min_age}-{p.max_age} years" if p.min_age else "N/A"
                }
                for p in policies
            ]
        }
    except Exception as e:
        logger.error(f"Error in list_all_policies: {e}")
        return {"success": False, "error": str(e)}


def search_policy_document(query: str, policy_id: Optional[str] = None, section: Optional[str] = None) -> Dict[str, Any]:
    """
    Search for specific information across policy documents

    Args:
        query: Search query
        policy_id: Optional policy ID or name to search within
        section: Optional section to search in
    """
    try:
        db = get_db()
        doc_service = DocumentService(db)

        results = doc_service.search(query, policy_id, section)

        db.close()

        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "matches": results[:10]  # Limit to top 10 results
        }
    except Exception as e:
        logger.error(f"Error in search_policy_document: {e}")
        return {"success": False, "error": str(e)}


def get_policy_details(policy_id: str) -> Dict[str, Any]:
    """
    Get complete details of a specific policy

    Args:
        policy_id: Policy ID, UIN, or product name
    """
    try:
        db = get_db()
        policy_service = PolicyService(db)

        policy = policy_service.get_by_id_or_name(policy_id)

        db.close()

        if not policy:
            return {
                "success": False,
                "error": f"Policy not found: {policy_id}"
            }

        return {
            "success": True,
            "policy": {
                "id": policy.id,
                "insurer": policy.insurer_name,
                "product": policy.product_name,
                "uin": policy.uin_number,
                "sum_insured": {
                    "min": policy.min_sum_insured,
                    "max": policy.max_sum_insured
                } if policy.min_sum_insured else None,
                "age_eligibility": {
                    "min": policy.min_age,
                    "max": policy.max_age
                } if policy.min_age else None,
                "waiting_periods": policy.waiting_periods,
                "key_features": policy.key_features,
                "major_exclusions": policy.major_exclusions,
                "optional_covers": policy.optional_covers,
                "network_hospitals": policy.network_hospitals,
                "key_warnings": policy.key_warnings,
                "policy_type": policy.policy_type,
                "renewable": policy.renewable,
                "cashless_available": policy.cashless_available
            }
        }
    except Exception as e:
        logger.error(f"Error in get_policy_details: {e}")
        return {"success": False, "error": str(e)}


def extract_section(policy_id: str, section_name: str) -> Dict[str, Any]:
    """
    Extract a specific section from policy document

    Args:
        policy_id: Policy ID or name
        section_name: Section to extract (exclusions, coverage, waiting_periods, premiums, claims, definitions)
    """
    try:
        db = get_db()
        doc_service = DocumentService(db)

        section_text = doc_service.extract_section(policy_id, section_name)

        db.close()

        return {
            "success": True,
            "policy_id": policy_id,
            "section": section_name,
            "content": section_text[:5000]  # Limit to 5000 chars
        }
    except Exception as e:
        logger.error(f"Error in extract_section: {e}")
        return {"success": False, "error": str(e)}


def compare_policies(policy_ids: List[str], comparison_aspects: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compare multiple policies on specific aspects

    Args:
        policy_ids: List of policy IDs or names to compare
        comparison_aspects: Aspects to compare (waiting_periods, exclusions, coverage, etc.)
    """
    try:
        db = get_db()
        policy_service = PolicyService(db)

        policies = []
        for pid in policy_ids:
            policy = policy_service.get_by_id_or_name(pid)
            if policy:
                policies.append(policy)

        if len(policies) < 2:
            db.close()
            return {
                "success": False,
                "error": "Need at least 2 valid policies to compare"
            }

        # Default aspects
        if not comparison_aspects:
            comparison_aspects = ["waiting_periods", "major_exclusions", "key_features", "sum_insured"]

        comparison = {}
        for aspect in comparison_aspects:
            comparison[aspect] = {}
            for policy in policies:
                value = getattr(policy, aspect, None)

                # Format based on type
                if aspect == "sum_insured":
                    comparison[aspect][policy.product_name] = {
                        "min": policy.min_sum_insured,
                        "max": policy.max_sum_insured
                    } if policy.min_sum_insured else "N/A"
                elif isinstance(value, (list, dict)):
                    comparison[aspect][policy.product_name] = value
                else:
                    comparison[aspect][policy.product_name] = str(value) if value else "N/A"

        db.close()

        return {
            "success": True,
            "policies_compared": [p.product_name for p in policies],
            "comparison": comparison
        }
    except Exception as e:
        logger.error(f"Error in compare_policies: {e}")
        return {"success": False, "error": str(e)}


def calculate_premium(
    policy_id: str,
    age: int,
    sum_insured: Optional[int] = None,
    family_members: int = 1
) -> Dict[str, Any]:
    """
    Calculate estimated premium for a policy

    Args:
        policy_id: Policy ID or name
        age: Age of primary member
        sum_insured: Sum insured amount (optional)
        family_members: Number of family members
    """
    try:
        db = get_db()
        policy_service = PolicyService(db)

        policy = policy_service.get_by_id_or_name(policy_id)

        db.close()

        if not policy:
            return {
                "success": False,
                "error": f"Policy not found: {policy_id}"
            }

        # Check age eligibility
        if policy.min_age and age < policy.min_age:
            return {
                "success": False,
                "error": f"Age {age} is below minimum age {policy.min_age} for this policy"
            }

        if policy.max_age and age > policy.max_age:
            return {
                "success": False,
                "error": f"Age {age} is above maximum age {policy.max_age} for this policy"
            }

        # Use policy's minimum sum insured if not provided
        si = sum_insured or policy.min_sum_insured or 500000

        # Simplified premium calculation (replace with actual rate cards)
        # Base premium increases with age
        if age < 25:
            base = 5000
        elif age < 35:
            base = 7000
        elif age < 45:
            base = 10000
        elif age < 55:
            base = 15000
        elif age < 65:
            base = 25000
        else:
            base = 40000

        # Sum insured factor
        si_factor = si / 500000

        # Family discount
        family_discount = 1.0
        if family_members == 2:
            family_discount = 0.85
        elif family_members >= 3:
            family_discount = 0.75

        estimated = base * si_factor * family_discount

        return {
            "success": True,
            "policy": policy.product_name,
            "estimated_annual_premium": round(estimated, 2),
            "breakdown": {
                "base_premium": base,
                "sum_insured_factor": round(si_factor, 2),
                "family_discount": f"{int((1 - family_discount) * 100)}%"
            },
            "factors": {
                "age": age,
                "sum_insured": si,
                "family_members": family_members
            },
            "disclaimer": "This is an estimated premium. Actual premium depends on medical history, pre-existing conditions, location, and other factors. Please contact the insurer for accurate quote."
        }
    except Exception as e:
        logger.error(f"Error in calculate_premium: {e}")
        return {"success": False, "error": str(e)}


def get_document_text(
    document_id: str,
    page_start: Optional[int] = None,
    page_end: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get full text or specific pages from a document

    Args:
        document_id: Document ID or filename
        page_start: Starting page (optional)
        page_end: Ending page (optional)
    """
    try:
        db = get_db()
        doc_service = DocumentService(db)

        text = doc_service.get_text(document_id, page_start, page_end)

        db.close()

        if not text:
            return {
                "success": False,
                "error": f"Document not found or no text available: {document_id}"
            }

        # Limit text length
        if len(text) > 10000:
            text = text[:10000] + "\n\n[Text truncated for length...]"

        page_range = "all"
        if page_start:
            page_range = f"{page_start}-{page_end or 'end'}"

        return {
            "success": True,
            "document_id": document_id,
            "pages": page_range,
            "text": text
        }
    except Exception as e:
        logger.error(f"Error in get_document_text: {e}")
        return {"success": False, "error": str(e)}


# Tool definitions for Anthropic API
TOOL_DEFINITIONS = [
    {
        "name": "list_all_policies",
        "description": "Lists all available insurance policies in the database with basic information like insurer name, product name, UIN, and coverage ranges",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "search_policy_document",
        "description": "Search for specific information across all policy documents using keywords. Returns matching text with context and page numbers.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query or keywords to find in policy documents"
                },
                "policy_id": {
                    "type": "string",
                    "description": "Optional: specific policy ID or name to search within"
                },
                "section": {
                    "type": "string",
                    "description": "Optional: specific section to search (exclusions, coverage, etc.)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_policy_details",
        "description": "Get complete structured details of a specific policy including coverage, exclusions, waiting periods, features, and warnings",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_id": {
                    "type": "string",
                    "description": "Policy ID, UIN number, or product name"
                }
            },
            "required": ["policy_id"]
        }
    },
    {
        "name": "extract_section",
        "description": "Extract a specific section from a policy document (like exclusions, coverage, waiting periods, premiums, claims, or definitions)",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_id": {
                    "type": "string",
                    "description": "Policy ID or product name"
                },
                "section_name": {
                    "type": "string",
                    "description": "Section to extract",
                    "enum": ["exclusions", "coverage", "waiting_periods", "premiums", "claims", "definitions"]
                }
            },
            "required": ["policy_id", "section_name"]
        }
    },
    {
        "name": "compare_policies",
        "description": "Compare multiple policies side-by-side on specific aspects like waiting periods, exclusions, coverage, and sum insured",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of policy IDs or names to compare (minimum 2)"
                },
                "comparison_aspects": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: specific aspects to compare (e.g., waiting_periods, major_exclusions, key_features)"
                }
            },
            "required": ["policy_ids"]
        }
    },
    {
        "name": "calculate_premium",
        "description": "Calculate estimated annual premium for a policy based on age, sum insured, and family size. Returns estimated premium with breakdown.",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_id": {
                    "type": "string",
                    "description": "Policy ID or name"
                },
                "age": {
                    "type": "integer",
                    "description": "Age of primary insured member"
                },
                "sum_insured": {
                    "type": "integer",
                    "description": "Optional: desired sum insured amount in INR"
                },
                "family_members": {
                    "type": "integer",
                    "description": "Number of family members to cover (default: 1)"
                }
            },
            "required": ["policy_id", "age"]
        }
    },
    {
        "name": "get_document_text",
        "description": "Get full text or specific pages from a policy document. Useful for detailed review of specific sections.",
        "input_schema": {
            "type": "object",
            "properties": {
                "document_id": {
                    "type": "string",
                    "description": "Document ID or filename"
                },
                "page_start": {
                    "type": "integer",
                    "description": "Optional: starting page number"
                },
                "page_end": {
                    "type": "integer",
                    "description": "Optional: ending page number"
                }
            },
            "required": ["document_id"]
        }
    }
]


# Map tool names to functions
TOOL_FUNCTIONS = {
    "list_all_policies": list_all_policies,
    "search_policy_document": search_policy_document,
    "get_policy_details": get_policy_details,
    "extract_section": extract_section,
    "compare_policies": compare_policies,
    "calculate_premium": calculate_premium,
    "get_document_text": get_document_text
}
