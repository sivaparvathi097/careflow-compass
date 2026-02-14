"""
ML risk assessment service for CareFlow AI using trained model.
Adapts existing patient data format to trained ML model input.
"""

from typing import List, Dict

try:
    # ML module may be added later by another teammate
    from app.ml.trained_model import predict_risk
except ImportError:
    predict_risk = None


def assess_risk(
    age: int,
    gender: str,
    symptoms: List[str],
    blood_pressure: str,
    heart_rate: int,
    temperature: float,
    pre_existing_conditions: List[str]
) -> Dict[str, float | str | List[str]]:
    """
    Assess clinical risk using trained ML model.

    Returns:
        {
            "riskScore": float (0.0–1.0),
            "riskLevel": "Low" | "Medium" | "High",
            "contributingFactors": List[str]
        }
    """

    # -----------------------------
    # Parse blood pressure
    # -----------------------------
    try:
        systolic, diastolic = map(int, blood_pressure.split("/"))
    except (ValueError, IndexError):
        systolic, diastolic = 120, 80

    # -----------------------------
    # ML input adapter
    # -----------------------------
    ml_input = {
        "age": age,
        "vitals": {
            "systolic_bp": systolic,
            "diastolic_bp": diastolic,
            "heart_rate": heart_rate,
            "temperature": temperature
        }
    }

    try:
        ml_output = predict_risk(ml_input)

        # Normalize outputs
        risk_score = ml_output["risk_score"] / 100.0
        contributing_factors = [
            f["feature"]
            for f in ml_output.get("top_contributing_features", [])
        ]

        return {
            "riskScore": risk_score,
            "riskLevel": ml_output["risk_level"],
            "contributingFactors": contributing_factors
        }

    except Exception:
        return {
            "riskScore": 0.5,
            "riskLevel": "Medium",
            "contributingFactors": ["model unavailable"]
        }
