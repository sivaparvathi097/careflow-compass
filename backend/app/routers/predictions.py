"""
Predictions router for CareFlow AI.
API endpoints for bed availability forecasting using ML models.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.ml.bed_predictor import bed_predictor, BedPredictor


# Pydantic models for API responses
class HourlyPrediction(BaseModel):
    """Single hourly prediction."""
    datetime: str
    hours_ahead: int
    predicted_occupied: int
    predicted_available: int
    predicted_occupancy_rate: float
    confidence_lower: float
    confidence_upper: float
    total_beds: int


class DailyForecast(BaseModel):
    """Daily aggregated forecast."""
    date: str
    avg_occupied: float
    avg_available: float
    avg_occupancy_rate: float
    min_available: int
    max_available: int
    total_beds: int


class PredictionResponse(BaseModel):
    """Response for department predictions."""
    department: str
    generated_at: str
    predictions: List[HourlyPrediction]


class DailyForecastResponse(BaseModel):
    """Response for daily forecasts."""
    department: str
    generated_at: str
    forecasts: List[DailyForecast]


class AllDepartmentsPrediction(BaseModel):
    """Predictions for all departments."""
    generated_at: str
    predictions: Dict[str, List[HourlyPrediction]]


class ModelInfoResponse(BaseModel):
    """Model information response."""
    is_trained: bool
    departments: List[str]
    model_type: str
    training_metrics: Dict
    feature_importance: Dict


class TrainingStatus(BaseModel):
    """Training status response."""
    status: str
    message: str


router = APIRouter(
    prefix="/api/predictions",
    tags=["predictions"],
    responses={404: {"description": "Department not found"}},
)


@router.post("/train", response_model=TrainingStatus)
async def train_models(days: int = Query(default=365, ge=30, le=730)):
    """
    Train ML models with historical data.
    
    Args:
        days: Number of historical days to use (30-730)
        
    Returns:
        Training status with metrics
    """
    try:
        metrics = bed_predictor.train(days=days)
        return TrainingStatus(
            status="success",
            message=f"Models trained on {days} days of data. Departments: {list(metrics.keys())}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info():
    """
    Get information about the trained ML models.
    
    Returns:
        Model status, metrics, and feature importance
    """
    info = bed_predictor.get_model_info()
    return ModelInfoResponse(**info)


@router.get("/{department}", response_model=PredictionResponse)
async def get_department_predictions(
    department: str,
    hours: int = Query(default=24, ge=1, le=168, description="Hours to predict (1-168)")
):
    """
    Get hourly bed availability predictions for a department.
    
    Args:
        department: Department name (e.g., "Cardiology")
        hours: Number of hours to predict ahead (max 168 = 1 week)
        
    Returns:
        List of hourly predictions with confidence intervals
    """
    try:
        predictions = bed_predictor.predict(department, hours_ahead=hours)
        return PredictionResponse(
            department=department,
            generated_at=datetime.now().isoformat(),
            predictions=predictions
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/{department}/daily", response_model=DailyForecastResponse)
async def get_daily_forecast(
    department: str,
    days: int = Query(default=7, ge=1, le=14, description="Days to forecast (1-14)")
):
    """
    Get daily aggregated bed availability forecast.
    
    Args:
        department: Department name
        days: Number of days to forecast
        
    Returns:
        Daily forecasts with min/max available beds
    """
    try:
        forecasts = bed_predictor.get_daily_forecast(department, days_ahead=days)
        return DailyForecastResponse(
            department=department,
            generated_at=datetime.now().isoformat(),
            forecasts=forecasts
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


@router.get("", response_model=AllDepartmentsPrediction)
@router.get("/", response_model=AllDepartmentsPrediction)
async def get_all_predictions(
    hours: int = Query(default=24, ge=1, le=72, description="Hours to predict (1-72)")
):
    """
    Get bed availability predictions for all departments.
    
    Args:
        hours: Number of hours to predict ahead
        
    Returns:
        Predictions for each department
    """
    try:
        predictions = bed_predictor.predict_all_departments(hours_ahead=hours)
        return AllDepartmentsPrediction(
            generated_at=datetime.now().isoformat(),
            predictions=predictions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/{department}/peak-hours")
async def get_peak_hours(
    department: str,
    days: int = Query(default=7, ge=1, le=14)
):
    """
    Identify predicted peak occupancy hours for planning.
    
    Args:
        department: Department name
        days: Days to analyze
        
    Returns:
        Peak and low occupancy periods
    """
    try:
        predictions = bed_predictor.predict(department, hours_ahead=days * 24)
        
        # Find peak and low periods
        sorted_by_rate = sorted(predictions, key=lambda x: x["predicted_occupancy_rate"], reverse=True)
        
        peak_hours = sorted_by_rate[:5]  # Top 5 busiest hours
        low_hours = sorted_by_rate[-5:]  # 5 least busy hours
        
        return {
            "department": department,
            "analysis_period_days": days,
            "peak_occupancy_periods": [
                {
                    "datetime": p["datetime"],
                    "occupancy_rate": p["predicted_occupancy_rate"],
                    "available_beds": p["predicted_available"],
                }
                for p in peak_hours
            ],
            "low_occupancy_periods": [
                {
                    "datetime": p["datetime"],
                    "occupancy_rate": p["predicted_occupancy_rate"],
                    "available_beds": p["predicted_available"],
                }
                for p in low_hours
            ],
            "recommendation": _generate_recommendation(peak_hours, low_hours, department),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


def _generate_recommendation(peak: List, low: List, department: str) -> str:
    """Generate staffing/planning recommendation based on predictions."""
    avg_peak_rate = sum(p["predicted_occupancy_rate"] for p in peak) / len(peak)
    avg_low_rate = sum(p["predicted_occupancy_rate"] for p in low) / len(low)
    
    if avg_peak_rate > 85:
        return f"High occupancy predicted for {department}. Consider postponing non-urgent admissions or arranging overflow capacity."
    elif avg_peak_rate > 75:
        return f"Moderate-high occupancy expected. Monitor bed availability closely during peak hours."
    else:
        return f"Occupancy levels appear manageable. Normal staffing should suffice."


# Expose router for imports
predictions_router = router
