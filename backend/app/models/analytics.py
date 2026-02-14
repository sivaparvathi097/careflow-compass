# app/models/analytics.py

from pydantic import BaseModel
from typing import List, Dict


class OverviewResponse(BaseModel):
    total_patients: int
    low_risk: int
    medium_risk: int
    high_risk: int


class RiskDistributionItem(BaseModel):
    risk_level: str
    count: int
    percentage: float


class RiskSummaryResponse(BaseModel):
    total: int
    distribution: List[RiskDistributionItem]


class SymptomTrendResponse(BaseModel):
    time_window_days: int
    symptom_counts: Dict[str, int]


class WeeklyRiskTrendResponse(BaseModel):
    daily_trend: Dict[str, Dict[str, int]]


class DepartmentTrendResponse(BaseModel):
    department_distribution: Dict[str, int]


class AlertResponse(BaseModel):
    alerts: List[str]
