const BASE_URL = "http://127.0.0.1:8000/api/admin";

const handleResponse = async (res: Response) => {
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
};

export const adminAPI = {
  getOverview: async () => {
    const res = await fetch(`${BASE_URL}/overview`);
    return handleResponse(res);
  },

  getRiskSummary: async () => {
    const res = await fetch(`${BASE_URL}/risk-summary`);
    return handleResponse(res);
  },

  getSymptomTrends: async (days = 7) => {
    const res = await fetch(`${BASE_URL}/trends/symptoms?days=${days}`);
    return handleResponse(res);
  },

  getWeeklyRiskTrend: async () => {
    const res = await fetch(`${BASE_URL}/trends/weekly-risk`);
    return handleResponse(res);
  },

  getDepartmentTrends: async () => {
    const res = await fetch(`${BASE_URL}/trends/departments`);
    return handleResponse(res);
  },

  getAlerts: async () => {
    const res = await fetch(`${BASE_URL}/alerts`);
    return handleResponse(res);
  }
};
