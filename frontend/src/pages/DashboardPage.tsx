import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FileText,
  Award,
  Clock,
  Bookmark,
  FilePlus2,
  Sparkles,
  ArrowRight,
  Activity,
  BookOpen,
} from 'lucide-react';
import { api } from '../services/api';
import type { DashboardStats, AnalysisSummary } from '../types';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recent, setRecent] = useState<{
    recent_analyses: AnalysisSummary[];
    recent_activity: any[];
    latest_catalogue_updates: any[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [sampleLoading, setSampleLoading] = useState(false);

  useEffect(() => {
    Promise.all([api.getDashboardStats(), api.getDashboardRecent()])
      .then(([s, r]: any) => {
        setStats(s);
        setRecent(r);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleTrySample = async () => {
    setSampleLoading(true);
    try {
      const created: any = await api.createAnalysis({
        title: 'Municipal Outdoor LED Street Lighting Procurement',
        category: 'Lighting',
        department_name: 'Municipal Electrical & Lighting',
        context_notes: 'Built-in synthetic demonstration tender for outdoor LED street lighting.',
        is_sample: true,
      });
      await api.processAnalysis(created.id);
      navigate(`/analyses/${created.id}/requirements`);
    } catch (err) {
      console.error(err);
    } finally {
      setSampleLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading dashboard...</div>;
  }

  const statCards = [
    {
      label: 'Documents Processed',
      value: stats?.total_documents_processed ?? 0,
      icon: FileText,
      color: 'text-blue-600 bg-blue-50',
    },
    {
      label: 'Standards Identified',
      value: stats?.standards_identified ?? 0,
      icon: Award,
      color: 'text-emerald-600 bg-emerald-50',
    },
    {
      label: 'Awaiting Review',
      value: stats?.analyses_awaiting_review ?? 0,
      icon: Clock,
      color: 'text-amber-600 bg-amber-50',
    },
    {
      label: 'Saved Standards',
      value: stats?.saved_standards ?? 0,
      icon: Bookmark,
      color: 'text-purple-600 bg-purple-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Quick Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Procurement Standards Dashboard</h1>
          <p className="text-sm text-slate-600">
            Upload tender specifications to extract requirements and discover candidate standards.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleTrySample}
            disabled={sampleLoading}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold shadow-sm transition-colors disabled:opacity-60"
          >
            <Sparkles className="w-4 h-4" />
            {sampleLoading ? 'Loading Sample...' : 'Try Sample Tender'}
          </button>
          <Link
            to="/analyses/new"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold shadow-sm transition-colors"
          >
            <FilePlus2 className="w-4 h-4" />
            New Analysis
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.label} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                  {c.label}
                </span>
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${c.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="mt-3 text-3xl font-bold text-slate-900">{c.value}</div>
            </div>
          );
        })}
      </div>

      {/* Recent Analyses & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Recent Tender Analyses</h2>
            <Link to="/documents" className="text-xs font-medium text-blue-700 hover:underline">
              View all
            </Link>
          </div>
          {recent?.recent_analyses.length === 0 ? (
            <div className="py-10 text-center text-sm text-slate-500">
              No analyses yet. Click <strong>Try Sample Tender</strong> or{' '}
              <strong>New Analysis</strong> to begin.
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {recent?.recent_analyses.map((a) => (
                <div key={a.id} className="py-3 flex items-center justify-between gap-4">
                  <div>
                    <div className="font-medium text-sm text-slate-900">{a.title}</div>
                    <div className="text-xs text-slate-500">
                      {a.category} • {a.department_name}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 capitalize">
                      {a.status.replace('_', ' ')}
                    </span>
                    <Link
                      to={
                        a.status === 'completed'
                          ? `/analyses/${a.id}/recommendations`
                          : `/analyses/${a.id}/requirements`
                      }
                      className="text-blue-700 hover:text-blue-900"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="flex items-center gap-2 mb-3">
              <Activity className="w-4 h-4 text-blue-600" />
              <h2 className="font-semibold text-slate-900 text-sm">Recent Activity</h2>
            </div>
            <div className="space-y-3">
              {recent?.recent_activity.slice(0, 4).map((e) => (
                <div key={e.id} className="text-xs border-l-2 border-blue-200 pl-3">
                  <div className="font-medium text-slate-800">{e.details}</div>
                  <div className="text-slate-400">{e.username}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
            <div className="flex items-center gap-2 mb-3">
              <BookOpen className="w-4 h-4 text-emerald-600" />
              <h2 className="font-semibold text-slate-900 text-sm">Demo Catalogue Updates</h2>
            </div>
            <div className="space-y-2.5">
              {recent?.latest_catalogue_updates.map((s) => (
                <Link
                  key={s.id}
                  to={`/standards/${s.id}`}
                  className="block p-2 rounded-lg hover:bg-slate-50 border border-slate-100"
                >
                  <div className="text-xs font-semibold text-blue-700">{s.catalogue_id}</div>
                  <div className="text-xs text-slate-700 truncate">{s.title}</div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
