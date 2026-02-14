"""
Real LLM explainability service using OpenRouter API for CareFlow AI.
Generates clinician-friendly explanations for risk assessments.
"""

import os
import json
import requests
from typing import List, Dict


def generate_explanation(
    risk_level: str,
    contributing_factors: List[str],
    department: str
) -> Dict[str, str | float]:
    """
    Generate LLM-based explanation for patient risk assessment.

    Args:
        risk_level: "Low", "Medium", or "High"
        contributing_factors: List of risk factors
        department: Assigned department

    Returns:
        {"reasonSummary": str, "confidenceScore": float}
    """
    # Normalize risk level
    risk_level = risk_level.title()
    if risk_level == "Critical":
        risk_level = "High"

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return _fallback_explanation(risk_level)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are a medical AI explaining triage decisions to clinicians. "
        "Respond ONLY with valid JSON."
    )

    factors_str = (
        ", ".join(contributing_factors)
        if contributing_factors
        else "clinical indicators from vital signs and symptoms"
    )

    user_prompt = f"""
Risk Level: {risk_level}
Contributing Factors: {factors_str}
Department: {department}

Explain this triage decision for clinicians.

Respond ONLY with this JSON:
{{
  "reasonSummary": "Brief explanation mentioning risk, factors, and department",
  "confidenceScore": 0.0
}}
No markdown or extra text.
"""

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=8)
        response.raise_for_status()

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if not content or "{" not in content:
            return _fallback_explanation(risk_level)

        start = content.find("{")
        end = content.rfind("}") + 1
        result = json.loads(content[start:end])

        confidence = result.get("confidenceScore", 0.8)
        confidence = max(0.0, min(1.0, float(confidence)))

        return {
            "reasonSummary": result.get(
                "reasonSummary",
                f"{risk_level} risk assessment routed to {department}."
            ),
            "confidenceScore": confidence
        }

    except Exception:
        return _fallback_explanation(risk_level)


def _fallback_explanation(risk_level: str) -> Dict[str, str | float]:
    """Deterministic fallback explanation."""
    confidence_map = {
        "Low": 0.75,
        "Medium": 0.85,
        "High": 0.92
    }
    confidence = confidence_map.get(risk_level, 0.8)

    return {
        "reasonSummary": (
            f"{risk_level} risk assessment based on clinical symptoms and vitals. "
            "This supports appropriate and timely triage."
        ),
        "confidenceScore": confidence
    }
