export type DemoRole = 'procurement_officer' | 'technical_reviewer' | 'admin';

export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: DemoRole;
  department_name?: string;
}

export interface DashboardStats {
  total_documents_processed: number;
  standards_identified: number;
  analyses_awaiting_review: number;
  saved_standards: number;
  catalogue_count: number;
}

export interface AnalysisSummary {
  id: number;
  title: string;
  category: string;
  department_name: string;
  status: string;
  is_sample: boolean;
  filename?: string;
  requirements_count?: number;
  recommendations_count?: number;
  created_at: string;
}

export interface ExtractedRequirement {
  id?: number;
  analysis_id?: number;
  req_code: string;
  description: string;
  category: string;
  keywords: string[];
  units_or_conditions?: string | null;
  criticality: string;
  source_document: string;
  source_location: string;
  evidence_text: string;
  confidence: number;
  review_status: string;
  is_confirmed: boolean;
}

export interface StandardCatalogueItem {
  id: number;
  catalogue_id: string;
  title: string;
  sector: string;
  product_category: string;
  description: string;
  scope: string;
  technical_keywords: string[];
  related_requirement_categories: string[];
  applicability_conditions: string;
  source_provenance: string;
  verification_status: string;
  last_checked_status: string;
  version_info: string;
  qco_status: string;
  is_demo: boolean;
}

export interface RecommendationItem {
  id: number;
  analysis_id: number;
  relevance_score: number;
  match_label: string;
  score_breakdown: Record<string, number>;
  explanation: string;
  addressed_req_codes: string[];
  unaddressed_req_codes: string[];
  matching_concepts: string[];
  tender_evidence: string[];
  catalogue_evidence: string;
  uncertainty_notes: string;
  recommended_action: string;
  standard: {
    id: number;
    catalogue_id: string;
    title: string;
    sector: string;
    product_category: string;
    verification_status: string;
    version_info: string;
    qco_status: string;
    source_provenance: string;
  };
  decision?: {
    decision: string;
    comments: string;
    decided_at?: string;
  } | null;
}

export interface CoverageMatrixData {
  columns: {
    standard_id: number;
    catalogue_id: string;
    title: string;
    relevance_score: number;
  }[];
  rows: {
    requirement_id: number;
    req_code: string;
    description: string;
    category: string;
    criticality: string;
    cells: {
      standard_id: number;
      catalogue_id: string;
      coverage_status: 'covered' | 'partially_covered' | 'not_covered' | 'needs_review';
      evidence_note: string;
      confidence: number;
    }[];
  }[];
  uncovered_critical: {
    req_code: string;
    description: string;
    category: string;
  }[];
}
