from app.services.ml_service import predict_risk

sample = {
  "demographics": {"age": 60, "gender": "Male"},
  "symptoms": ["chest pain"],
  "vitals": {
    "systolic_bp": 180,
    "diastolic_bp": 100,
    "heart_rate": 115,
    "temperature": 37.5
  },
  "pre_existing_conditions": ["hypertension"]
}

print(predict_risk(sample))
