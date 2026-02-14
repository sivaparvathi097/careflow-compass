"""
Simulation service for CareFlow AI.
Generates synthetic patients for real-time streaming demo.
"""

import random
import uuid
from typing import Dict, List

from app.models.patient import Patient
from app.storage.in_memory import InMemoryStorage
from app.services.ml_service import assess_risk
from app.services.department_service import assign_department
from app.services.explainability_service import generate_explanation


def generate_synthetic_patient_input() -> Dict:
    """
    Generate realistic synthetic PatientInput data.
    Returns dict matching PatientInput schema.
    """
    genders = ["Male", "Female", "Other"]
    ages = list(range(18, 90))

    symptom_sets = {
        "cardiac": ["chest pain", "shortness of breath", "palpitations"],
        "neuro": ["severe headache", "confusion", "vision changes"],
        "trauma": ["fall", "bleeding", "leg injury"],
        "infection": ["fever", "cough", "fatigue"],
        "general": ["abdominal pain", "nausea", "dizziness"]
    }

    condition_type = random.choice(list(symptom_sets.keys()))
    symptoms = random.sample(
        symptom_sets[condition_type],
        k=random.randint(1, len(symptom_sets[condition_type]))
    )

    heart_rate = random.randint(60, 140)
    temperature = round(random.uniform(36.5, 39.5), 1)

    blood_pressure = random.choice(
        ["120/80", "140/90", "160/100", "100/60", "90/50"]
    )

    pre_conditions = ["Hypertension", "Diabetes", "Asthma", None]
    pre_existing = random.choice(pre_conditions)

    return {
        "age": random.choice(ages),
        "gender": random.choice(genders),
        "symptoms": symptoms,
        "bloodPressure": blood_pressure,
        "heartRate": heart_rate,
        "temperature": temperature,
        "preExistingConditions": [pre_existing] if pre_existing else []
    }


def create_simulated_patient() -> Patient:
    """
    Create fully processed synthetic patient using real ML pipeline.
    Stores in memory and returns Patient object.
    """
    patient_input = generate_synthetic_patient_input()

    # Real ML pipeline
    risk_result = assess_risk(
        patient_input["age"],
        patient_input["gender"],
        patient_input["symptoms"],
        patient_input["bloodPressure"],
        patient_input["heartRate"],
        patient_input["temperature"],
        patient_input["preExistingConditions"]
    )

    department = assign_department(
        patient_input["symptoms"],
        patient_input["heartRate"],
        patient_input["bloodPressure"],
        patient_input["temperature"]
    )

    explanation = generate_explanation(
        risk_result["riskLevel"],
        risk_result["contributingFactors"],
        department
    )

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

    InMemoryStorage.add_patient(patient)
    return patient
