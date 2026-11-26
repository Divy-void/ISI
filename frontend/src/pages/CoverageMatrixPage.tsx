import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import type { CoverageMatrixData } from '../types';

export const CoverageMatrixPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const analysisId = Number(id);
  const [data, setData] = useState<CoverageMatrixData | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);

  useEffect(() => {
    api.getCoverage(analysisId).then((res: any) => setData(res));
  }, [analysisId]);

  if (!data) return <div className="p-8 text-center text-slate-500">Loading coverage matrix...</div>;

  const badge = (status: string) => {
    if (status === 'covered') return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (status === 'partially_covered') return 'bg-amber-100 text-amber-800 border-amber-200';
    if (status === 'needs_review') return 'bg-purple-100 text-purple-800 border-purple-200';
    return 'bg-red-50 text-red-700 border-red-200';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link
            to={`/analyses/${analysisId}/recommendations`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-700 hover:underline mb-1"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Recommendations
          </Link>
          <h1 className="text-2xl font-bold text-slate-900">Requirement Coverage Matrix</h1>
        </div>
      </div>

      {data.uncovered_critical.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 space-y-1">
          <div className="flex items-center gap-2 text-sm font-semibold text-red-800">
            <AlertTriangle className="w-4 h-4" />
            Uncovered Critical Requirements ({data.uncovered_critical.length})
          </div>
          {data.uncovered_critical.map((u) => (
            <div key={u.req_code} className="text-xs text-red-700">
              <span className="font-mono font-semibold">{u.req_code}</span>: {u.description}
            </div>
          ))}
        </div>
      )}

      {selectedEvidence && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-xs text-blue-900 flex justify-between items-center">
          <span><strong>Evidence Inspection:</strong> {selectedEvidence}</span>
          <button onClick={() => setSelectedEvidence(null)} className="underline font-semibold">
            Close
          </button>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-slate-200 overflow-x-auto shadow-xs">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200">
              <th className="p-3 font-semibold text-slate-700 min-w-[260px]">Requirement</th>
              {data.columns.map((col) => (
                <th key={col.standard_id} className="p-3 font-semibold text-slate-700 text-center min-w-[130px]">
                  <div className="font-mono text-blue-700">{col.catalogue_id}</div>
                  <div className="text-[11px] font-normal text-slate-500">Score: {col.relevance_score}</div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {data.rows.map((row) => (
              <tr key={row.requirement_id} className="hover:bg-slate-50/60">
                <td className="p-3">
                  <div className="font-mono font-semibold text-slate-900">{row.req_code}</div>
                  <div className="text-slate-600 line-clamp-2">{row.description}</div>
                </td>
                {row.cells.map((cell) => (
                  <td key={cell.standard_id} className="p-3 text-center">
                    <button
                      onClick={() => setSelectedEvidence(`${row.req_code} ↔ ${cell.catalogue_id}: ${cell.evidence_note}`)}
                      className={`px-2 py-1 rounded-md border text-[11px] font-medium capitalize ${badge(
                        cell.coverage_status
                      )}`}
                    >
                      {cell.coverage_status.replace('_', ' ')}
                    </button>
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
