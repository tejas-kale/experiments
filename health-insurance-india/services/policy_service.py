"""Policy service for CRUD operations"""

from sqlalchemy.orm import Session
from typing import List, Optional
from models.database import Policy
from models.schemas import PolicyCreate
from utils.logger import get_logger

logger = get_logger(__name__)


class PolicyService:
    """Service for policy operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, policy_data: PolicyCreate) -> Policy:
        """Create a new policy"""
        policy = Policy(**policy_data.model_dump())
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)

        logger.info(f"Created policy: {policy.product_name} ({policy.insurer_name})")
        return policy

    def get_by_id(self, policy_id: int) -> Optional[Policy]:
        """Get policy by ID"""
        return self.db.query(Policy).filter(Policy.id == policy_id).first()

    def get_by_uin(self, uin: str) -> Optional[Policy]:
        """Get policy by UIN number"""
        return self.db.query(Policy).filter(Policy.uin_number == uin).first()

    def get_by_name(self, product_name: str) -> Optional[Policy]:
        """Get policy by product name (case-insensitive partial match)"""
        return self.db.query(Policy).filter(
            Policy.product_name.ilike(f"%{product_name}%")
        ).first()

    def get_by_id_or_name(self, identifier: str) -> Optional[Policy]:
        """Get policy by ID, UIN, or name"""
        # Try ID first
        if identifier.isdigit():
            policy = self.get_by_id(int(identifier))
            if policy:
                return policy

        # Try UIN
        policy = self.get_by_uin(identifier)
        if policy:
            return policy

        # Try name
        return self.get_by_name(identifier)

    def list_all(self) -> List[Policy]:
        """List all policies"""
        return self.db.query(Policy).all()

    def list_by_insurer(self, insurer_name: str) -> List[Policy]:
        """List policies by insurer"""
        return self.db.query(Policy).filter(
            Policy.insurer_name.ilike(f"%{insurer_name}%")
        ).all()

    def update(self, policy_id: int, policy_data: dict) -> Optional[Policy]:
        """Update policy"""
        policy = self.get_by_id(policy_id)
        if not policy:
            return None

        for key, value in policy_data.items():
            if hasattr(policy, key):
                setattr(policy, key, value)

        self.db.commit()
        self.db.refresh(policy)

        logger.info(f"Updated policy: {policy.product_name}")
        return policy

    def delete(self, policy_id: int) -> bool:
        """Delete policy"""
        policy = self.get_by_id(policy_id)
        if not policy:
            return False

        self.db.delete(policy)
        self.db.commit()

        logger.info(f"Deleted policy: {policy.product_name}")
        return True

    def count(self) -> int:
        """Count total policies"""
        return self.db.query(Policy).count()

    def search(self, query: str) -> List[Policy]:
        """Search policies by name or insurer"""
        return self.db.query(Policy).filter(
            (Policy.product_name.ilike(f"%{query}%")) |
            (Policy.insurer_name.ilike(f"%{query}%"))
        ).all()

    def get_by_coverage_range(self, min_sum: int, max_sum: int) -> List[Policy]:
        """Get policies by coverage range"""
        return self.db.query(Policy).filter(
            Policy.min_sum_insured >= min_sum,
            Policy.max_sum_insured <= max_sum
        ).all()

    def get_by_age(self, age: int) -> List[Policy]:
        """Get policies available for specific age"""
        return self.db.query(Policy).filter(
            Policy.min_age <= age,
            Policy.max_age >= age
        ).all()
