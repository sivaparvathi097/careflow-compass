"""
Bed availability prediction model for CareFlow AI.
Uses Random Forest with time-series features to predict future bed occupancy.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import warnings

from app.ml.data_generator import HistoricalDataGenerator, data_generator

warnings.filterwarnings("ignore")


class BedPredictor:
    """
    Machine Learning model for predicting future bed availability.
    Uses ensemble methods with temporal feature engineering.
    """
    
    def __init__(self, data_gen: HistoricalDataGenerator = data_generator):
        """
        Initialize predictor with data generator.
        
        Args:
            data_gen: Historical data generator instance
        """
        self._data_gen = data_gen
        self._models: Dict[str, RandomForestRegressor] = {}
        self._label_encoder = LabelEncoder()
        self._is_trained = False
        self._training_metrics: Dict[str, Dict] = {}
        self._feature_importance: Dict[str, Dict] = {}
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for the ML model.
        
        Args:
            df: Raw dataframe with datetime column
            
        Returns:
            DataFrame with engineered features
        """
        features = df.copy()
        
        # Time-based features
        features["hour"] = features["datetime"].dt.hour
        features["day_of_week"] = features["datetime"].dt.dayofweek
        features["day_of_month"] = features["datetime"].dt.day
        features["month"] = features["datetime"].dt.month
        features["week_of_year"] = features["datetime"].dt.isocalendar().week.astype(int)
        features["quarter"] = features["datetime"].dt.quarter
        
        # Cyclical encoding for time features (helps model learn periodic patterns)
        features["hour_sin"] = np.sin(2 * np.pi * features["hour"] / 24)
        features["hour_cos"] = np.cos(2 * np.pi * features["hour"] / 24)
        features["dow_sin"] = np.sin(2 * np.pi * features["day_of_week"] / 7)
        features["dow_cos"] = np.cos(2 * np.pi * features["day_of_week"] / 7)
        features["month_sin"] = np.sin(2 * np.pi * features["month"] / 12)
        features["month_cos"] = np.cos(2 * np.pi * features["month"] / 12)
        
        # Boolean features
        features["is_weekend"] = (features["day_of_week"] >= 5).astype(int)
        features["is_night"] = ((features["hour"] >= 22) | (features["hour"] <= 6)).astype(int)
        features["is_flu_season"] = features["month"].isin([12, 1, 2]).astype(int)
        features["is_summer"] = features["month"].isin([6, 7, 8]).astype(int)
        
        return features
    
    def _get_feature_columns(self) -> List[str]:
        """Get list of feature columns for model training."""
        return [
            "hour", "day_of_week", "day_of_month", "month", "week_of_year", "quarter",
            "hour_sin", "hour_cos", "dow_sin", "dow_cos", "month_sin", "month_cos",
            "is_weekend", "is_night", "is_flu_season", "is_summer", "total_beds"
        ]
    
    def train(self, days: int = 365) -> Dict[str, Dict]:
        """
        Train prediction models for all departments.
        
        Args:
            days: Number of historical days to use for training
            
        Returns:
            Dictionary with training metrics per department
        """
        print("Generating historical data...")
        df = self._data_gen.generate_historical_data(days=days)
        
        print("Training models per department...")
        departments = df["department"].unique()
        
        for dept in departments:
            dept_data = df[df["department"] == dept].copy()
            metrics = self._train_department_model(dept, dept_data)
            self._training_metrics[dept] = metrics
            print(f"  {dept}: MAE={metrics['mae']:.2f}, R²={metrics['r2']:.3f}")
        
        self._is_trained = True
        print("Training complete!")
        return self._training_metrics
    
    def _train_department_model(
        self, 
        department: str, 
        data: pd.DataFrame
    ) -> Dict:
        """
        Train a model for a specific department.
        
        Args:
            department: Department name
            data: Department-specific historical data
            
        Returns:
            Dictionary with training metrics
        """
        # Prepare features
        features_df = self._prepare_features(data)
        feature_cols = self._get_feature_columns()
        
        X = features_df[feature_cols]
        y = features_df["occupancy_rate"]
        
        # Split data (using last 20% as test to respect time ordering)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Train Random Forest model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Store model
        self._models[department] = model
        
        # Calculate metrics
        y_pred = model.predict(X_test)
        metrics = {
            "mae": mean_absolute_error(y_test, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_test, y_pred)),
            "r2": r2_score(y_test, y_pred),
            "samples_trained": len(X_train),
            "samples_tested": len(X_test),
        }
        
        # Feature importance
        importance = dict(zip(feature_cols, model.feature_importances_))
        self._feature_importance[department] = dict(
            sorted(importance.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return metrics
    
    def predict(
        self, 
        department: str, 
        hours_ahead: int = 24
    ) -> List[Dict]:
        """
        Predict bed availability for future hours.
        
        Args:
            department: Department name
            hours_ahead: Number of hours to predict
            
        Returns:
            List of predictions with confidence intervals
        """
        if not self._is_trained:
            self.train()
        
        if department not in self._models:
            raise ValueError(f"Unknown department: {department}")
        
        model = self._models[department]
        config = self._data_gen.DEPT_CONFIG[department]
        total_beds = config["total_beds"]
        
        predictions = []
        now = datetime.now()
        
        for h in range(1, hours_ahead + 1):
            future_time = now + timedelta(hours=h)
            
            # Create feature vector
            features = self._create_feature_vector(future_time, total_beds)
            
            # Get prediction
            pred_occupancy = model.predict([features])[0]
            
            # Calculate confidence interval using tree variance
            tree_predictions = np.array([
                tree.predict([features])[0] for tree in model.estimators_
            ])
            std_dev = np.std(tree_predictions)
            
            # Convert to bed counts
            pred_occupied = int(round(pred_occupancy * total_beds))
            pred_occupied = min(max(pred_occupied, 0), total_beds)
            pred_available = total_beds - pred_occupied
            
            # Confidence bounds (95% CI)
            lower_occupancy = max(0, pred_occupancy - 1.96 * std_dev)
            upper_occupancy = min(1, pred_occupancy + 1.96 * std_dev)
            
            predictions.append({
                "datetime": future_time.isoformat(),
                "hours_ahead": h,
                "predicted_occupied": pred_occupied,
                "predicted_available": pred_available,
                "predicted_occupancy_rate": round(pred_occupancy * 100, 1),
                "confidence_lower": round(lower_occupancy * 100, 1),
                "confidence_upper": round(upper_occupancy * 100, 1),
                "total_beds": total_beds,
            })
        
        return predictions
    
    def _create_feature_vector(
        self, 
        dt: datetime, 
        total_beds: int
    ) -> List[float]:
        """
        Create a feature vector for prediction.
        
        Args:
            dt: Datetime to predict
            total_beds: Total beds in department
            
        Returns:
            List of feature values
        """
        hour = dt.hour
        dow = dt.weekday()
        dom = dt.day
        month = dt.month
        woy = dt.isocalendar()[1]
        quarter = (month - 1) // 3 + 1
        
        return [
            hour,
            dow,
            dom,
            month,
            woy,
            quarter,
            np.sin(2 * np.pi * hour / 24),  # hour_sin
            np.cos(2 * np.pi * hour / 24),  # hour_cos
            np.sin(2 * np.pi * dow / 7),    # dow_sin
            np.cos(2 * np.pi * dow / 7),    # dow_cos
            np.sin(2 * np.pi * month / 12), # month_sin
            np.cos(2 * np.pi * month / 12), # month_cos
            1 if dow >= 5 else 0,           # is_weekend
            1 if hour >= 22 or hour <= 6 else 0,  # is_night
            1 if month in [12, 1, 2] else 0,      # is_flu_season
            1 if month in [6, 7, 8] else 0,       # is_summer
            total_beds,
        ]
    
    def predict_all_departments(
        self, 
        hours_ahead: int = 24
    ) -> Dict[str, List[Dict]]:
        """
        Predict bed availability for all departments.
        
        Args:
            hours_ahead: Number of hours to predict
            
        Returns:
            Dictionary with predictions per department
        """
        if not self._is_trained:
            self.train()
        
        return {
            dept: self.predict(dept, hours_ahead)
            for dept in self._models.keys()
        }
    
    def get_daily_forecast(
        self, 
        department: str, 
        days_ahead: int = 7
    ) -> List[Dict]:
        """
        Get daily aggregated forecast (average per day).
        
        Args:
            department: Department name
            days_ahead: Number of days to forecast
            
        Returns:
            List of daily forecasts
        """
        # Get hourly predictions
        hourly = self.predict(department, hours_ahead=days_ahead * 24)
        
        # Aggregate by day
        daily = {}
        for pred in hourly:
            dt = datetime.fromisoformat(pred["datetime"])
            date_key = dt.date().isoformat()
            
            if date_key not in daily:
                daily[date_key] = {
                    "date": date_key,
                    "predictions": [],
                }
            daily[date_key]["predictions"].append(pred)
        
        # Calculate daily averages
        result = []
        for date_key, data in sorted(daily.items()):
            preds = data["predictions"]
            avg_occupied = np.mean([p["predicted_occupied"] for p in preds])
            avg_available = np.mean([p["predicted_available"] for p in preds])
            avg_rate = np.mean([p["predicted_occupancy_rate"] for p in preds])
            min_available = min(p["predicted_available"] for p in preds)
            max_available = max(p["predicted_available"] for p in preds)
            
            result.append({
                "date": date_key,
                "avg_occupied": round(avg_occupied, 1),
                "avg_available": round(avg_available, 1),
                "avg_occupancy_rate": round(avg_rate, 1),
                "min_available": min_available,
                "max_available": max_available,
                "total_beds": preds[0]["total_beds"],
            })
        
        return result
    
    def get_model_info(self) -> Dict:
        """
        Get information about trained models.
        
        Returns:
            Dictionary with model information
        """
        return {
            "is_trained": self._is_trained,
            "departments": list(self._models.keys()),
            "training_metrics": self._training_metrics,
            "feature_importance": self._feature_importance,
            "model_type": "RandomForestRegressor",
        }


# Singleton instance
bed_predictor = BedPredictor()
