"""
In-memory storage for patients using a simple dictionary.
Suitable for hackathon/demo purposes only.
"""

from typing import Dict, List, Optional
from app.models.patient import Patient


class InMemoryStorage:
    """Singleton-like in-memory store for patient data."""

    _patients: Dict[str, Patient] = {}

    @classmethod
    def add_patient(cls, patient: Patient) -> None:
        """Add a new patient to storage, overwriting if patientId already exists."""
        cls._patients[patient.patientId] = patient

    @classmethod
    def get_patient(cls, patient_id: str) -> Optional[Patient]:
        """Retrieve a patient by ID, or None if not found."""
        return cls._patients.get(patient_id)

    @classmethod
    def get_all_patients(cls) -> List[Patient]:
        """Return all stored patients as a list."""
        return list(cls._patients.values())

    @classmethod
    def clear_patients(cls) -> None:
        """Clear all patients from storage (useful for testing/reset)."""
        cls._patients.clear()
