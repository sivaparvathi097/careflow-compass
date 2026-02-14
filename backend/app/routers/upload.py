"""
EMR / EHR upload router for CareFlow AI.
Handles file upload, extraction, ML triage, and storage.
"""

import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.models.patient import Patient
from app.storage.in_memory import InMemoryStorage
from app.services.emr_extraction_service import extract_patient_from_emr
from app.services.ml_service import assess_risk
from app.services.department_service import assign_department
from app.services.explainability_service import generate_explanation


router = APIRouter(prefix="/api/upload", tags=["Upload"])

TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)


@router.post("/")
async def upload_emr(file: UploadFile = File(...)):
    """
    Upload EMR/EHR file (PDF/TXT/JSON), extract patient data,
    and process using existing ML triage pipeline.
    """
    try:
        # -----------------------------
        # Save uploaded file temporarily
        # -----------------------------
        temp_path = TEMP_DIR / f"{uuid.uuid4()}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # -----------------------------
        # Extract standardized PatientInput
        # -----------------------------
        patient_input = extract_patient_from_emr(str(temp_path))

        # -----------------------------
        # ML Risk Assessment
        # -----------------------------
        risk_result = assess_risk(
            age=patient_input["age"],
            gender=patient_input["gender"],
            symptoms=patient_input["symptoms"],
            blood_pressure=patient_input["bloodPressure"],
            heart_rate=patient_input["heartRate"],
            temperature=patient_input["temperature"],
            pre_existing_conditions=patient_input["preExistingConditions"]
        )

        # -----------------------------
        # Department Assignment
        # -----------------------------
        department = assign_department(
            patient_input["symptoms"],
            patient_input["heartRate"],
            patient_input["bloodPressure"],
            patient_input["temperature"]
        )

        # -----------------------------
        # Explainability
        # -----------------------------
        explanation = generate_explanation(
            risk_result["riskLevel"],
            risk_result["contributingFactors"],
            department
        )

        # -----------------------------
        # Create Patient object
        # -----------------------------
        patient = Patient(
            patientId=str(uuid.uuid4()),
            age=patient_input["age"],
            gender=patient_input["gender"],
            symptoms=patient_input["symptoms"],
            bloodPressure=patient_input["bloodPressure"],
            heartRate=patient_input["heartRate"],
            temperature=patient_input["temperature"],
            preExistingConditions=patient_input["preExistingConditions"],
            riskScore=risk_result["riskScore"],
            riskLevel=risk_result["riskLevel"],
            department=department,
            contributingFactors=risk_result["contributingFactors"],
            reasonSummary=explanation["reasonSummary"],
            confidenceScore=explanation["confidenceScore"]
        )

        # -----------------------------
        # Store patient
        # -----------------------------
        InMemoryStorage.add_patient(patient)

        return {
            "patient": patient,
            "source": "EMR_UPLOAD"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        # Cleanup temp file
        try:
            temp_path.unlink(missing_ok=True)
        except Exception:
            pass
