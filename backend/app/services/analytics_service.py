# app/services/analytics_service.py

from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional


class AnalyticsService:

    def __init__(self, repository):
        self.repository = repository

    def _parse_timestamp(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _normalize_risk_level(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        normalized = value.strip().lower()
        if normalized in {"low", "medium", "high"}:
            return normalized
        return None

    # -----------------------------------
    # 1️⃣ Overview
    # -----------------------------------
    def get_overview(self) -> Dict:
        patients = self.repository.get_all_patients()
        total = len(patients)

        risk_counts = Counter(
            risk for risk in (self._normalize_risk_level(p.get("risk_level")) for p in patients) if risk
        )

        return {
            "total_patients": total,
            "low_risk": risk_counts.get("low", 0),
            "medium_risk": risk_counts.get("medium", 0),
            "high_risk": risk_counts.get("high", 0),
        }

    # -----------------------------------
    # 2️⃣ Risk Summary (Pie Chart)
    # -----------------------------------
    def get_risk_summary(self) -> Dict:
        patients = self.repository.get_all_patients()
        normalized_levels = [
            self._normalize_risk_level(p.get("risk_level")) for p in patients
        ]
        risk_counts = Counter(risk for risk in normalized_levels if risk)
        total = sum(risk_counts.values())

        distribution = []
        for level in ["low", "medium", "high"]:
            count = risk_counts.get(level, 0)
            percentage = round((count / total) * 100, 2) if total else 0.0
            distribution.append(
                {
                    "risk_level": level,
                    "count": count,
                    "percentage": percentage,
                }
            )

        return {"total": total, "distribution": distribution}

    # -----------------------------------
    # 3️⃣ Symptom Pattern Trends
    # -----------------------------------
    def get_symptom_trends(self, days: int = 7) -> Dict:
        patients = self.repository.get_all_patients()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        symptom_counter = Counter()

        for p in patients:
            patient_time = self._parse_timestamp(p.get("timestamp"))
            if not patient_time or patient_time < cutoff:
                continue
            for symptom in p.get("symptoms", []):
                symptom_counter[symptom.lower()] += 1

        return {
            "time_window_days": days,
            "symptom_counts": dict(symptom_counter),
        }

    # -----------------------------------
    # 4️⃣ Weekly Risk Trend
    # -----------------------------------
    def get_weekly_risk_trend(self) -> Dict:
        patients = self.repository.get_all_patients()

        trend = defaultdict(lambda: {"low": 0, "medium": 0, "high": 0})

        for p in patients:
            patient_time = self._parse_timestamp(p.get("timestamp"))
            risk_level = self._normalize_risk_level(p.get("risk_level"))
            if not patient_time or not risk_level:
                continue
            date = patient_time.date().isoformat()
            trend[date][risk_level] += 1

        return {"daily_trend": dict(trend)}

    # -----------------------------------
    # 5️⃣ Department Trend
    # -----------------------------------
    def get_department_trend(self) -> Dict:
        patients = self.repository.get_all_patients()

        dept_counter = Counter(
            p.get("assigned_department") for p in patients if p.get("assigned_department")
        )

        return {"department_distribution": dict(dept_counter)}

    # -----------------------------------
    # 6️⃣ Alerts
    # -----------------------------------
    def get_alerts(self) -> Dict:
        overview = self.get_overview()
        alerts = []

        if overview["high_risk"] > overview["medium_risk"]:
            alerts.append("High-risk patients exceed medium-risk patients.")

        if overview["total_patients"] > 100:
            alerts.append("Patient load exceeding safe capacity threshold.")

        return {"alerts": alerts}
