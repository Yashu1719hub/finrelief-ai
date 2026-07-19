"""
Basic test suite for FinRelief AI backend.

Run with:
    pytest test_main.py -v

Covers: user creation, loan profile creation, financial health calculation,
and validation error handling — satisfying the System Testing epic.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _unique_email():
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    assert "message" in res.json()


def test_create_user_success():
    payload = {"name": "Test Borrower", "email": _unique_email(), "monthly_income": 40000}
    res = client.post("/users", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == payload["name"]
    assert data["monthly_income"] == 40000


def test_create_duplicate_user_fails():
    email = _unique_email()
    payload = {"name": "Dup User", "email": email, "monthly_income": 30000}
    first = client.post("/users", json=payload)
    assert first.status_code == 200
    second = client.post("/users", json=payload)
    assert second.status_code == 400


def test_create_loan_profile_and_financial_health():
    user_res = client.post("/users", json={
        "name": "Loan Tester", "email": _unique_email(), "monthly_income": 50000,
    })
    user_id = user_res.json()["id"]

    loan_res = client.post("/loans", json={
        "user_id": user_id,
        "lender_name": "Test Bank",
        "loan_type": "Personal Loan",
        "outstanding_amount": 200000,
        "emi_amount": 15000,
        "overdue_duration_months": 4,
    })
    assert loan_res.status_code == 200
    loan_id = loan_res.json()["id"]

    health_res = client.get(f"/loans/{loan_id}/financial-health")
    assert health_res.status_code == 200
    health = health_res.json()
    assert health["monthly_income"] == 50000
    assert health["emi_to_income_ratio"] == 30.0
    assert health["financial_stress_level"] in ("Low", "Medium", "High")


def test_loan_not_found_returns_404():
    res = client.get("/loans/999999/financial-health")
    assert res.status_code == 404


def test_settlement_recommendation_fallback_without_api_key():
    """Without GEMINI_API_KEY configured, the endpoint should still return a
    valid rule-based recommendation instead of failing (Fallback Logic)."""
    user_res = client.post("/users", json={
        "name": "Fallback Tester", "email": _unique_email(), "monthly_income": 25000,
    })
    user_id = user_res.json()["id"]

    loan_res = client.post("/loans", json={
        "user_id": user_id,
        "lender_name": "Fallback Bank",
        "loan_type": "Credit Card",
        "outstanding_amount": 100000,
        "emi_amount": 18000,
        "overdue_duration_months": 7,
    })
    loan_id = loan_res.json()["id"]

    res = client.get(f"/loans/{loan_id}/settlement")
    assert res.status_code == 200
    data = res.json()
    assert "recommended_settlement_percentage" in data
    assert data["financial_stress_level"] == "High"
