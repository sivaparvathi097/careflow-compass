"""
EMR / EHR extraction service for CareFlow AI.

Extracts clinical data from PDF / TXT / JSON files using
regex + keyword-based rules and converts it into the
standardized PatientInput format used by the ML pipeline.
"""

import re
import json
from typing import Dict, List
from pathlib import Path

import pdfplumber


# -------------------------------------------------
# TEXT EXTRACTION
# -------------------------------------------------

def extract_text_from_file(file_path: str) -> str:
    """
    Extract raw text from EMR files.

    Supported formats:
    - PDF
    - TXT
    - JSON
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _extract_pdf_text(file_path)
    elif ext == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".json":
        return _extract_json_text(file_path)
    else:
        raise ValueError(f"Unsupported EMR file type: {ext}")


def _extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n".join(pages)


def _extract_json_text(json_path: str) -> str:
    """Extract clinical text from common EHR JSON fields."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fields = []
    for key in ["clinical_notes", "history", "observations", "notes", "text"]:
        if key in data:
            fields.append(str(data[key]))

    return "\n".join(fields)


# -------------------------------------------------
# CLINICAL FIELD PARSING
# -------------------------------------------------

def parse_clinical_fields(text: str) -> Dict:
    """
    Parse clinical entities using regex + keyword rules.
    """
    text_lower = text.lower()

    # -------- Age --------
    age_match = re.search(
        r"(?:age|aged|dob)[:\s]*(\d+)|(\d+)\s*(?:years?|yo\b)",
        text_lower
    )
    age = int(age_match.group(1) or age_match.group(2)) if age_match else 50

    # -------- Gender --------
    if "female" in text_lower or " f/" in text_lower:
        gender = "female"
    elif "male" in text_lower or " m/" in text_lower:
        gender = "male"
    else:
        gender = "unknown"

    # -------- Blood Pressure --------
    bp_match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text_lower)
    blood_pressure = f"{bp_match.group(1)}/{bp_match.group(2)}" if bp_match else "120/80"

    # -------- Heart Rate --------
    hr_match = re.search(r"(?:hr|heart rate|bpm)[:\s]*(\d{2,3})", text_lower)
    heart_rate = int(hr_match.group(1)) if hr_match else 80

    # -------- Temperature (C / F handling) --------
    temp_match = re.search(
        r"(?:temp|temperature)[:\s]*(\d+\.?\d*)\s*([cf]?)",
        text_lower
    )
    if temp_match:
        temp_val = float(temp_match.group(1))
        unit = temp_match.group(2)
        # Convert Fahrenheit → Celsius if needed
        if unit == "f" or temp_val > 45:
            temperature = round((temp_val - 32) * 5 / 9, 1)
        else:
            temperature = temp_val
    else:
        temperature = 37.0

    # -------- Symptoms --------
    symptom_triggers = [
        "symptoms",
        "complains of",
        "presents with",
        "chief complaint"
    ]
    symptoms: List[str] = []

    for trigger in symptom_triggers:
        if trigger in text_lower:
            start = text_lower.find(trigger) + len(trigger)
            snippet = text_lower[start:start + 200]
            raw_items = re.split(r"[.,;]", snippet)
            symptoms = [
                s.strip()
                for s in raw_items
                if s.strip()
                and not re.search(r"\d+/\d+|\bbp\b|\bhr\b|\btemp\b", s)
            ]
            break

    if not symptoms:
        symptoms = ["undocumented"]

    # -------- Pre-existing Conditions --------
    condition_triggers = [
        "history of",
        "pmh",
        "past medical history",
        "medical history"
    ]
    known_conditions = [
        "diabetes", "hypertension", "asthma", "copd",
        "cad", "chf", "afib", "cancer", "thyroid"
    ]
    conditions: List[str] = []

    for trigger in condition_triggers:
        if trigger in text_lower:
            start = text_lower.find(trigger) + len(trigger)
            snippet = text_lower[start:start + 200]
            for cond in known_conditions:
                if cond in snippet:
                    conditions.append(cond.title())
            break

    return {
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "bloodPressure": blood_pressure,
        "heartRate": heart_rate,
        "temperature": temperature,
        "preExistingConditions": conditions
    }


# -------------------------------------------------
# NORMALIZATION TO PatientInput
# -------------------------------------------------

def normalize_to_patient_input(parsed: Dict) -> Dict:
    """
    Normalize parsed fields into exact PatientInput schema.
    Ensures ML-safe numeric ranges.
    """
    return {
        "age": max(18, min(90, parsed["age"])),
        "gender": parsed["gender"],
        "symptoms": parsed["symptoms"][:10],
        "bloodPressure": parsed["bloodPressure"],
        "heartRate": max(50, min(150, parsed["heartRate"])),
        "temperature": round(max(36.0, min(40.5, parsed["temperature"])), 1),
        "preExistingConditions": parsed["preExistingConditions"][:5]
    }


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def extract_patient_from_emr(file_path: str) -> Dict:
    """
    End-to-end EMR extraction → standardized PatientInput.

    Output can be passed directly to existing ML + triage pipeline.
    """
    raw_text = extract_text_from_file(file_path)
    parsed = parse_clinical_fields(raw_text)
    return normalize_to_patient_input(parsed)
