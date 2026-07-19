"""
FinRelief AI - AI Powered Debt Relief & Financial Recovery Platform
--------------------------------------------------------------------
FastAPI backend exposing endpoints to:
  - create/manage borrower and loan profiles (SQLite via SQLAlchemy)
  - generate AI-powered settlement recommendations (Google Gemini)
  - generate AI-powered negotiation letters (Google Gemini)
  - compute financial health metrics (EMI-to-income ratio, stress level)

Run locally:
    uvicorn main:app --reload
Then open http://127.0.0.1:8000/docs for interactive API docs.
"""
import logging

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import models
import schemas
import gemini_service
from database import engine, get_db, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finrelief")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinRelief AI", description="AI Powered Debt Relief & Financial Recovery Platform")

# Performance: gzip-compress responses over 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global error handling (Backend Error Handling & AI Fallback Management)
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/")
def root():
    return {"message": "FinRelief AI backend is running"}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------
@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists")
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# Loan Profiles
# ---------------------------------------------------------------------------
@app.post("/loans", response_model=schemas.LoanProfileOut)
def create_loan(loan: schemas.LoanProfileCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == loan.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_loan = models.LoanProfile(**loan.model_dump())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


@app.get("/loans/{loan_id}", response_model=schemas.LoanProfileOut)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.LoanProfile).filter(models.LoanProfile.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan profile not found")
    return loan


@app.get("/users/{user_id}/loans", response_model=list[schemas.LoanProfileOut])
def list_user_loans(user_id: int, db: Session = Depends(get_db)):
    return db.query(models.LoanProfile).filter(models.LoanProfile.user_id == user_id).all()


# ---------------------------------------------------------------------------
# AI: Settlement Recommendation (Scenario 1 & 3)
# ---------------------------------------------------------------------------
@app.get("/loans/{loan_id}/settlement", response_model=schemas.SettlementResponse)
def get_settlement_recommendation(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.LoanProfile).filter(models.LoanProfile.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan profile not found")

    try:
        result = gemini_service.generate_settlement_recommendation(loan, loan.owner.monthly_income)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(exc)}")

    history = models.NegotiationHistory(
        loan_id=loan.id, kind="settlement",
        content=f"{result['recommended_settlement_percentage']} — {result['recommendation']}",
    )
    db.add(history)
    db.commit()

    return schemas.SettlementResponse(loan_id=loan.id, **result)


# ---------------------------------------------------------------------------
# AI: Negotiation Letter Generation (Scenario 2)
# ---------------------------------------------------------------------------
@app.post("/loans/negotiation-letter", response_model=schemas.NegotiationLetterResponse)
def generate_negotiation_letter(req: schemas.NegotiationLetterRequest, db: Session = Depends(get_db)):
    loan = db.query(models.LoanProfile).filter(models.LoanProfile.id == req.loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan profile not found")

    try:
        letter = gemini_service.generate_negotiation_letter(loan, loan.owner.monthly_income, req.tone)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(exc)}")

    history = models.NegotiationHistory(loan_id=loan.id, kind="negotiation_letter", content=letter)
    db.add(history)
    db.commit()

    return schemas.NegotiationLetterResponse(loan_id=loan.id, letter=letter)


# ---------------------------------------------------------------------------
# Financial Health Tracking (Scenario 3)
# ---------------------------------------------------------------------------
@app.get("/loans/{loan_id}/financial-health")
def get_financial_health(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.LoanProfile).filter(models.LoanProfile.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan profile not found")

    income = loan.owner.monthly_income
    ratio = loan.emi_to_income_ratio(income)
    stress = loan.financial_stress_level(income)
    monthly_surplus = round(income - loan.emi_amount, 2)

    return {
        "loan_id": loan.id,
        "monthly_income": income,
        "monthly_emi": loan.emi_amount,
        "monthly_surplus": monthly_surplus,
        "emi_to_income_ratio": ratio,
        "financial_stress_level": stress,
        "overdue_duration_months": loan.overdue_duration_months,
    }


@app.get("/loans/{loan_id}/negotiation-history")
def get_negotiation_history(loan_id: int, db: Session = Depends(get_db)):
    records = db.query(models.NegotiationHistory).filter(models.NegotiationHistory.loan_id == loan_id).all()
    return [{"id": r.id, "kind": r.kind, "content": r.content, "created_at": r.created_at} for r in records]
