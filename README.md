# IS-Assist — AI-Powered Indian Standards Recommendation Engine
**Smart India Hackathon 2026 • Problem Statement 26108 • Theme: Smart Automation**

## Overview
IS-Assist is a decision-support platform that helps procurement officers and technical reviewers extract technical requirements from tender documents, map them against a standards catalogue, inspect requirement coverage, and generate traceable recommendation reports.

> **Demonstration Notice:** This local demonstration uses synthetic illustrative standards (`DEMO-STD-001` through `DEMO-STD-014`) marked *"Not verified against BIS"*. Demo authentication is role-based for local demonstration only and is not production-grade.

## Architecture Summary
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, React Router, Lucide Icons (`frontend/`)
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, SQLite (`backend/`)
- **Document Processing:** `pypdf` (PDF), `python-docx` (DOCX), native text (TXT) with scanned-PDF fallback
- **Recommendation Engine:** Deterministic rule-based requirement extraction, curated synonym/concept expansion, hybrid lexical + concept retrieval, transparent 5-component relevance scoring, and requirement coverage matrix.

## Prerequisites
- Python 3.10+ (tested on Python 3.14.6)
- Node.js 18+ and npm (tested on Node v26.7.0)

## Quick Start
```bash
chmod +x run-demo.sh
./run-demo.sh
```
Or run separately:
- **Backend:** `cd backend && .venv/bin/uvicorn main:app --reload --port 8000`
- **Frontend:** `cd frontend && npm run dev -- --port 5173`

Open **http://localhost:5173** in your browser.

## Demo Login & Sample Workflow
1. Select **Procurement Officer**, **Technical Reviewer**, or **Administrator** on `/login`.
2. On the Dashboard, click **Try Sample Tender** (*Municipal Outdoor LED Street Lighting Procurement*).
3. Review/edit extracted requirements and click **Confirm & Generate Recommendations**.
4. Inspect ranked recommendations, score breakdowns, and evidence; open **Coverage Matrix**.
5. Accept/reject recommendations and click **Generate Report** to view printable PDF or download CSV.

## Production Migration Notes
- Replace SQLite with PostgreSQL + `pgvector` for semantic vector search.
- Replace demo `X-Demo-Role` header auth with OIDC/JWT and RBAC.
- Connect authorized BIS standards metadata and QCO lifecycle feeds.
- Add Redis/Celery async workers and private S3-compatible object storage.
