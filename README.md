# AI Powered Debt Relief & Financial Recovery Platform (FinRelief AI)

An intelligent AI-powered web application that simplifies and automates the
debt management and financial recovery process for borrowers. Users manage
loan details, analyze financial health, generate AI-powered negotiation
strategies, and receive adaptive settlement recommendations.

Built with **React.js** (frontend) + **FastAPI** (backend) + **SQLite /
SQLAlchemy ORM** (database) + **Google Gemini API** (AI recommendations).

## Scenarios Covered

1. **AI-Powered Settlement Recommendation** — borrower enters loan details
   (outstanding amount, EMI, overdue duration, income); the system analyzes
   financial health and generates a settlement % recommendation.
2. **Intelligent Negotiation Letter Generation** — the platform uses Gemini
   to draft a professional, lender-specific negotiation/settlement email.
3. **Financial Health Tracking & Loan Analysis** — dashboard showing EMI
   ratio, financial stress level, and monthly surplus.

## Entity Relationship (ER) Diagram

See `docs/ER_Diagram_FinRelief_AI.docx` and `docs/er.png` for the full diagram.

- **User** (1) → (many) **LoanProfile** — a borrower can have multiple loans
- **LoanProfile** (1) → (many) **NegotiationHistory** — each loan can have
  multiple AI-generated settlement recommendations / negotiation letters

## Project Workflow

1. **Pre-requisites** — install Python, Node.js, get a Gemini API key
2. **Epic 1: Application Development & System Setup** — backend/frontend
   environment, dependencies, and project structure
3. **Epic 2: AI Integration & Financial Processing Setup** — FastAPI routes,
   the financial engine (EMI ratio/stress calculations), the settlement
   prediction system, the AI negotiation strategy engine, and fallback logic
4. **Epic 3: Database Management & Financial Data Storage Setup** — SQLite +
   SQLAlchemy models and API endpoints for loans and settlement data
5. **Epic 4: Frontend Integration & UI Development** — React dashboard,
   API communication layer, financial health visualization
6. **Epic 5: Testing, Debugging & Performance Optimization** — automated
   tests (`backend/test_main.py`), global error handling, gzip compression
7. **Epic 6: Version Control, Project Finalization & Deployment Readiness** —
   Git/GitHub setup, clean modular folder structure, deployment configuration
   (`Procfile`, `.env.production.example`)

## Project Structure

```
finrelief-ai/
├── backend/
│   ├── main.py              # FastAPI app, routes, error handling, gzip middleware
│   ├── models.py            # SQLAlchemy ORM models (User, LoanProfile, NegotiationHistory)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── database.py          # SQLite engine/session setup
│   ├── gemini_service.py    # Google Gemini prompt logic + rule-based fallback logic
│   ├── test_main.py         # Automated test suite (pytest)
│   ├── requirements.txt
│   ├── Procfile             # Deployment config (Render/Heroku-style)
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.production.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx          # Dashboard UI (3 tabs: Settlement, Letter, Health)
│       ├── api.js           # API calls to FastAPI backend
│       └── index.css
└── docs/
    ├── er.png                          # ER diagram image
    └── ER_Diagram_FinRelief_AI.docx    # ER diagram document
```

## 1. Pre-Requisites

- Python 3.9+
- Node.js 18+ and npm
- A free **Google Gemini API key** → https://aistudio.google.com/app/apikey
- Git + GitHub account

## 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
# open .env and paste your real Gemini API key after GEMINI_API_KEY=

uvicorn main:app --reload
```
Backend runs at **http://127.0.0.1:8000** (interactive docs at `/docs`).

## 3. Frontend Setup

Open a **second terminal**:
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at **http://127.0.0.1:5173**.

## 4. Using the App

1. Fill in borrower name, email, income, and loan details → Save & Continue
2. Use the three tabs to:
   - Generate an AI settlement recommendation
   - Generate an AI negotiation letter (choose tone: professional/firm/empathetic)
   - View the financial health dashboard (EMI ratio, stress level, surplus)

## 5. Running Tests (System Testing)

```bash
cd backend
pytest test_main.py -v
```
This covers user creation, duplicate-email validation, loan profile
creation, financial health calculation, 404 handling, and the settlement
fallback logic (in case the Gemini API key isn't configured).

## 6. Deployment Readiness

- **Backend:** the `Procfile` in `backend/` allows one-click deployment on
  platforms like Render or Heroku (`web: uvicorn main:app --host 0.0.0.0 --port $PORT`).
- **Frontend:** rename `.env.production.example` to `.env.production`, set
  `VITE_API_BASE_URL` to your deployed backend URL, then run `npm run build`
  to produce a production-ready `dist/` folder.
- **Error handling:** a global exception handler in `main.py` ensures the
  API never crashes with an unhandled 500 — it always returns a clean JSON
  error response.
- **Performance:** GZip middleware compresses API responses for faster
  load times.

## 7. Uploading to GitHub

```bash
cd finrelief-ai
git init
git add .
git commit -m "AI Powered Debt Relief & Financial Recovery Platform"
git branch -M main
git remote add origin https://github.com/<your-username>/finrelief-ai.git
git push -u origin main
```

If you don't have a repo yet: go to github.com → **New repository** → name
it `finrelief-ai` → **Create repository** (don't add a README there) → then
run the commands above.

⚠️ `.env` is excluded via `.gitignore` — your real Gemini API key is never
uploaded to GitHub, only `.env.example` (the template).

## 6. Skills Used

Python, FastAPI, SQLite, SQLAlchemy ORM, Generative AI (Google Gemini),
Responsible AI, LLMs, Prompt Engineering, React.js, API Integration, Cloud
Computing.

## 7. Conclusion

FinRelief AI demonstrates a full-stack AI-powered financial platform:
structured loan and borrower data is stored via SQLAlchemy/SQLite, financial
health is computed algorithmically, and Google Gemini generates realistic,
context-aware settlement recommendations and negotiation letters — covering
database design, AI integration, backend API development, and frontend
delivery as required by the project workflow.
