"""
SQLAlchemy ORM models for FinRelief AI.

Entities:
- User: a borrower using the platform
- LoanProfile: a loan/debt record belonging to a user
- NegotiationHistory: AI-generated negotiation letters and settlement
  recommendations tied to a loan profile
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    monthly_income = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loans = relationship("LoanProfile", back_populates="owner", cascade="all, delete-orphan")


class LoanProfile(Base):
    __tablename__ = "loan_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lender_name = Column(String(150), nullable=False)
    loan_type = Column(String(80), nullable=False)  # e.g. Credit Card, Personal Loan
    outstanding_amount = Column(Float, nullable=False)
    emi_amount = Column(Float, nullable=False)
    overdue_duration_months = Column(Integer, nullable=False, default=0)
    interest_rate = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="loans")
    negotiations = relationship("NegotiationHistory", back_populates="loan", cascade="all, delete-orphan")

    # ---- Derived financial health helpers ----
    def emi_to_income_ratio(self, monthly_income: float) -> float:
        if not monthly_income:
            return 0.0
        return round((self.emi_amount / monthly_income) * 100, 2)

    def financial_stress_level(self, monthly_income: float) -> str:
        ratio = self.emi_to_income_ratio(monthly_income)
        if ratio >= 50 or self.overdue_duration_months >= 6:
            return "High"
        if ratio >= 30 or self.overdue_duration_months >= 3:
            return "Medium"
        return "Low"


class NegotiationHistory(Base):
    __tablename__ = "negotiation_history"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loan_profiles.id"), nullable=False)
    kind = Column(String(40), nullable=False)  # "settlement" or "negotiation_letter"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loan = relationship("LoanProfile", back_populates="negotiations")
