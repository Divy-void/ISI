import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FolderOpen, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import type { AnalysisSummary } from '../types';

export const MyDocumentsPage: React.FC = () => {
  const [items, setItems] = useState<AnalysisSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listAnalyses().then((res: any) => setItems(res)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-8 text-center text-slate-500">Loading documents...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">My Documents & Analyses</h1>
        <p className="text-sm text-slate-600">Reopen any uploaded tender or completed analysis.</p>
      </div>

      {items.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center text-slate-500">
          <FolderOpen className="w-8 h-8 mx-auto mb-2 text-slate-400" />
          No documents uploaded yet.
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-xs">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-600">
              <tr>
                <th className="p-4">Analysis Name</th>
                <th className="p-4">Document</th>
                <th className="p-4">Status</th>
                <th className="p-4">Requirements</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50">
                  <td className="p-4 font-medium text-slate-900">{a.title}</td>
                  <td className="p-4 text-xs text-slate-500">{a.filename || 'Pasted / Sample'}</td>
                  <td className="p-4">
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 capitalize">
                      {a.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="p-4 text-xs text-slate-600">{a.requirements_count ?? 0}</td>
                  <td className="p-4 text-right">
                    <Link
                      to={
                        a.status === 'completed'
                          ? `/analyses/${a.id}/recommendations`
                          : `/analyses/${a.id}/requirements`
                      }
                      className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 hover:underline"
                    >
                      Open <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
