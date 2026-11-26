import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, ArrowRight, Briefcase, ClipboardCheck, Settings } from 'lucide-react';
import { Logo } from '../components/Logo';
import { api } from '../services/api';
import type { DemoRole, User } from '../types';

interface LoginPageProps {
  onLogin: (user: User) => void;
}

const ROLES: {
  role: DemoRole;
  title: string;
  desc: string;
  icon: React.FC<{ className?: string }>;
}[] = [
  {
    role: 'procurement_officer',
    title: 'Procurement Officer',
    desc: 'Upload tenders, review extracted requirements, generate recommendations, and export reports.',
    icon: Briefcase,
  },
  {
    role: 'technical_reviewer',
    title: 'Technical Reviewer',
    desc: 'Inspect evidence, review coverage matrices, and accept or reject candidate standards.',
    icon: ClipboardCheck,
  },
  {
    role: 'admin',
    title: 'Administrator',
    desc: 'Manage demo users, synthetic standards catalogue records, and view audit logs.',
    icon: Settings,
  },
];

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [loadingRole, setLoadingRole] = useState<DemoRole | null>(null);
  const [error, setError] = useState('');

  const handleSelectRole = async (role: DemoRole) => {
    setLoadingRole(role);
    setError('');
    try {
      localStorage.setItem('is_assist_role', role);
      const user = (await api.demoLogin(role)) as User;
      onLogin(user);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Failed to sign in');
    } finally {
      setLoadingRole(null);
    }
  };

  return (
    <div className="min-h-screen bg-[#F0F6FF] flex flex-col justify-center items-center p-4">
      <div className="max-w-3xl w-full bg-white rounded-2xl shadow-sm border border-slate-200 p-6 sm:p-10">
        <div className="flex items-center gap-3 mb-6">
          <Logo className="w-11 h-11" />
          <div>
            <h1 className="text-2xl font-bold text-slate-900">IS-Assist</h1>
            <p className="text-sm text-slate-600">
              AI-Powered Indian Standards Recommendation Engine • SIH 2026 (PS 26108)
            </p>
          </div>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6 flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-900 leading-relaxed">
            <span className="font-semibold">Demonstration Access Only:</span> This local demo uses
            role-based demonstration sign-in without production credentials. All standards records
            are synthetic illustrative data (<code className="font-mono">DEMO-STD-*</code>) and
            require verification against official BIS sources.
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">
            {error}
          </div>
        )}

        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 mb-3">
          Select a Demo Role to Continue
        </h2>

        <div className="grid gap-4 sm:grid-cols-3">
          {ROLES.map((item) => {
            const Icon = item.icon;
            const isLoading = loadingRole === item.role;
            return (
              <button
                key={item.role}
                onClick={() => handleSelectRole(item.role)}
                disabled={loadingRole !== null}
                className="text-left p-4 rounded-xl border border-slate-200 hover:border-blue-500 hover:bg-blue-50/40 transition-all flex flex-col justify-between group"
              >
                <div>
                  <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center mb-3 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h3 className="font-semibold text-slate-900 mb-1">{item.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed">{item.desc}</p>
                </div>
                <div className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-blue-700">
                  {isLoading ? 'Signing in...' : 'Enter Demo'}
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
