import { useState } from "react";
import { api } from "./api";

function ProfileForm({ onCreated }) {
  const [form, setForm] = useState({
    name: "", email: "", monthly_income: "",
    lender_name: "", loan_type: "Personal Loan",
    outstanding_amount: "", emi_amount: "", overdue_duration_months: "",
    interest_rate: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const user = await api.createUser({
        name: form.name,
        email: form.email,
        monthly_income: parseFloat(form.monthly_income),
      });
      const loan = await api.createLoan({
        user_id: user.id,
        lender_name: form.lender_name,
        loan_type: form.loan_type,
        outstanding_amount: parseFloat(form.outstanding_amount),
        emi_amount: parseFloat(form.emi_amount),
        overdue_duration_months: parseInt(form.overdue_duration_months || "0", 10),
        interest_rate: form.interest_rate ? parseFloat(form.interest_rate) : null,
      });
      onCreated(loan);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="card">
      <h2>Borrower & Loan Details</h2>
      <div className="grid-2">
        <div className="field"><label>Full Name</label><input required value={form.name} onChange={update("name")} /></div>
        <div className="field"><label>Email</label><input required type="email" value={form.email} onChange={update("email")} /></div>
      </div>
      <div className="field"><label>Monthly Income (Rs.)</label><input required type="number" value={form.monthly_income} onChange={update("monthly_income")} /></div>
      <div className="grid-2">
        <div className="field"><label>Lender Name</label><input required value={form.lender_name} onChange={update("lender_name")} /></div>
        <div className="field">
          <label>Loan Type</label>
          <select value={form.loan_type} onChange={update("loan_type")}>
            <option>Personal Loan</option>
            <option>Credit Card</option>
            <option>Home Loan</option>
            <option>Vehicle Loan</option>
          </select>
        </div>
      </div>
      <div className="grid-2">
        <div className="field"><label>Outstanding Amount (Rs.)</label><input required type="number" value={form.outstanding_amount} onChange={update("outstanding_amount")} /></div>
        <div className="field"><label>Monthly EMI (Rs.)</label><input required type="number" value={form.emi_amount} onChange={update("emi_amount")} /></div>
      </div>
      <div className="grid-2">
        <div className="field"><label>Overdue Duration (months)</label><input type="number" value={form.overdue_duration_months} onChange={update("overdue_duration_months")} /></div>
        <div className="field"><label>Interest Rate % (optional)</label><input type="number" value={form.interest_rate} onChange={update("interest_rate")} /></div>
      </div>
      <button type="submit" disabled={loading}>{loading ? "Saving..." : "Save & Continue"}</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}

function SettlementTab({ loanId }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchSettlement = async () => {
    setLoading(true);
    setError("");
    try {
      setResult(await api.getSettlement(loanId));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>AI Settlement Recommendation</h2>
      <button onClick={fetchSettlement} disabled={loading}>
        {loading ? "Analysing..." : "Generate Settlement Recommendation"}
      </button>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="result-box">
          <p><strong>EMI-to-Income Ratio:</strong> {result.emi_to_income_ratio}%</p>
          <p><strong>Financial Stress Level:</strong> {result.financial_stress_level}</p>
          <p><strong>Recommended Settlement:</strong> {result.recommended_settlement_percentage}</p>
          <p><strong>Recommendation:</strong> {result.recommendation}</p>
          <p><strong>Financial Health Insight:</strong> {result.financial_health_insight}</p>
        </div>
      )}
    </div>
  );
}

function NegotiationLetterTab({ loanId }) {
  const [tone, setTone] = useState("professional");
  const [letter, setLetter] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.generateNegotiationLetter(loanId, tone);
      setLetter(res.letter);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>AI Negotiation Letter Generator</h2>
      <div className="field">
        <label>Tone</label>
        <select value={tone} onChange={(e) => setTone(e.target.value)}>
          <option value="professional">Professional</option>
          <option value="firm">Firm</option>
          <option value="empathetic">Empathetic</option>
        </select>
      </div>
      <button onClick={generate} disabled={loading}>{loading ? "Drafting..." : "Generate Letter"}</button>
      {error && <p className="error">{error}</p>}
      {letter && <pre className="letter-box">{letter}</pre>}
    </div>
  );
}

function FinancialHealthTab({ loanId }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchHealth = async () => {
    setLoading(true);
    setError("");
    try {
      setHealth(await api.getFinancialHealth(loanId));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Financial Health Dashboard</h2>
      <button onClick={fetchHealth} disabled={loading}>{loading ? "Loading..." : "Refresh Financial Health"}</button>
      {error && <p className="error">{error}</p>}
      {health && (
        <div className="result-box">
          <p><strong>Monthly Income:</strong> Rs. {health.monthly_income}</p>
          <p><strong>Monthly EMI:</strong> Rs. {health.monthly_emi}</p>
          <p><strong>Monthly Surplus:</strong> Rs. {health.monthly_surplus}</p>
          <p><strong>EMI-to-Income Ratio:</strong> {health.emi_to_income_ratio}%</p>
          <p><strong>Financial Stress Level:</strong> {health.financial_stress_level}</p>
          <p><strong>Overdue Duration:</strong> {health.overdue_duration_months} months</p>
        </div>
      )}
    </div>
  );
}

export default function App() {
  const [loan, setLoan] = useState(null);
  const [tab, setTab] = useState("settlement");

  return (
    <div className="app">
      <header className="topbar">
        <h1>FinRelief AI</h1>
        <p>AI Powered Debt Relief & Financial Recovery Platform</p>
      </header>

      <main className="layout">
        {!loan ? (
          <ProfileForm onCreated={setLoan} />
        ) : (
          <>
            <p className="loan-info">Loan Profile #{loan.id} created for {loan.lender_name} ({loan.loan_type})</p>
            <nav className="tabs">
              <button className={tab === "settlement" ? "active" : ""} onClick={() => setTab("settlement")}>Settlement Recommendation</button>
              <button className={tab === "letter" ? "active" : ""} onClick={() => setTab("letter")}>Negotiation Letter</button>
              <button className={tab === "health" ? "active" : ""} onClick={() => setTab("health")}>Financial Health</button>
            </nav>
            {tab === "settlement" && <SettlementTab loanId={loan.id} />}
            {tab === "letter" && <NegotiationLetterTab loanId={loan.id} />}
            {tab === "health" && <FinancialHealthTab loanId={loan.id} />}
          </>
        )}
      </main>
    </div>
  );
}
