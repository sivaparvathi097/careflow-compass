# CareFlow AI – Analytics & Admin Intelligence Module

This module provides hospital-wide analytics and intelligence.

It is fully read-only and aggregates patient data for:

- Risk distribution
- Weekly risk trends
- Symptom pattern trends
- Department load analysis
- Alert generation

No clinical logic.
No diagnosis.
No mutation of patient data.

---

## 🚀 Run Locally

### 1️⃣ Install dependencies

pip install -r requirements.txt

### 2️⃣ Run server

uvicorn app.main:app --reload

Server runs at:
http://127.0.0.1:8000

Swagger docs:
http://127.0.0.1:8000/docs

---

## 📊 Available Endpoints

GET /api/admin/overview  
GET /api/admin/risk-summary  
GET /api/admin/trends/symptoms  
GET /api/admin/trends/weekly-risk  
GET /api/admin/trends/departments  
GET /api/admin/alerts  

---

## 🧠 Data Format Expected

Patient object must contain:

{
  "id": "uuid",
  "timestamp": "2026-02-14T12:45:22",
  "risk_level": "low" | "medium" | "high",
  "symptoms": ["fever", "chest pain"],
  "assigned_department": "Cardiology"
}

---

## 🏥 Architecture Philosophy

Analytics layer is isolated and performs aggregation only.
It does not modify or interfere with triage, ML, or bed assignment logic.

Designed for hackathon demo and production extension.
