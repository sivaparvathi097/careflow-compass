# app/routers/admin.py

from fastapi import APIRouter, Query
from app.services.analytics_service import AnalyticsService
from app.storage.repository import repository
from app.models.analytics import (
    OverviewResponse,
    RiskSummaryResponse,
    SymptomTrendResponse,
    WeeklyRiskTrendResponse,
    DepartmentTrendResponse,
    AlertResponse,
)

router = APIRouter(prefix="/api/admin", tags=["Admin"])

analytics_service = AnalyticsService(repository)


@router.get("/overview", response_model=OverviewResponse)
def get_overview():
    return analytics_service.get_overview()


@router.get("/risk-summary", response_model=RiskSummaryResponse)
def get_risk_summary():
    return analytics_service.get_risk_summary()


@router.get("/trends/symptoms", response_model=SymptomTrendResponse)
def get_symptom_trends(days: int = Query(7, ge=1, le=60)):
    return analytics_service.get_symptom_trends(days)


@router.get("/trends/weekly-risk", response_model=WeeklyRiskTrendResponse)
def get_weekly_risk_trend():
    return analytics_service.get_weekly_risk_trend()


@router.get("/trends/departments", response_model=DepartmentTrendResponse)
def get_department_trend():
    return analytics_service.get_department_trend()


@router.get("/alerts", response_model=AlertResponse)
def get_alerts():
    return analytics_service.get_alerts()
