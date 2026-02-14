from fastapi import FastAPI, Body
from app.services.ml_service import predict_risk

app = FastAPI(title="CareFlow AI Backend")


@app.get("/")
def root():
    return {"status": "CareFlow backend running"}


@app.post("/api/ml/predict")
def ml_predict(payload: dict = Body(...)):
    return predict_risk(payload)
