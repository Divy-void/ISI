import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  Grid3X3,
  FileBarChart2,
  AlertTriangle,
  ExternalLink,
} from 'lucide-react';
import { api } from '../services/api';
import type { RecommendationItem } from '../types';

export const RecommendationsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const analysisId = Number(id);
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState<any>(null);
  const [recs, setRecs] = useState<RecommendationItem[]>([]);
  const [comments, setComments] = useState<Record<number, string>>({});
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);

  const loadData = () => {
    Promise.all([api.getAnalysis(analysisId), api.getRecommendations(analysisId)])
      .then(([a, r]: any) => {
        setAnalysis(a);
        setRecs(r);
        const initialComments: Record<number, string> = {};
        r.forEach((item: RecommendationItem) => {
          initialComments[item.id] = item.decision?.comments || '';
        });
        setComments(initialComments);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, [analysisId]);

  const handleDecision = async (recId: number, decision: string) => {
    await api.saveDecision(recId, decision, comments[recId] || '');
    loadData();
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const rpt: any = await api.generateReport(analysisId);
      navigate(`/reports/${rpt.id}`);
    } finally {
      setGeneratingReport(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Loading recommendations...</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Recommendation Results</h1>
          <p className="text-sm text-slate-600">{analysis?.title}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            to={`/analyses/${analysisId}/coverage`}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-sm font-semibold text-slate-700"
          >
            <Grid3X3 className="w-4 h-4" />
            Coverage Matrix
          </Link>
          <button
            onClick={handleGenerateReport}
            disabled={generatingReport}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold shadow-sm"
          >
            <FileBarChart2 className="w-4 h-4" />
            {generatingReport ? 'Generating...' : 'Generate Report'}
          </button>
        </div>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3 text-xs text-amber-900">
        <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold">Decision-Support Notice:</span> Relevance scores are
          ranking signals from the synthetic demonstration catalogue, not a probability of
          compliance. Version, amendment, and QCO status are{' '}
          <strong>Not verified in demo catalogue</strong>.
        </div>
      </div>

      <div className="space-y-5">
        {recs.map((rec) => {
          const badgeColor =
            rec.match_label === 'Best Match'
              ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
              : rec.match_label === 'Partial Match'
              ? 'bg-blue-50 text-blue-700 border-blue-200'
              : 'bg-amber-50 text-amber-700 border-amber-200';

          return (
            <div key={rec.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="font-mono text-xs font-bold px-2.5 py-0.5 rounded bg-slate-100 text-slate-800">
                      {rec.standard.catalogue_id}
                    </span>
                    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
                      {rec.match_label}
                    </span>
                    <span className="text-xs text-slate-500">{rec.standard.sector}</span>
                  </div>
                  <Link
                    to={`/standards/${rec.standard.id}`}
                    className="text-lg font-bold text-slate-900 hover:text-blue-700 inline-flex items-center gap-1.5"
                  >
                    {rec.standard.title}
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                </div>

                <div className="text-left md:text-right shrink-0">
                  <div className="text-xs text-slate-500 font-medium">Demo Relevance Score</div>
                  <div className="text-3xl font-bold text-blue-700">{rec.relevance_score}</div>
                </div>
              </div>

              <p className="text-sm text-slate-700">{rec.explanation}</p>

              {/* Score Breakdown */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-100">
                {Object.entries(rec.score_breakdown).map(([k, v]) => (
                  <div key={k} className="text-xs">
                    <div className="text-slate-500 capitalize truncate">{k.replace(/_/g, ' ')}</div>
                    <div className="font-semibold text-slate-900">{v}</div>
                  </div>
                ))}
              </div>

              {/* Coverage & Evidence */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div className="p-3 rounded-xl bg-emerald-50/50 border border-emerald-100">
                  <div className="font-semibold text-emerald-900 mb-1">
                    Addressed Requirements ({rec.addressed_req_codes.length})
                  </div>
                  <div className="flex flex-wrap gap-1 mb-2">
                    {rec.addressed_req_codes.map((c) => (
                      <span key={c} className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-mono">
                        {c}
                      </span>
                    ))}
                  </div>
                  {rec.tender_evidence.slice(0, 2).map((ev, i) => (
                    <div key={i} className="text-slate-600 truncate">• {ev}</div>
                  ))}
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                  <div className="font-semibold text-slate-800">Catalogue & Verification Status</div>
                  <div className="text-slate-600">{rec.catalogue_evidence}</div>
                  <div className="text-amber-700 font-medium">
                    Verification: {rec.standard.verification_status} • QCO: {rec.standard.qco_status}
                  </div>
                </div>
              </div>

              {/* Reviewer Actions */}
              <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <input
                  type="text"
                  value={comments[rec.id] || ''}
                  onChange={(e) => setComments({ ...comments, [rec.id]: e.target.value })}
                  placeholder="Add reviewer comment..."
                  className="flex-1 px-3 py-1.5 rounded-lg border border-slate-300 text-xs"
                />
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDecision(rec.id, 'accepted')}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold border ${
                      rec.decision?.decision === 'accepted'
                        ? 'bg-emerald-600 text-white border-emerald-600'
                        : 'bg-white text-emerald-700 border-emerald-300 hover:bg-emerald-50'
                    }`}
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Accept
                  </button>
                  <button
                    onClick={() => handleDecision(rec.id, 'expert_review')}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold border ${
                      rec.decision?.decision === 'expert_review'
                        ? 'bg-amber-600 text-white border-amber-600'
                        : 'bg-white text-amber-700 border-amber-300 hover:bg-amber-50'
                    }`}
                  >
                    <HelpCircle className="w-3.5 h-3.5" />
                    Expert Review
                  </button>
                  <button
                    onClick={() => handleDecision(rec.id, 'rejected')}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold border ${
                      rec.decision?.decision === 'rejected'
                        ? 'bg-red-600 text-white border-red-600'
                        : 'bg-white text-red-700 border-red-300 hover:bg-red-50'
                    }`}
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Reject
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
