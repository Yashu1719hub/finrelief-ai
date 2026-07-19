"""
Gemini AI integration for FinRelief AI.

Two core AI capabilities:
1. generate_settlement_recommendation() - analyses a borrower's loan +
   income data and produces a settlement % recommendation with reasoning.
2. generate_negotiation_letter() - drafts a lender-specific negotiation /
   settlement request email based on the borrower's financial condition.
"""
import os
import json
import re

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _extract_json(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {"recommended_settlement_percentage": "N/A", "recommendation": raw_text[:500],
                "financial_health_insight": ""}


def _fallback_settlement(loan, monthly_income: float, ratio: float, stress: str) -> dict:
    """Rule-based fallback used when the Gemini API is unavailable or errors out,
    so the app never breaks even if the AI call fails (Fallback Logic Implementation)."""
    if stress == "High":
        pct = "60-70% of outstanding amount"
        rec = "Given the high financial stress, propose a lump-sum settlement at 60-70% with a short payment window, or request a restructured EMI plan."
    elif stress == "Medium":
        pct = "40-55% of outstanding amount"
        rec = "Moderate stress detected. A phased settlement (2-3 installments) at 40-55% of the outstanding amount is a reasonable starting offer."
    else:
        pct = "25-35% of outstanding amount"
        rec = "Financial stress is low; the borrower can likely negotiate a modest settlement or continue with a revised EMI schedule."
    insight = f"EMI consumes {ratio}% of monthly income with {loan.overdue_duration_months} month(s) overdue — stress level: {stress}."
    return {
        "recommended_settlement_percentage": pct,
        "recommendation": rec,
        "financial_health_insight": insight,
    }


def generate_settlement_recommendation(loan, monthly_income: float) -> dict:
    ratio = loan.emi_to_income_ratio(monthly_income)
    stress = loan.financial_stress_level(monthly_income)

    if not GEMINI_API_KEY:
        fallback = _fallback_settlement(loan, monthly_income, ratio, stress)
        return {"emi_to_income_ratio": ratio, "financial_stress_level": stress, **fallback}

    prompt = f"""
You are a financial debt-recovery advisor AI. Analyse the borrower's situation
and recommend a fair settlement strategy.

Loan details:
- Lender: {loan.lender_name}
- Loan type: {loan.loan_type}
- Outstanding amount: Rs. {loan.outstanding_amount}
- Monthly EMI: Rs. {loan.emi_amount}
- Overdue duration: {loan.overdue_duration_months} months
- Monthly income: Rs. {monthly_income}
- EMI-to-income ratio: {ratio}%
- Financial stress level: {stress}

Respond with ONLY valid JSON (no markdown fences), using exactly this schema:
{{
  "recommended_settlement_percentage": "e.g. '55-65% of outstanding amount'",
  "recommendation": "2-3 sentence practical settlement strategy",
  "financial_health_insight": "1-2 sentence insight about the borrower's financial stress and repayment capability"
}}
"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        data = _extract_json(response.text)
        return {
            "emi_to_income_ratio": ratio,
            "financial_stress_level": stress,
            "recommended_settlement_percentage": data.get("recommended_settlement_percentage", "N/A"),
            "recommendation": data.get("recommendation", ""),
            "financial_health_insight": data.get("financial_health_insight", ""),
        }
    except Exception:
        # Fallback Logic: Gemini call failed (quota, network, etc.) — degrade gracefully
        fallback = _fallback_settlement(loan, monthly_income, ratio, stress)
        return {"emi_to_income_ratio": ratio, "financial_stress_level": stress, **fallback}


def _fallback_negotiation_letter(loan, monthly_income: float, ratio: float) -> str:
    """Rule-based fallback negotiation letter used when Gemini is unavailable."""
    return f"""Subject: Request to Discuss Settlement Options for {loan.loan_type} Account

Dear {loan.lender_name} Team,

I am writing regarding my {loan.loan_type} account with an outstanding balance of
Rs. {loan.outstanding_amount}. Due to financial constraints, my current EMI of
Rs. {loan.emi_amount} represents {ratio}% of my monthly income, which has made
timely repayment difficult ({loan.overdue_duration_months} month(s) overdue).

I would like to request a discussion on possible settlement options or a revised
repayment plan that better reflects my current financial situation. I remain
committed to resolving this obligation and would appreciate the opportunity to
work out a mutually agreeable arrangement.

Thank you for your understanding and consideration.

Sincerely,
The Borrower"""


def generate_negotiation_letter(loan, monthly_income: float, tone: str = "professional") -> str:
    ratio = loan.emi_to_income_ratio(monthly_income)

    if not GEMINI_API_KEY:
        return _fallback_negotiation_letter(loan, monthly_income, ratio)

    prompt = f"""
Write a {tone} negotiation/settlement request email from a borrower to their
lender, based on the following details. Keep it realistic, respectful, and
specific to the numbers provided. Sign off as "The Borrower".

Lender: {loan.lender_name}
Loan type: {loan.loan_type}
Outstanding amount: Rs. {loan.outstanding_amount}
Monthly EMI: Rs. {loan.emi_amount}
Overdue duration: {loan.overdue_duration_months} months
Monthly income: Rs. {monthly_income}
EMI-to-income ratio: {ratio}%

Return only the email text (with a subject line at the top), no extra commentary.
"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return _fallback_negotiation_letter(loan, monthly_income, ratio)
