from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class PatientInput(BaseModel):
    """Input model used for POST /api/patients."""

    age: int = Field(..., ge=0, le=120, description="Patient age in years.")
    gender: str = Field(..., description="Patient gender as entered by staff.")
    symptoms: List[str] = Field(
        default_factory=list,
        description="List of symptom descriptions.",
    )
    bloodPressure: str = Field(
        ...,
        description="Blood pressure formatted as 'systolic/diastolic', e.g. '120/80'.",
        examples=["120/80", "140/90"],
    )
    heartRate: int = Field(
        ...,
        ge=20,
        le=250,
        description="Heart rate in beats per minute.",
    )
    temperature: float = Field(
        ...,
        ge=30.0,
        le=45.0,
        description="Body temperature in Celsius.",
    )
    preExistingConditions: List[str] = Field(
        default_factory=list,
        description="Known pre-existing medical conditions.",
    )


class PatientAnalysis(BaseModel):
    """AI analysis output model used by /analysis endpoint."""

    riskScore: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Risk score between 0.0 (no risk) and 1.0 (maximum risk).",
    )
    riskLevel: str = Field(
        ...,
        description='Discrete risk level label, e.g. "Low", "Medium", or "High".',
    )
    department: str = Field(
        ...,
        description="Assigned clinical department.",
    )
    contributingFactors: List[str] = Field(
        default_factory=list,
        description="Factors contributing to the risk assessment.",
    )
    reasonSummary: str = Field(
        ...,
        description="Short explanation of the AI assessment.",
    )
    confidenceScore: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence of the assessment between 0.0 and 1.0.",
    )


class Patient(BaseModel):
    """Canonical stored patient model combining core data and AI analysis."""

    patientId: str = Field(
        ...,
        description="Backend-generated UUID string.",
    )

    age: int = Field(..., ge=0, le=120)
    gender: str
    symptoms: List[str]
    bloodPressure: str
    heartRate: int = Field(..., ge=20, le=250)
    temperature: float = Field(..., ge=30.0, le=45.0)
    preExistingConditions: List[str] = Field(default_factory=list)

    riskScore: float = Field(..., ge=0.0, le=1.0)
    riskLevel: str
    department: str
    contributingFactors: List[str] = Field(default_factory=list)
    reasonSummary: str
    confidenceScore: float = Field(..., ge=0.0, le=1.0)


class RealtimePatientPayload(BaseModel):
    """Payload model for WebSocket streaming of new patients."""

    event: str = Field(
        "patient_created",
        description="Event type for the WebSocket message.",
    )
    patient: Patient = Field(
        ...,
        description="Newly created patient record.",
    )
