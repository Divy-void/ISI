import React, { useEffect, useState } from 'react';
import { ShieldCheck, Plus } from 'lucide-react';
import { api } from '../services/api';

export const AdminPage: React.FC = () => {
  const [users, setUsers] = useState<any[]>([]);
  const [audit, setAudit] = useState<any[]>([]);
  const [catalogue, setCatalogue] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [newStd, setNewStd] = useState({
    catalogue_id: '',
    title: '',
    sector: 'Lighting',
    product_category: '',
    description: '',
    scope: '',
  });

  const load = () => {
    Promise.all([api.getAdminUsers(), api.getAdminAudit(), api.getAdminCatalogue()])
      .then(([u, a, c]: any) => {
        setUsers(u);
        setAudit(a);
        setCatalogue(c);
      })
      .catch((err) => setError(err.message || 'Admin access required'));
  };

  useEffect(() => {
    load();
  }, []);

  const handleAddStandard = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createStandard({
        ...newStd,
        technical_keywords: [],
        related_requirement_categories: ['Product specification'],
        applicability_conditions: 'Demo record',
      });
      setNewStd({ catalogue_id: '', title: '', sector: 'Lighting', product_category: '', description: '', scope: '' });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (error) {
    return (
      <div className="p-6 rounded-xl bg-red-50 border border-red-200 text-sm text-red-800">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <ShieldCheck className="w-6 h-6 text-blue-700" />
        <h1 className="text-2xl font-bold text-slate-900">Administration Panel</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
          <h2 className="font-semibold text-slate-900 mb-3">Demo Users & Roles</h2>
          <div className="divide-y divide-slate-100 text-xs">
            {users.map((u) => (
              <div key={u.id} className="py-2.5 flex justify-between">
                <div>
                  <div className="font-semibold text-slate-900">{u.full_name}</div>
                  <div className="text-slate-500">{u.email}</div>
                </div>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 h-fit">{u.role}</span>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleAddStandard} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
          <h2 className="font-semibold text-slate-900">Add Demo Catalogue Record</h2>
          <div className="grid grid-cols-2 gap-2">
            <input
              required
              placeholder="DEMO-STD-015"
              value={newStd.catalogue_id}
              onChange={(e) => setNewStd({ ...newStd, catalogue_id: e.target.value })}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs"
            />
            <input
              required
              placeholder="Sector (e.g. Lighting)"
              value={newStd.sector}
              onChange={(e) => setNewStd({ ...newStd, sector: e.target.value })}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs"
            />
          </div>
          <input
            required
            placeholder="Illustrative Title"
            value={newStd.title}
            onChange={(e) => setNewStd({ ...newStd, title: e.target.value })}
            className="w-full px-3 py-1.5 rounded-lg border border-slate-300 text-xs"
          />
          <input
            required
            placeholder="Scope"
            value={newStd.scope}
            onChange={(e) => setNewStd({ ...newStd, scope: e.target.value })}
            className="w-full px-3 py-1.5 rounded-lg border border-slate-300 text-xs"
          />
          <button
            type="submit"
            className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-blue-700 text-white text-xs font-semibold"
          >
            <Plus className="w-3.5 h-3.5" /> Add Record ({catalogue.length} total)
          </button>
        </form>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs">
        <h2 className="font-semibold text-slate-900 mb-3">Recent Audit Activity</h2>
        <div className="divide-y divide-slate-100 text-xs max-h-72 overflow-y-auto">
          {audit.map((e) => (
            <div key={e.id} className="py-2 flex justify-between gap-4">
              <div>
                <span className="font-mono font-semibold text-blue-700">{e.action}</span> — {e.details}
              </div>
              <span className="text-slate-400 shrink-0">{e.username}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
