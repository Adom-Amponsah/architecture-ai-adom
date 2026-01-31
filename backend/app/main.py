from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB, Redis, etc.
    print("Starting up ARchitectureAI...")
    key = settings.OPENAI_API_KEY or ""
    suffix = key[-4:] if len(key) >= 4 else ""
    print(f"OPENAI_API_KEY loaded (suffix): {suffix}")
    yield
    # Shutdown: Close connections
    print("Shutting down ARchitectureAI...")

from app.api.v1.api import api_router
from app.api import deps
from app.models.user import User
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Mock Auth for local development without DB
if settings.MOCK_AUTH:
    print("WARNING: Running with MOCK AUTH enabled (Database not required)")
    async def mock_get_current_active_user():
        # Return a dummy user object that mimics the SQLAlchemy model
        return User(id=1, email="mock@admin.com", is_active=True, is_superuser=True, full_name="Mock Admin")
    
    app.dependency_overrides[deps.get_current_active_user] = mock_get_current_active_user

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to ARchitectureAI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
