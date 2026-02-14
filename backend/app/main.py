"""
CareFlow AI Backend - FastAPI Application Entry Point.

A sophisticated healthcare triage system API providing:
- Department management with real-time bed availability
- Patient queue management with AI-driven risk assessment
- RESTful endpoints aligned with frontend data expectations
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.departments import departments_router
from app.routers.predictions import predictions_router

# Initialize FastAPI application
app = FastAPI(
    title="CareFlow AI API",
    description="Healthcare Triage System Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(departments_router)
app.include_router(predictions_router)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "CareFlow AI API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs",
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
