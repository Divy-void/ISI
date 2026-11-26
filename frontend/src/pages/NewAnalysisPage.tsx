import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

const CATEGORIES = [
  'Lighting',
  'Electrical equipment',
  'Water systems',
  'Mechanical equipment',
  'Medical equipment',
  'Construction',
  'IT equipment',
  'Safety and testing',
];

const PROCESSING_STEPS = [
  'Uploading document',
  'Extracting document text',
  'Identifying requirements',
  'Normalizing technical terminology',
  'Searching the standards catalogue',
  'Ranking recommendations',
  'Preparing results',
];

export const NewAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Lighting');
  const [department, setDepartment] = useState('Municipal Electrical & Lighting');
  const [contextNotes, setContextNotes] = useState('');
  const [pastedText, setPastedText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [processingStep, setProcessingStep] = useState<number | null>(null);
  const [error, setError] = useState('');

  const handleFileChange = (selected: File | null) => {
    setError('');
    if (!selected) return;
    if (selected.size > 20 * 1024 * 1024) {
      setError('File exceeds maximum size of 20 MB.');
      return;
    }
    setFile(selected);
  };

  const runSample = async () => {
    setError('');
    setProcessingStep(1);
    try {
      const created: any = await api.createAnalysis({
        title: 'Municipal Outdoor LED Street Lighting Procurement',
        category: 'Lighting',
        department_name: 'Municipal Electrical & Lighting',
        context_notes: 'Synthetic demonstration tender.',
        is_sample: true,
      });
      setProcessingStep(3);
      await api.processAnalysis(created.id);
      setProcessingStep(7);
      navigate(`/analyses/${created.id}/requirements`);
    } catch (err: any) {
      setError(err.message || 'Failed to load sample tender');
      setProcessingStep(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!title.trim()) {
      setError('Please enter an analysis name.');
      return;
    }
    if (!file && !pastedText.trim()) {
      setError('Please upload a PDF, DOCX, or TXT file, or paste tender text.');
      return;
    }

    try {
      setProcessingStep(1);
      const created: any = await api.createAnalysis({
        title: title.trim(),
        category,
        department_name: department.trim() || 'General Procurement',
        context_notes: contextNotes.trim(),
        pasted_text: file ? undefined : pastedText.trim(),
        is_sample: false,
      });

      if (file) {
        setProcessingStep(2);
        const uploadRes: any = await api.uploadDocument(created.id, file);
        if (uploadRes.parse_status === 'scanned_fallback') {
          setError(uploadRes.parse_note);
          setProcessingStep(null);
          return;
        }
      }

      setProcessingStep(3);
      await api.processAnalysis(created.id);
      setProcessingStep(7);
      navigate(`/analyses/${created.id}/requirements`);
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
      setProcessingStep(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">New Tender Analysis</h1>
          <p className="text-sm text-slate-600">
            Upload a procurement specification (PDF, DOCX, TXT up to 20 MB) or paste tender text.
          </p>
        </div>
        <button
          type="button"
          onClick={runSample}
          disabled={processingStep !== null}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold"
        >
          <Sparkles className="w-4 h-4" />
          Try Sample Tender
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3 text-sm text-red-800">
          <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {processingStep !== null ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Processing Tender Document...</h2>
          <div className="space-y-3">
            {PROCESSING_STEPS.map((label, idx) => {
              const stepNum = idx + 1;
              const done = processingStep > stepNum;
              const active = processingStep === stepNum;
              return (
                <div key={label} className="flex items-center gap-3 text-sm">
                  <CheckCircle2
                    className={`w-5 h-5 ${
                      done ? 'text-emerald-600' : active ? 'text-blue-600 animate-pulse' : 'text-slate-300'
                    }`}
                  />
                  <span className={done || active ? 'font-medium text-slate-900' : 'text-slate-400'}>
                    {stepNum}. {label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Analysis Name *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Smart City LED Streetlight Tender"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Procurement Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Department</label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Optional Context</label>
              <input
                type="text"
                value={contextNotes}
                onChange={(e) => setContextNotes(e.target.value)}
                placeholder="e.g., Coastal municipality, high humidity"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Drag & Drop File Upload */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Upload Document (PDF, DOCX, TXT • Max 20 MB)
            </label>
            <label
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                handleFileChange(e.dataTransfer.files?.[0] || null);
              }}
              className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-xl p-6 cursor-pointer hover:border-blue-500 hover:bg-blue-50/30 transition-colors"
            >
              <UploadCloud className="w-8 h-8 text-blue-600 mb-2" />
              {file ? (
                <div className="flex items-center gap-2 text-sm font-medium text-slate-900">
                  <FileText className="w-4 h-4 text-blue-600" />
                  {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </div>
              ) : (
                <span className="text-sm text-slate-600">
                  Drag and drop a file here, or <span className="text-blue-700 font-semibold">browse</span>
                </span>
              )}
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
              />
            </label>
          </div>

          {/* Alternative Paste Text */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">
              Or Paste Tender Text Directly
            </label>
            <textarea
              rows={5}
              value={pastedText}
              onChange={(e) => setPastedText(e.target.value)}
              placeholder="Paste technical specification clauses here..."
              className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              className="px-6 py-2.5 rounded-xl bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold shadow-sm"
            >
              Extract Requirements & Continue
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
