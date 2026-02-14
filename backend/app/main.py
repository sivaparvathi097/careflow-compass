# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.admin import router as admin_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="CareFlow AI - Admin Intelligence Module",
        description="""
        This module provides:
        - Hospital-wide risk aggregation
        - Symptom pattern trend analysis
        - Department demand insights
        - Alert generation
        
        No clinical decisions. No patient mutation.
        """,
        version="1.0.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Admin Intelligence Router
    app.include_router(admin_router)

    # Health Check
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "Admin Intelligence",
            "module_owner": "Analytics Layer"
        }

    return app


app = create_app()
