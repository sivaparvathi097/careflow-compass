"""
Rule-based department assignment service for CareFlow AI.
Pure business logic, no storage or FastAPI dependencies.
"""

from typing import List


def assign_department(
    symptoms: List[str],
    heart_rate: int,
    blood_pressure: str,
    temperature: float
) -> str:
    """
    Assign clinical department based on symptoms and vitals.

    Rules (prioritized):
    - Cardiology: chest pain, abnormal BP, heart_rate > 110
    - Neurology: stroke, seizure, confusion, paralysis
    - Emergency: trauma, accident, bleeding, injury
    - General Medicine: fever >38.5 + infection symptoms
    - Fallback: General Medicine
    """
    symptoms_lower = [s.lower() for s in symptoms]
    bp_lower = blood_pressure.lower()

    # Cardiology
    cardiology_keywords = ["chest pain", "chest", "palpitations"]
    if (
        any(
            keyword in symptom
            for symptom in symptoms_lower
            for keyword in cardiology_keywords
        )
        or heart_rate > 110
        or any(
            indicator in bp_lower
            for indicator in ["hypertension", "hypotension", "high bp", "low bp"]
        )
    ):
        return "Cardiology"

    # Neurology
    neurology_keywords = ["stroke", "seizure", "confusion", "paralysis", "neurological"]
    if any(
        keyword in symptom
        for symptom in symptoms_lower
        for keyword in neurology_keywords
    ):
        return "Neurology"

    # Emergency
    emergency_keywords = ["trauma", "accident", "bleeding", "injury", "fracture"]
    if any(
        keyword in symptom
        for symptom in symptoms_lower
        for keyword in emergency_keywords
    ):
        return "Emergency"

    # General Medicine (fever + infection-like symptoms)
    infection_keywords = ["fever", "infection", "cough", "sore throat", "fatigue"]
    if temperature > 38.5 and any(
        keyword in symptom
        for symptom in symptoms_lower
        for keyword in infection_keywords
    ):
        return "General Medicine"

    # Fallback
    return "General Medicine"
