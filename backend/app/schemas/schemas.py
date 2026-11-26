from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DemoLoginRequest(BaseModel):
    role: str = Field(..., description="procurement_officer | technical_reviewer | admin")


class UserOut(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    role: str
    department_name: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisCreate(BaseModel):
    title: str
    category: str
    department_name: str
    context_notes: Optional[str] = ""
    pasted_text: Optional[str] = None
    is_sample: bool = False


class RequirementIn(BaseModel):
    id: Optional[int] = None
    req_code: Optional[str] = None
    description: str
    category: str
    keywords: List[str] = []
    units_or_conditions: Optional[str] = None
    criticality: str = "standard"
    source_document: str = "Tender Document"
    source_location: str = "Page 1"
    evidence_text: str = ""
    confidence: float = 0.85
    review_status: str = "edited"
    is_confirmed: bool = True


class RequirementOut(BaseModel):
    id: int
    analysis_id: int
    req_code: str
    description: str
    category: str
    keywords: List[str]
    units_or_conditions: Optional[str]
    criticality: str
    source_document: str
    source_location: str
    evidence_text: str
    confidence: float
    review_status: str
    is_confirmed: bool

    class Config:
        from_attributes = True


class RequirementsBulkUpdate(BaseModel):
    requirements: List[RequirementIn]


class StandardIn(BaseModel):
    catalogue_id: str
    title: str
    sector: str
    product_category: str
    description: str
    scope: str
    technical_keywords: List[str] = []
    related_requirement_categories: List[str] = []
    applicability_conditions: str = ""


class StandardOut(BaseModel):
    id: int
    catalogue_id: str
    title: str
    sector: str
    product_category: str
    description: str
    scope: str
    technical_keywords: List[str]
    related_requirement_categories: List[str]
    applicability_conditions: str
    source_provenance: str
    verification_status: str
    last_checked_status: str
    version_info: str
    qco_status: str
    is_demo: bool

    class Config:
        from_attributes = True


class DecisionIn(BaseModel):
    decision: str  # accepted | rejected | expert_review
    comments: Optional[str] = ""


class RecommendationOut(BaseModel):
    id: int
    analysis_id: int
    standard: StandardOut
    relevance_score: float
    match_label: str
    score_breakdown: Dict[str, Any]
    explanation: str
    addressed_req_codes: List[str]
    unaddressed_req_codes: List[str]
    matching_concepts: List[str]
    tender_evidence: List[str]
    catalogue_evidence: str
    uncertainty_notes: str
    recommended_action: str
    decision: Optional[Dict[str, Any]] = None
