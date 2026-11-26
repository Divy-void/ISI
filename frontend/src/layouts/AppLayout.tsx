import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FilePlus2,
  FolderOpen,
  BookOpen,
  FileBarChart2,
  ShieldCheck,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { Logo } from '../components/Logo';
import type { User } from '../types';

interface AppLayoutProps {
  user: User;
  onLogout: () => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ user, onLogout, children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/analyses/new', label: 'New Analysis', icon: FilePlus2 },
    { to: '/documents', label: 'My Documents', icon: FolderOpen },
    { to: '/standards', label: 'Standards Catalogue', icon: BookOpen },
    { to: '/reports', label: 'Reports', icon: FileBarChart2 },
    ...(user.role === 'admin'
      ? [{ to: '/admin', label: 'Admin Panel', icon: ShieldCheck }]
      : []),
  ];

  const roleLabel =
    user.role === 'procurement_officer'
      ? 'Procurement Officer'
      : user.role === 'technical_reviewer'
      ? 'Technical Reviewer'
      : 'Administrator';

  const handleLogoutClick = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex bg-[#F8FAFC] text-[#0F172A]">
      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform lg:static lg:translate-x-0 no-print ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="h-16 px-5 flex items-center justify-between border-b border-slate-200">
          <Link to="/dashboard" className="flex items-center gap-2.5">
            <Logo className="w-8 h-8" />
            <div>
              <span className="font-bold text-base tracking-tight text-slate-900 block leading-none">
                IS-Assist
              </span>
              <span className="text-[11px] text-slate-500 font-medium">SIH 2026 • PS 26108</span>
            </div>
          </Link>
          <button
            className="lg:hidden p-1 text-slate-500 hover:text-slate-800"
            onClick={() => setMobileOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = location.pathname === item.to || location.pathname.startsWith(item.to + '/');
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-slate-200">
          <div className="bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-[11px] text-amber-800">
            <span className="font-semibold block">DEMO ENVIRONMENT</span>
            Synthetic catalogue only. Not official BIS verification.
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b border-slate-200 px-4 lg:px-8 flex items-center justify-between sticky top-0 z-30 no-print">
          <div className="flex items-center gap-3">
            <button
              className="lg:hidden p-2 rounded-lg border border-slate-200 text-slate-600"
              onClick={() => setMobileOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
              DEMO ENVIRONMENT
            </span>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm font-semibold text-slate-900">{user.full_name}</div>
              <div className="text-xs text-slate-500">{roleLabel}</div>
            </div>
            <button
              onClick={handleLogoutClick}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              Switch Role
            </button>
          </div>
        </header>

        <main className="flex-1 p-4 lg:p-8 max-w-7xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};
