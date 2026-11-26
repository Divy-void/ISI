from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(150), nullable=False)
    role = Column(String(40), nullable=False)  # procurement_officer | technical_reviewer | admin
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    department = relationship("Department")


class AnalysisCase(Base):
    __tablename__ = "analysis_cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    department_name = Column(String(120), nullable=False)
    context_notes = Column(Text, default="")
    status = Column(String(50), default="created")
    # created | uploading | extracting | identifying | normalizing | searching | ranking | awaiting_review | completed | failed
    progress_step = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    is_sample = Column(Boolean, default=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    created_by = relationship("User")
    documents = relationship("UploadedDocument", back_populates="analysis", cascade="all, delete-orphan")
    requirements = relationship("ExtractedRequirement", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_cases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf | docx | txt | pasted
    file_size_bytes = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=True)
    extracted_text = Column(Text, default="")
    page_count = Column(Integer, default=1)
    parse_status = Column(String(40), default="pending")  # pending | parsed | scanned_fallback | failed
    parse_note = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), default=utcnow)

    analysis = relationship("AnalysisCase", back_populates="documents")


class ExtractedRequirement(Base):
    __tablename__ = "extracted_requirements"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_cases.id"), nullable=False)
    req_code = Column(String(40), nullable=False)  # e.g., REQ-001
    description = Column(Text, nullable=False)
    category = Column(String(80), nullable=False)
    keywords = Column(JSON, default=list)
    units_or_conditions = Column(String(255), nullable=True)
    criticality = Column(String(30), default="standard")  # critical | high | standard
    source_document = Column(String(255), default="Tender Document")
    source_location = Column(String(120), default="Page 1")
    evidence_text = Column(Text, default="")
    confidence = Column(Float, default=0.85)
    review_status = Column(String(30), default="extracted")  # extracted | edited | confirmed | added
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    analysis = relationship("AnalysisCase", back_populates="requirements")


class StandardCatalogue(Base):
    __tablename__ = "standard_catalogue"

    id = Column(Integer, primary_key=True, index=True)
    catalogue_id = Column(String(40), unique=True, nullable=False, index=True)  # DEMO-STD-001
    title = Column(String(255), nullable=False)
    sector = Column(String(100), nullable=False)
    product_category = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)
    technical_keywords = Column(JSON, default=list)
    related_requirement_categories = Column(JSON, default=list)
    applicability_conditions = Column(Text, default="")
    source_provenance = Column(String(255), default="IS-Assist Synthetic Demonstration Catalogue")
    verification_status = Column(String(80), default="Not verified against BIS")
    last_checked_status = Column(String(80), default="Not verified in demo catalogue")
    version_info = Column(String(80), default="Not verified in demo catalogue")
    qco_status = Column(String(80), default="Not verified in demo catalogue")
    is_demo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_cases.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standard_catalogue.id"), nullable=False)
    relevance_score = Column(Float, nullable=False)  # 0-100 demo relevance score
    match_label = Column(String(50), nullable=False)  # Best Match | Partial Match | Related Standard | Requires Human Review
    score_breakdown = Column(JSON, default=dict)
    explanation = Column(Text, nullable=False)
    addressed_req_codes = Column(JSON, default=list)
    unaddressed_req_codes = Column(JSON, default=list)
    matching_concepts = Column(JSON, default=list)
    tender_evidence = Column(JSON, default=list)
    catalogue_evidence = Column(Text, default="")
    uncertainty_notes = Column(Text, default="")
    recommended_action = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)

    analysis = relationship("AnalysisCase", back_populates="recommendations")
    standard = relationship("StandardCatalogue")
    decision = relationship("ReviewerDecision", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")


class RequirementStandardMapping(Base):
    __tablename__ = "requirement_standard_mappings"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analysis_cases.id"), nullable=False)
    requirement_id = Column(Integer, ForeignKey("extracted_requirements.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standard_catalogue.id"), nullable=False)
    coverage_status = Column(String(40), nullable=False)  # covered | partially_covered | not_covered | needs_review
    evidence_note = Column(Text, default="")
    confidence = Column(Float, default=0.0)


class ReviewerDecision(Base):
    __tablename__ = "reviewer_decisions"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), unique=True, nullable=False)
    decision = Column(String(40), nullable=False)  # accepted | rejected | expert_review | pending
    comments = Column(Text, default="")
    decided_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    recommendation = relationship("Recommendation", back_populates="decision")
    decided_by = relationship("User")


class SavedStandard(Base):
    __tablename__ = "saved_standards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    standard_id = Column(Integer, ForeignKey("standard_catalogue.id"), nullable=False)
    saved_at = Column(DateTime(timezone=True), default=utcnow)

    standard = relationship("StandardCatalogue")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(50), unique=True, nullable=False)
    analysis_id = Column(Integer, ForeignKey("analysis_cases.id"), nullable=False)
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    summary_snapshot = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    analysis = relationship("AnalysisCase", back_populates="reports")
    generated_by = relationship("User")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(80), default="system")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(60), nullable=False)
    entity_id = Column(String(60), nullable=True)
    details = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utcnow)
