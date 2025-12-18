"""Agent tools for querying insurance policies"""

from models.database import get_db
from services.document_service import DocumentService
from services.policy_service import PolicyService
import json


def list_all_policies() -> dict:
    """List all available policies"""
    db = get_db()
    policies = PolicyService(db).list_all()
    
    return {
        "count": len(policies),
        "policies": [
            {
                "id": p.id,
                "insurer": p.insurer_name,
                "product": p.product_name,
                "uin": p.uin_number,
                "sum_insured_range": f"₹{(p.min_sum_insured or 0)/100000}L - ₹{(p.max_sum_insured or 0)/100000}L"
            }
            for p in policies
        ]
    }


def search_policy_document(query: str, policy_id: str = None, section: str = None) -> dict:
    """Search across policy documents"""
    db = get_db()
    doc_service = DocumentService(db)
    
    # Search in document text
    results = doc_service.search(query, policy_id, section)
    
    return {
        "query": query,
        "results_count": len(results),
        "matches": results
    }


def get_policy_details(policy_id: str) -> dict:
    """Get complete policy details"""
    db = get_db()
    policy = PolicyService(db).get_by_id_or_name(policy_id)
    
    if not policy:
        return {"error": f"Policy not found: {policy_id}"}
    
    return {
        "id": policy.id,
        "insurer": policy.insurer_name,
        "product": policy.product_name,
        "uin": policy.uin_number,
        "sum_insured": {
            "min": policy.min_sum_insured,
            "max": policy.max_sum_insured
        },
        "age_eligibility": {
            "min": policy.min_age,
            "max": policy.max_age
        },
        "waiting_periods": policy.waiting_periods,
        "key_features": policy.key_features,
        "major_exclusions": policy.major_exclusions,
        "optional_covers": policy.optional_covers,
        "network_hospitals": policy.network_hospitals,
        "warnings": policy.key_warnings
    }


def extract_section(policy_id: str, section_name: str) -> dict:
    """Extract specific section from policy"""
    db = get_db()
    doc_service = DocumentService(db)
    
    section_text = doc_service.extract_section(policy_id, section_name)
    
    return {
        "policy_id": policy_id,
        "section": section_name,
        "content": section_text
    }


def compare_policies(policy_ids: list, comparison_aspects: list = None) -> dict:
    """Compare multiple policies"""
    db = get_db()
    policy_service = PolicyService(db)
    
    policies = [policy_service.get_by_id_or_name(pid) for pid in policy_ids]
    
    if not comparison_aspects:
        comparison_aspects = ["waiting_periods", "major_exclusions", "key_features"]
    
    comparison = {}
    for aspect in comparison_aspects:
        comparison[aspect] = {}
        for policy in policies:
            if policy:
                comparison[aspect][policy.product_name] = getattr(policy, aspect, "N/A")
    
    return {
        "policies_compared": [p.product_name for p in policies if p],
        "aspects": comparison
    }


def calculate_premium(
    policy_id: str, 
    age: int, 
    sum_insured: int = None, 
    family_members: int = 1
) -> dict:
    """Calculate estimated premium"""
    db = get_db()
    policy = PolicyService(db).get_by_id_or_name(policy_id)
    
    if not policy:
        return {"error": f"Policy not found: {policy_id}"}
    
    # Simplified calculation (replace with actual logic)
    base_premium = 5000
    age_factor = 1 + (age - 30) * 0.05
    si_factor = (sum_insured or policy.min_sum_insured or 500000) / 500000
    family_factor = family_members * 0.8
    
    estimated_premium = base_premium * age_factor * si_factor * family_factor
    
    return {
        "policy": policy.product_name,
        "estimated_annual_premium": round(estimated_premium, 2),
        "factors": {
            "age": age,
            "sum_insured": sum_insured or policy.min_sum_insured,
            "family_members": family_members
        },
        "note": "This is an estimate. Actual premium may vary based on medical history and other factors."
    }


def get_document_text(
    document_id: str, 
    page_start: int = None, 
    page_end: int = None
) -> dict:
    """Get document text"""
    db = get_db()
    doc_service = DocumentService(db)
    
    text = doc_service.get_text(document_id, page_start, page_end)
    
    return {
        "document_id": document_id,
        "pages": f"{page_start or 1}-{page_end or 'end'}",
        "text": text
    }
