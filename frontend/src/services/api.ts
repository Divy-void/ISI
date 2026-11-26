import type { DemoRole } from '../types';

const getRole = (): DemoRole => {
  return (localStorage.getItem('is_assist_role') as DemoRole) || 'procurement_officer';
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('X-Demo-Role', getRole());
  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  demoLogin: (role: DemoRole) =>
    request('/api/auth/demo-login', { method: 'POST', body: JSON.stringify({ role }) }),
  getMe: () => request('/api/auth/me'),
  logout: () => request('/api/auth/logout', { method: 'POST' }),

  getDashboardStats: () => request('/api/dashboard/stats'),
  getDashboardRecent: () => request('/api/dashboard/recent'),

  createAnalysis: (data: {
    title: string;
    category: string;
    department_name: string;
    context_notes?: string;
    pasted_text?: string;
    is_sample?: boolean;
  }) => request('/api/analyses', { method: 'POST', body: JSON.stringify(data) }),

  listAnalyses: () => request('/api/analyses'),
  getAnalysis: (id: number) => request(`/api/analyses/${id}`),
  uploadDocument: (id: number, file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return request(`/api/analyses/${id}/upload`, { method: 'POST', body: fd });
  },
  processAnalysis: (id: number) => request(`/api/analyses/${id}/process`, { method: 'POST' }),
  getRequirements: (id: number) => request(`/api/analyses/${id}/requirements`),
  updateRequirements: (id: number, requirements: any[]) =>
    request(`/api/analyses/${id}/requirements`, {
      method: 'PUT',
      body: JSON.stringify({ requirements }),
    }),

  generateRecommendations: (id: number) =>
    request(`/api/analyses/${id}/recommend`, { method: 'POST' }),
  getRecommendations: (id: number) => request(`/api/analyses/${id}/recommendations`),
  saveDecision: (recId: number, decision: string, comments: string) =>
    request(`/api/recommendations/${recId}/decision`, {
      method: 'POST',
      body: JSON.stringify({ decision, comments }),
    }),
  getCoverage: (id: number) => request(`/api/analyses/${id}/coverage`),

  listStandards: () => request('/api/standards'),
  searchStandards: (q: string, sector: string, category: string) =>
    request(`/api/standards/search?q=${encodeURIComponent(q)}&sector=${encodeURIComponent(sector)}&category=${encodeURIComponent(category)}`),
  getStandard: (id: number) => request(`/api/standards/${id}`),
  createStandard: (data: any) =>
    request('/api/standards', { method: 'POST', body: JSON.stringify(data) }),

  listSavedStandards: () => request('/api/saved-standards'),
  saveStandard: (standardId: number) =>
    request(`/api/saved-standards?standard_id=${standardId}`, { method: 'POST' }),
  removeSavedStandard: (savedId: number) =>
    request(`/api/saved-standards/${savedId}`, { method: 'DELETE' }),

  generateReport: (analysisId: number) =>
    request(`/api/analyses/${analysisId}/reports`, { method: 'POST' }),
  listReports: () => request('/api/reports'),
  getReport: (id: number) => request(`/api/reports/${id}`),

  getAdminUsers: () => request('/api/admin/users'),
  getAdminAudit: () => request('/api/admin/audit'),
  getAdminCatalogue: () => request('/api/admin/catalogue'),
};
