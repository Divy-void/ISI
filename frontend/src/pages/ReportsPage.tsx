import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Download, Printer, FileBarChart2, ArrowLeft } from 'lucide-react';
import { api } from '../services/api';

export const ReportsListPage: React.FC = () => {
  const [reports, setReports] = useState<any[]>([]);

  useEffect(() => {
    api.listReports().then((res: any) => setReports(res));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Generated Reports</h1>
        <p className="text-sm text-slate-600">Downloadable decision-support reports with evidence and reviewer decisions.</p>
      </div>
      {reports.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center text-slate-500">
          <FileBarChart2 className="w-8 h-8 mx-auto mb-2 text-slate-400" />
          No reports generated yet. Complete an analysis and click <strong>Generate Report</strong>.
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 divide-y divide-slate-100">
          {reports.map((r) => (
            <div key={r.id} className="p-4 flex items-center justify-between">
              <div>
                <div className="font-mono text-xs font-bold text-blue-700">{r.report_code}</div>
                <div className="font-medium text-sm text-slate-900">{r.analysis_title}</div>
              </div>
              <div className="flex items-center gap-3">
                <a
                  href={`/api/reports/${r.id}/csv`}
                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-medium text-slate-700 hover:bg-slate-50"
                >
                  <Download className="w-3.5 h-3.5" /> CSV
                </a>
                <Link
                  to={`/reports/${r.id}`}
                  className="px-3 py-1.5 rounded-lg bg-blue-700 text-white text-xs font-semibold hover:bg-blue-800"
                >
                  View Report
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const ReportDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    api.getReport(Number(id)).then((res: any) => setReport(res));
  }, [id]);

  if (!report) return <div className="p-8 text-center text-slate-500">Loading report...</div>;

  const snap = report.summary_snapshot || {};

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between no-print">
        <Link to="/reports" className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-700 hover:underline">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Reports
        </Link>
        <div className="flex gap-2">
          <a
            href={`/api/reports/${report.id}/csv`}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-300 bg-white text-xs font-semibold text-slate-700 hover:bg-slate-50"
          >
            <Download className="w-4 h-4" /> Download CSV
          </a>
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-700 text-white text-xs font-semibold hover:bg-blue-800"
          >
            <Printer className="w-4 h-4" /> Print / Save PDF
          </button>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs space-y-6">
        <div className="border-b border-slate-200 pb-4">
          <div className="text-xs font-mono text-blue-700 font-bold">{report.report_code}</div>
          <h1 className="text-2xl font-bold text-slate-900 mt-1">IS-Assist Standards Recommendation Report</h1>
          <p className="text-sm text-slate-600">{snap.analysis?.title}</p>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 font-medium">
          {snap.disclaimer}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs bg-slate-50 p-4 rounded-xl">
          <div><strong>Category:</strong> {snap.analysis?.category}</div>
          <div><strong>Department:</strong> {snap.analysis?.department_name}</div>
          <div><strong>Document:</strong> {snap.document?.filename}</div>
        </div>

        <div>
          <h2 className="font-semibold text-slate-900 mb-2">Ranked Recommendations ({snap.recommendations?.length || 0})</h2>
          <div className="space-y-3">
            {(snap.recommendations || []).map((rec: any, i: number) => (
              <div key={i} className="p-4 rounded-xl border border-slate-200 text-xs space-y-1">
                <div className="flex justify-between font-semibold text-slate-900">
                  <span>{rec.catalogue_id} — {rec.title}</span>
                  <span className="text-blue-700">Score: {rec.relevance_score} ({rec.match_label})</span>
                </div>
                <p className="text-slate-600">{rec.explanation}</p>
                <div className="text-slate-500">
                  <strong>Decision:</strong> {rec.decision} • <strong>Verification:</strong> {rec.verification_status}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="font-semibold text-slate-900 mb-2">Extracted Requirements ({snap.requirements?.length || 0})</h2>
          <div className="divide-y divide-slate-100 border border-slate-200 rounded-xl">
            {(snap.requirements || []).map((req: any, i: number) => (
              <div key={i} className="p-3 text-xs">
                <span className="font-mono font-semibold text-blue-700">{req.req_code}</span>{' '}
                <span className="text-slate-500">({req.category})</span>: {req.description}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
