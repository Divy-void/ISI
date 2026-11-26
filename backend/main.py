from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.session import Base, engine, SessionLocal
from app.database.seed import seed_database
from app.api.routes_auth_dashboard import router as auth_dashboard_router
from app.api.routes_analyses import router as analyses_router
from app.api.routes_standards_reports_admin import router as standards_reports_admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="IS-Assist API",
    description="AI-Powered Indian Standards Recommendation Engine (Demonstration Backend)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_dashboard_router)
app.include_router(analyses_router)
app.include_router(standards_reports_admin_router)
