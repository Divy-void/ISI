import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { NewAnalysisPage } from './pages/NewAnalysisPage';
import { RequirementReviewPage } from './pages/RequirementReviewPage';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { CoverageMatrixPage } from './pages/CoverageMatrixPage';
import { StandardsSearchPage, StandardDetailPage } from './pages/StandardsPages';
import { MyDocumentsPage } from './pages/MyDocumentsPage';
import { ReportsListPage, ReportDetailPage } from './pages/ReportsPage';
import { AdminPage } from './pages/AdminPage';
import { api } from './services/api';
import type { User } from './types';

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    const role = localStorage.getItem('is_assist_role');
    if (!role) {
      setChecking(false);
      return;
    }
    api
      .getMe()
      .then((u: any) => setUser(u))
      .catch(() => localStorage.removeItem('is_assist_role'))
      .finally(() => setChecking(false));
  }, []);

  const handleLogout = () => {
    api.logout().catch(() => {});
    localStorage.removeItem('is_assist_role');
    setUser(null);
  };

  if (checking) {
    return <div className="min-h-screen flex items-center justify-center text-slate-500">Loading IS-Assist...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={setUser} />} />
        <Route
          path="/*"
          element={
            user ? (
              <AppLayout user={user} onLogout={handleLogout}>
                <Routes>
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/analyses/new" element={<NewAnalysisPage />} />
                  <Route path="/analyses/:id/requirements" element={<RequirementReviewPage />} />
                  <Route path="/analyses/:id/recommendations" element={<RecommendationsPage />} />
                  <Route path="/analyses/:id/coverage" element={<CoverageMatrixPage />} />
                  <Route path="/documents" element={<MyDocumentsPage />} />
                  <Route path="/standards" element={<StandardsSearchPage />} />
                  <Route path="/standards/:id" element={<StandardDetailPage />} />
                  <Route path="/reports" element={<ReportsListPage />} />
                  <Route path="/reports/:id" element={<ReportDetailPage />} />
                  <Route path="/admin" element={<AdminPage />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </AppLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
