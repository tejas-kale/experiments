"""Basic tests for the health insurance CLI"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_db, get_db
from services.policy_service import PolicyService
from services.document_service import DocumentService


def test_database_initialization():
    """Test that database can be initialized"""
    print("Testing database initialization...")
    db = init_db()
    assert db is not None
    print("✓ Database initialized")


def test_policy_service():
    """Test policy service basic operations"""
    print("\nTesting policy service...")
    db = get_db()
    service = PolicyService(db)
    
    # Test creating a policy
    policy = service.create(
        insurer_name="Test Insurer",
        product_name="Test Product",
        uin_number="TEST123",
        min_sum_insured=100000,
        max_sum_insured=1000000
    )
    
    assert policy.id is not None
    assert policy.product_name == "Test Product"
    print("✓ Policy created")
    
    # Test retrieving policy
    retrieved = service.get_by_id(policy.id)
    assert retrieved is not None
    assert retrieved.product_name == "Test Product"
    print("✓ Policy retrieved")
    
    # Test listing policies
    policies = service.list_all()
    assert len(policies) > 0
    print(f"✓ Listed {len(policies)} policies")
    
    # Test count
    count = service.count()
    assert count > 0
    print(f"✓ Policy count: {count}")


def test_document_service():
    """Test document service basic operations"""
    print("\nTesting document service...")
    db = get_db()
    service = DocumentService(db)
    
    # Test creating a document
    doc = service.create(
        insurer_name="Test Insurer",
        product_name="Test Product",
        document_type="test",
        file_path="/tmp/test.pdf",
        file_name="test.pdf",
        page_count=1,
        full_text="This is test content",
        is_user_upload=False
    )
    
    assert doc.id is not None
    assert doc.product_name == "Test Product"
    print("✓ Document created")
    
    # Test retrieving document
    retrieved = service.get_by_id(doc.id)
    assert retrieved is not None
    print("✓ Document retrieved")
    
    # Test listing documents
    documents = service.list_all()
    assert len(documents) > 0
    print(f"✓ Listed {len(documents)} documents")
    
    # Test search
    results = service.search("test")
    print(f"✓ Search returned {len(results)} results")


def test_tools():
    """Test agent tools"""
    print("\nTesting agent tools...")
    from agents.tools import (
        list_all_policies,
        get_policy_details,
        search_policy_document
    )
    
    # Test list_all_policies
    result = list_all_policies()
    assert "count" in result
    assert "policies" in result
    print(f"✓ list_all_policies returned {result['count']} policies")
    
    # Test search (with empty results is ok)
    result = search_policy_document("test query")
    assert "query" in result
    assert "results_count" in result
    print(f"✓ search_policy_document returned {result['results_count']} results")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Health Insurance CLI Tests")
    print("=" * 60)
    
    try:
        test_database_initialization()
        test_policy_service()
        test_document_service()
        test_tools()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
