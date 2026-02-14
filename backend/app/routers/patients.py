"""
Patient router for CareFlow AI backend.
Handles patient ingestion, listing, and analysis retrieval.
"""

import uuid
from typing import List, Dict

from fastapi import APIRouter, HTTPException

from app.models.patient import PatientInput, Patient, PatientAnalysis
from app.storage.in_memory import InMemoryStorage
from app.services.ml_service import assess_risk
from app.services.department_service import assign_department
from app.services.explainability_service import generate_explanation


router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.post("/", status_code=201)
def create_patient(patient_input: PatientInput):
    """Create new patient with AI risk assessment."""

    # Step 1: ML risk assessment
    risk_result = assess_risk(
        patient_input.age,
        patient_input.gender,
        patient_input.symptoms,
        patient_input.bloodPressure,
        patient_input.heartRate,
        patient_input.temperature,
        patient_input.preExistingConditions
    )

    # Step 2: Department assignment
    department = assign_department(
        patient_input.symptoms,
        patient_input.heartRate,
        patient_input.bloodPressure,
        patient_input.temperature
    )

    # Step 3: Generate explanation
    explanation = generate_explanation(
        risk_result["riskLevel"],
        risk_result["contributingFactors"],
        department
    )

    # Step 4: Create Patient object
    patient = Patient(
        patientId=str(uuid.uuid4()),
        age=patient_input.age,
        gender=patient_input.gender,
        symptoms=patient_input.symptoms,
        bloodPressure=patient_input.bloodPressure,
        heartRate=patient_input.heartRate,
        temperature=patient_input.temperature,
        preExistingConditions=patient_input.preExistingConditions,
        riskScore=risk_result["riskScore"],
        riskLevel=risk_result["riskLevel"],
        department=department,
        contributingFactors=risk_result["contributingFactors"],
        reasonSummary=explanation["reasonSummary"],
        confidenceScore=explanation["confidenceScore"]
    )

    # Step 5: Store patient
    InMemoryStorage.add_patient(patient)

    # Response
    return {
        "patient": patient,
        "riskScore": patient.riskScore,
        "riskLevel": patient.riskLevel,
        "department": patient.department,
        "contributingFactors": patient.contributingFactors,
        "reasonSummary": patient.reasonSummary,
        "confidenceScore": patient.confidenceScore
    }


@router.get("/")
def list_patients() -> Dict[str, List[Patient]]:
    """List all patients."""
    return {"patients": InMemoryStorage.get_all_patients()}


@router.get("/{patient_id}/analysis")
def get_patient_analysis(patient_id: str) -> PatientAnalysis:
    """Get analysis for a specific patient."""
    patient = InMemoryStorage.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return PatientAnalysis(
        riskScore=patient.riskScore,
        riskLevel=patient.riskLevel,
        department=patient.department,
        contributingFactors=patient.contributingFactors,
        reasonSummary=patient.reasonSummary,
        confidenceScore=patient.confidenceScore
    )
