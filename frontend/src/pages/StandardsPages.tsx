import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Search, Bookmark, ArrowLeft, ExternalLink } from 'lucide-react';
import { api } from '../services/api';
import type { StandardCatalogueItem } from '../types';

const SECTORS = [
  'All',
  'Lighting',
  'Electrical equipment',
  'Water systems',
  'Mechanical equipment',
  'Medical equipment',
  'Construction',
  'IT equipment',
  'Safety and testing',
];

export const StandardsSearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [sector, setSector] = useState('All');
  const [items, setItems] = useState<StandardCatalogueItem[]>([]);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  const load = () => {
    api.searchStandards(query, sector === 'All' ? '' : sector, '').then((res: any) => setItems(res));
  };

  useEffect(() => {
    load();
    api.listSavedStandards().then((res: any) => {
      setSavedIds(new Set(res.map((s: any) => s.standard_id)));
    });
  }, [sector]);

  const handleSave = async (standardId: number) => {
    await api.saveStandard(standardId);
    setSavedIds((prev) => new Set(prev).add(standardId));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Standards Knowledge Base (Demo)</h1>
        <p className="text-sm text-slate-600">
          Search illustrative demonstration standards. All records are synthetic and not verified against BIS.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && load()}
            placeholder="Search by keyword, product, or DEMO-STD ID..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm"
          />
        </div>
        <select
          value={sector}
          onChange={(e) => setSector(e.target.value)}
          className="px-3 py-2 rounded-lg border border-slate-300 text-sm bg-white"
        >
          {SECTORS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button
          onClick={load}
          className="px-5 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white text-sm font-semibold"
        >
          Search
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {items.map((s) => (
          <div key={s.id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="font-mono text-xs font-bold px-2.5 py-0.5 rounded bg-blue-50 text-blue-700">
                  {s.catalogue_id}
                </span>
                <span className="text-xs text-amber-700 font-medium">{s.verification_status}</span>
              </div>
              <h3 className="font-semibold text-slate-900 mb-1">{s.title}</h3>
              <p className="text-xs text-slate-600 mb-3 line-clamp-2">{s.scope}</p>
              <div className="flex flex-wrap gap-1 mb-3">
                {s.technical_keywords.slice(0, 5).map((kw) => (
                  <span key={kw} className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 text-[11px]">
                    {kw}
                  </span>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <Link
                to={`/standards/${s.id}`}
                className="inline-flex items-center gap-1 text-xs font-semibold text-blue-700 hover:underline"
              >
                View Details <ExternalLink className="w-3.5 h-3.5" />
              </Link>
              <button
                onClick={() => handleSave(s.id)}
                disabled={savedIds.has(s.id)}
                className="inline-flex items-center gap-1 text-xs font-medium text-slate-600 hover:text-blue-700 disabled:text-emerald-600"
              >
                <Bookmark className="w-3.5 h-3.5" />
                {savedIds.has(s.id) ? 'Saved' : 'Save'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const StandardDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [std, setStd] = useState<StandardCatalogueItem | null>(null);

  useEffect(() => {
    api.getStandard(Number(id)).then((res: any) => setStd(res));
  }, [id]);

  if (!std) return <div className="p-8 text-center text-slate-500">Loading standard details...</div>;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <Link to="/standards" className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-700 hover:underline">
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Standards Catalogue
      </Link>
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <span className="font-mono text-sm font-bold px-3 py-1 rounded bg-blue-50 text-blue-700">
            {std.catalogue_id}
          </span>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200">
            {std.verification_status}
          </span>
        </div>
        <h1 className="text-xl font-bold text-slate-900">{std.title}</h1>
        <p className="text-sm text-slate-700">{std.description}</p>
        <div className="grid grid-cols-2 gap-4 text-xs bg-slate-50 p-4 rounded-xl">
          <div><strong>Sector:</strong> {std.sector}</div>
          <div><strong>Category:</strong> {std.product_category}</div>
          <div><strong>Provenance:</strong> {std.source_provenance}</div>
          <div><strong>QCO / Version:</strong> {std.qco_status}</div>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-slate-900 mb-1">Scope</h2>
          <p className="text-sm text-slate-600">{std.scope}</p>
        </div>
        <div>
          <h2 className="text-sm font-semibold text-slate-900 mb-1">Technical Concepts</h2>
          <div className="flex flex-wrap gap-1.5">
            {std.technical_keywords.map((k) => (
              <span key={k} className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 text-xs">{k}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
