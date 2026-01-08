"""Policy service for managing insurance policies"""

from typing import List, Optional
from sqlalchemy.orm import Session
from models.database import Policy


class PolicyService:
    """Service for policy operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def list_all(self) -> List[Policy]:
        """List all policies"""
        return self.db.query(Policy).all()
    
    def get_by_id(self, policy_id: int) -> Optional[Policy]:
        """Get policy by ID"""
        return self.db.query(Policy).filter(Policy.id == policy_id).first()
    
    def get_by_uin(self, uin: str) -> Optional[Policy]:
        """Get policy by UIN number"""
        return self.db.query(Policy).filter(Policy.uin_number == uin).first()
    
    def get_by_name(self, name: str) -> Optional[Policy]:
        """Get policy by product name (case-insensitive partial match)"""
        return self.db.query(Policy).filter(
            Policy.product_name.ilike(f"%{name}%")
        ).first()
    
    def get_by_id_or_name(self, identifier: str) -> Optional[Policy]:
        """Get policy by ID, UIN, or name"""
        # Try ID first
        try:
            policy_id = int(identifier)
            policy = self.get_by_id(policy_id)
            if policy:
                return policy
        except ValueError:
            pass
        
        # Try UIN
        policy = self.get_by_uin(identifier)
        if policy:
            return policy
        
        # Try name
        return self.get_by_name(identifier)
    
    def create(self, **kwargs) -> Policy:
        """Create new policy"""
        policy = Policy(**kwargs)
        self.db.add(policy)
        self.db.commit()
        self.db.refresh(policy)
        return policy
    
    def update(self, policy_id: int, **kwargs) -> Optional[Policy]:
        """Update policy"""
        policy = self.get_by_id(policy_id)
        if policy:
            for key, value in kwargs.items():
                setattr(policy, key, value)
            self.db.commit()
            self.db.refresh(policy)
        return policy
    
    def delete(self, policy_id: int) -> bool:
        """Delete policy"""
        policy = self.get_by_id(policy_id)
        if policy:
            self.db.delete(policy)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """Count total policies"""
        return self.db.query(Policy).count()
