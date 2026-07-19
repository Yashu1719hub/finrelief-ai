"""Pydantic schemas used by the FastAPI routes for request/response validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    monthly_income: float


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    monthly_income: float
    created_at: datetime

    class Config:
        from_attributes = True


class LoanProfileCreate(BaseModel):
    user_id: int
    lender_name: str
    loan_type: str
    outstanding_amount: float
    emi_amount: float
    overdue_duration_months: int = 0
    interest_rate: Optional[float] = None


class LoanProfileOut(BaseModel):
    id: int
    user_id: int
    lender_name: str
    loan_type: str
    outstanding_amount: float
    emi_amount: float
    overdue_duration_months: int
    interest_rate: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class NegotiationLetterRequest(BaseModel):
    loan_id: int
    tone: Optional[str] = "professional"  # professional, firm, empathetic


class SettlementResponse(BaseModel):
    loan_id: int
    emi_to_income_ratio: float
    financial_stress_level: str
    recommended_settlement_percentage: str
    recommendation: str
    financial_health_insight: str


class NegotiationLetterResponse(BaseModel):
    loan_id: int
    letter: str
