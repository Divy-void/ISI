import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Plus, Trash2, CheckCircle2, ArrowRight, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';
import type { ExtractedRequirement } from '../types';

const REQ_CATEGORIES = [
  'Product specification',
  'Performance',
  'Electrical',
  'Mechanical',
  'Material',
  'Safety',
  'Environmental',
  'Testing',
  'Certification',
  'Quality assurance',
];

export const RequirementReviewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const analysisId = Number(id);
  const navigate = useNavigate();

  const [analysis, setAnalysis] = useState<any>(null);
  const [requirements, setRequirements] = useState<ExtractedRequirement[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([api.getAnalysis(analysisId), api.getRequirements(analysisId)])
      .then(([a, reqs]: any) => {
        setAnalysis(a);
        setRequirements(reqs);
      })
      .finally(() => setLoading(false));
  }, [analysisId]);

  const updateField = (idx: number, field: keyof ExtractedRequirement, value: any) => {
    setRequirements((prev) =>
      prev.map((r, i) => (i === idx ? { ...r, [field]: value, review_status: 'edited' } : r))
    );
  };

  const deleteReq = (idx: number) => {
    setRequirements((prev) => prev.filter((_, i) => i !== idx));
  };

  const addReq = () => {
    const nextCode = `REQ-${String(requirements.length + 1).padStart(3, '0')}`;
    setRequirements((prev) => [
      ...prev,
      {
        req_code: nextCode,
        description: '',
        category: 'Product specification',
        keywords: [],
        units_or_conditions: '',
        criticality: 'standard',
        source_document: analysis?.document?.filename || 'Manual Entry',
        source_location: 'Manual',
        evidence_text: '',
        confidence: 1.0,
        review_status: 'added',
        is_confirmed: true,
      },
    ]);
  };

  const handleConfirmAndRecommend = async () => {
    setSaving(true);
    try {
      const confirmed = requirements
        .filter((r) => r.description.trim().length > 0)
        .map((r) => ({ ...r, is_confirmed: true }));
      await api.updateRequirements(analysisId, confirmed);
      await api.generateRecommendations(analysisId);
      navigate(`/analyses/${analysisId}/recommendations`);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Loading extracted requirements...</div>;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Review Extracted Requirements</h1>
          <p className="text-sm text-slate-600">
            {analysis?.title} • {requirements.length} requirements extracted
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={addReq}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-sm font-medium text-slate-700"
          >
            <Plus className="w-4 h-4" />
            Add Requirement
          </button>
          <button
            onClick={handleConfirmAndRecommend}
            disabled={saving || requirements.length === 0}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold shadow-sm disabled:opacity-60"
          >
            <CheckCircle2 className="w-4 h-4" />
            {saving ? 'Generating Recommendations...' : 'Confirm & Generate Recommendations'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {requirements.map((req, idx) => (
          <div key={idx} className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-md bg-blue-50 text-blue-700 font-mono text-xs font-semibold">
                  {req.req_code}
                </span>
                <select
                  value={req.category}
                  onChange={(e) => updateField(idx, 'category', e.target.value)}
                  className="text-xs border border-slate-300 rounded-md px-2 py-1 bg-white"
                >
                  {REQ_CATEGORIES.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() =>
                    updateField(idx, 'criticality', req.criticality === 'critical' ? 'standard' : 'critical')
                  }
                  className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    req.criticality === 'critical'
                      ? 'bg-red-50 text-red-700 border border-red-200'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {req.criticality === 'critical' && <AlertTriangle className="w-3 h-3" />}
                  {req.criticality === 'critical' ? 'Critical' : 'Standard'}
                </button>
              </div>
              <div className="flex items-center gap-3 text-xs text-slate-500">
                <span>{req.source_location}</span>
                <button
                  type="button"
                  onClick={() => deleteReq(idx)}
                  className="text-red-600 hover:text-red-800 p-1"
                  title="Delete requirement"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>

            <textarea
              rows={2}
              value={req.description}
              onChange={(e) => updateField(idx, 'description', e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            {req.units_or_conditions && (
              <div className="text-xs text-slate-600">
                <span className="font-semibold">Detected Units/Conditions:</span> {req.units_or_conditions}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
