"""Tests for FastAPI endpoints"""

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Health Insurance India API"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_list_policies():
    """Test list policies endpoint"""
    response = client.get("/policies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_documents():
    """Test list documents endpoint"""
    response = client.get("/documents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_insurers():
    """Test list insurers endpoint"""
    response = client.get("/insurers")
    assert response.status_code == 200
    assert "insurers" in response.json()


def test_query_endpoint():
    """Test query endpoint"""
    response = client.post(
        "/query",
        json={"query": "What is health insurance?"}
    )
    # May fail if ANTHROPIC_API_KEY not set
    assert response.status_code in [200, 503]
