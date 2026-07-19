const BASE_URL = "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Something went wrong");
  }
  return data;
}

export const api = {
  createUser: (payload) => request("/users", { method: "POST", body: JSON.stringify(payload) }),
  createLoan: (payload) => request("/loans", { method: "POST", body: JSON.stringify(payload) }),
  getSettlement: (loanId) => request(`/loans/${loanId}/settlement`),
  getFinancialHealth: (loanId) => request(`/loans/${loanId}/financial-health`),
  generateNegotiationLetter: (loanId, tone) =>
    request("/loans/negotiation-letter", {
      method: "POST",
      body: JSON.stringify({ loan_id: loanId, tone }),
    }),
};
