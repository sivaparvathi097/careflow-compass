# CareFlow AI Backend

A FastAPI-based backend system for patient risk prediction, analytics, and real-time monitoring in healthcare settings.

## 📋 Overview

The CareFlow AI backend is built with FastAPI and provides machine learning-driven risk prediction for patients, along with comprehensive analytics, department management, and real-time monitoring capabilities.

## 🏗️ Architecture

### Core Structure

```
backend/
├── app/
│   ├── core/                 # Configuration & Security
│   │   ├── config.py        # App configuration settings
│   │   ├── security.py      # Authentication & security utilities
│   │   └── dependencies.py  # Dependency injection
│   │
│   ├── models/              # Data Models
│   │   ├── patient.py       # Patient data models
│   │   ├── department.py    # Department models
│   │   └── analytics.py     # Analytics data models
│   │
│   ├── services/            # Business Logic
│   │   ├── ml_service.py                    # ML prediction engine
│   │   ├── analytics_service.py             # Analytics processing
│   │   ├── bed_service.py                   # Bed/room management
│   │   ├── department_service.py            # Department operations
│   │   ├── explainability_service.py        # Model explainability
│   │   ├── simulation_service.py            # Data/scenario simulation
│   │   └── ml_assets/                       # ML model and utilities
│   │       ├── model.pkl                    # Trained XGBoost model
│   │       ├── feature_builder.py          # Feature engineering
│   │       ├── input_adapters.py           # Data input adapters
│   │       ├── vocab.py                    # Symptom/condition vocabularies
│   │       └── __init__.py
│   │
│   ├── routers/             # API Endpoints
│   │   ├── patients.py      # Patient CRUD operations
│   │   ├── departments.py   # Department management
│   │   ├── admin.py         # Admin operations
│   │   ├── realtime.py      # Real-time data endpoints
│   │   └── upload.py        # File upload handling
│   │
│   ├── realtime/            # Real-time Communication
│   │   ├── broadcaster.py   # Message broadcasting
│   │   └── ws_manager.py    # WebSocket management
│   │
│   ├── storage/             # Data Storage
│   │   ├── repository.py    # Data access layer
│   │   └── in_memory.py     # In-memory storage
│   │
│   ├── utils/               # Utilities
│   │   ├── file_parser.py   # File parsing utilities
│   │   └── time_utils.py    # Time-related utilities
│   │
│   └── main.py              # FastAPI application entry point
│
├── ml_training/             # ML Model Training
│   ├── generate_data.py     # Training data generation
│   ├── train_model.py       # Model training pipeline
│   └── train.csv            # Generated training dataset
│
├── test_ml.py              # ML prediction testing script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🤖 Machine Learning System

### Overview
The ML system provides intelligent patient risk assessment using a trained XGBoost classifier that predicts risk levels (Low, Medium, High) based on patient vitals and medical history.

### Key Components

#### 1. **ML Service** (`ml_service.py`)
- Main prediction engine using trained XGBoost model
- Risk Level Classification: Low (0), Medium (1), High (2)
- Risk Scoring: Severity-based scoring from 0-100
- Feature Importance: Identifies top contributing factors

**Features Tracked:**
- Age, systolic/diastolic BP, heart rate, temperature
- Derived features: Mean BP, pulse pressure, shock index
- Boolean flags: Fever flag (temp ≥ 38°C), tachycardia flag (HR > 100)

**Fallback Logic:**
- If model unavailable, uses rule-based fallback:
  - Systolic BP > 170 → High risk
  - Heart rate > 120 → High risk
  - Temperature > 38°C → Medium risk
  - Heart rate > 100 → Medium risk

#### 2. **Feature Builder** (`feature_builder.py`)
Transforms raw patient input into ML-ready features:
- Processes vital signs (BP, HR, temperature)
- Calculates derived metrics (shock index, pulse pressure)
- Encodes symptoms and pre-existing conditions
- Handles feature scaling and normalization

#### 3. **Training Pipeline** (`ml_training/`)

**Data Generation** (`generate_data.py`)
- Generates 15,000 synthetic patient records
- Symptoms: chest pain, fever, breathlessness, dizziness
- Conditions: hypertension, diabetes, asthma
- Labels based on learnable patterns from vital signs

**Model Training** (`train_model.py`)
- Algorithm: XGBoost Classifier
- Configuration:
  - Estimators: 600
  - Max depth: 6
  - Learning rate: 0.07
  - Subsample ratio: 0.9
- Train/test split: 80/20 with stratification
- Evaluation: Macro F1-score
- Output: Serialized model as `model.pkl`

#### 4. **Input Adapters** (`input_adapters.py`)
- CSV parsing for bulk patient data
- JSON parsing for API inputs
- Standardized data format conversion

#### 5. **Vocabularies** (`vocab.py`)
- Standard symptom list for consistent encoding
- Standard condition list for consistent encoding
- Extensible for future symptoms/conditions

### Sample Patient Input Format
```json
{
  "demographics": {
    "age": 60,
    "gender": "Male"
  },
  "symptoms": ["chest pain", "breathlessness"],
  "vitals": {
    "systolic_bp": 180,
    "diastolic_bp": 100,
    "heart_rate": 115,
    "temperature": 37.5
  },
  "pre_existing_conditions": ["hypertension"]
}
```

### Risk Prediction Response
```json
{
  "risk_level": "High",
  "risk_score": 85.5,
  "risk_class_id": 2,
  "top_contributing_features": [
    {"feature": "sys", "value": 180, "impact": "high"},
    {"feature": "hr", "value": 115, "impact": "high"},
    {"feature": "temp", "value": 37.5, "impact": "high"}
  ]
}
```

## 📡 API Endpoints

### Main Application (`main.py`)
- `GET /` - Health check endpoint
- `POST /api/ml/predict` - Risk prediction for patient data

### Router Categories

**Patients Router** (`routers/patients.py`)
- Patient record management
- CRUD operations for patient data

**Departments Router** (`routers/departments.py`)
- Department operations
- Department information management

**Admin Router** (`routers/admin.py`)
- Administrative operations
- System configuration

**Real-time Router** (`routers/realtime.py`)
- Live data streaming
- Real-time updates and notifications

**Upload Router** (`routers/upload.py`)
- File upload handling
- Bulk data import

## 🔄 Real-time Features

### WebSocket Management (`realtime/`)
- **WebSocket Manager** (`ws_manager.py`) - Manages WebSocket connections
- **Message Broadcaster** (`broadcaster.py`) - Broadcasts real-time updates to connected clients

## 💾 Data Storage

### Storage Layer (`storage/`)
- **Repository Pattern** (`repository.py`) - Abstract data access layer
- **In-Memory Storage** (`in_memory.py`) - Fast in-memory database

## 🛠️ Utilities

### File Parsing (`utils/file_parser.py`)
- CSV/JSON file parsing for patient data
- Data format validation

### Time Utilities (`utils/time_utils.py`)
- Time formatting and conversions
- Timestamp operations

## 🔐 Security & Configuration

### Core Module (`core/`)
- **Configuration** (`config.py`) - Application settings and environment variables
- **Security** (`security.py`) - Authentication, authorization, encryption utilities
- **Dependencies** (`dependencies.py`) - Dependency injection for FastAPI

## 🚀 Features Implemented

### ✅ Machine Learning
- [x] XGBoost-based risk prediction model
- [x] Feature engineering pipeline
- [x] Model training and evaluation
- [x] Synthetic data generation for training
- [x] Rule-based fallback prediction
- [x] Risk scoring (0-100 scale)
- [x] Feature importance tracking

### ✅ Data Management
- [x] Patient data models
- [x] Department management
- [x] Analytics data structures
- [x] In-memory storage system
- [x] Repository data access pattern

### ✅ API Services
- [x] Machine learning service with prediction
- [x] Analytics service for data analysis
- [x] Bed management service
- [x] Department operations service
- [x] Model explainability service
- [x] Simulation service

### ✅ Real-time Capabilities
- [x] WebSocket connection management
- [x] Message broadcasting system
- [x] Real-time data streaming endpoints

### ✅ API Routes
- [x] Patient endpoints
- [x] Department endpoints
- [x] Admin operations
- [x] Real-time data endpoints
- [x] File upload handling

### ✅ Utilities & Infrastructure
- [x] File parsing utilities
- [x] Time utilities
- [x] Security and authentication setup
- [x] Configuration management
- [x] Input adapters for data conversion

## 📊 Testing

**ML Testing Script** (`test_ml.py`)
- Sample patient data for model testing
- Demonstrates prediction endpoint usage
- Validates end-to-end ML pipeline

## 🔧 Technology Stack

- **Framework:** FastAPI
- **ML:** XGBoost, scikit-learn, joblib
- **Data:** Pandas
- **Real-time:** WebSocket support
- **Storage:** In-memory storage with repository pattern

## 📦 Dependencies

See `requirements.txt` for complete Python dependencies including:
- FastAPI
- XGBoost
- scikit-learn
- Pandas
- joblib
- And supporting libraries

## 🎯 Next Steps & Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Advanced explainability features
- [ ] More sophisticated analytics
- [ ] Performance optimization
- [ ] Additional validation rules
- [ ] Enhanced error handling
- [ ] API documentation (Swagger UI)
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] Deployment pipeline

## 📝 Notes

- The ML model requires proper feature order consistency between training and inference
- Fallback prediction logic ensures service availability if model loading fails
- All feature engineering is deterministic for reproducible predictions
- Risk scores are calibrated for clinical interpretation
