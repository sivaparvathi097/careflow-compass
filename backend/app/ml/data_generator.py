"""
Synthetic historical data generator for CareFlow AI.
Generates realistic bed occupancy patterns for ML model training.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class HistoricalDataGenerator:
    """
    Generates synthetic historical bed occupancy data with realistic patterns.
    Includes daily, weekly, and seasonal variations per department.
    """
    
    # Department configurations: (total_beds, base_occupancy, volatility)
    DEPT_CONFIG = {
        "Cardiology": {"total_beds": 40, "base_occupancy": 0.68, "volatility": 0.08},
        "Neurology": {"total_beds": 22, "base_occupancy": 0.70, "volatility": 0.10},
        "General Medicine": {"total_beds": 60, "base_occupancy": 0.72, "volatility": 0.12},
        "Emergency": {"total_beds": 25, "base_occupancy": 0.78, "volatility": 0.18},
        "Gynecology": {"total_beds": 20, "base_occupancy": 0.58, "volatility": 0.15},
    }
    
    def __init__(self, seed: int = 42):
        """
        Initialize generator with random seed for reproducibility.
        
        Args:
            seed: Random seed for numpy
        """
        np.random.seed(seed)
    
    def generate_historical_data(
        self, 
        days: int = 365, 
        end_date: datetime = None
    ) -> pd.DataFrame:
        """
        Generate historical bed occupancy data for all departments.
        
        Args:
            days: Number of historical days to generate
            end_date: End date for data (defaults to today)
            
        Returns:
            DataFrame with columns: date, hour, department, total_beds, 
            occupied, available, occupancy_rate
        """
        if end_date is None:
            end_date = datetime.now()
        
        start_date = end_date - timedelta(days=days)
        records = []
        
        # Generate hourly data for each department
        current_date = start_date
        while current_date <= end_date:
            for hour in range(24):
                for dept_name, config in self.DEPT_CONFIG.items():
                    occupied = self._calculate_occupancy(
                        current_date, hour, dept_name, config
                    )
                    total = config["total_beds"]
                    available = total - occupied
                    
                    records.append({
                        "date": current_date.date(),
                        "datetime": current_date.replace(hour=hour),
                        "hour": hour,
                        "day_of_week": current_date.weekday(),
                        "month": current_date.month,
                        "department": dept_name,
                        "total_beds": total,
                        "occupied": occupied,
                        "available": available,
                        "occupancy_rate": occupied / total,
                    })
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(records)
    
    def _calculate_occupancy(
        self, 
        date: datetime, 
        hour: int, 
        department: str, 
        config: Dict
    ) -> int:
        """
        Calculate occupancy for a specific time and department.
        Incorporates multiple realistic patterns.
        
        Args:
            date: Current date
            hour: Hour of day (0-23)
            department: Department name
            config: Department configuration
            
        Returns:
            Number of occupied beds
        """
        base = config["base_occupancy"]
        volatility = config["volatility"]
        total_beds = config["total_beds"]
        
        # 1. Hour-of-day pattern (busier 10am-8pm)
        hour_factor = self._get_hour_factor(hour, department)
        
        # 2. Day-of-week pattern (slightly lower weekends except Emergency)
        dow_factor = self._get_day_of_week_factor(date.weekday(), department)
        
        # 3. Seasonal pattern (flu season, summer variations)
        season_factor = self._get_seasonal_factor(date.month, department)
        
        # 4. Random daily variation
        random_factor = np.random.normal(0, volatility)
        
        # 5. Trend component (slight increase over time for realism)
        days_from_start = (date - datetime(2025, 1, 1)).days
        trend_factor = 0.0001 * days_from_start  # Very gradual increase
        
        # Calculate final occupancy rate
        occupancy_rate = base + hour_factor + dow_factor + season_factor + random_factor + trend_factor
        
        # Clamp between reasonable bounds
        occupancy_rate = np.clip(occupancy_rate, 0.15, 0.98)
        
        # Convert to integer beds
        occupied = int(round(occupancy_rate * total_beds))
        return min(max(occupied, 1), total_beds)
    
    def _get_hour_factor(self, hour: int, department: str) -> float:
        """
        Get hour-of-day adjustment factor.
        Different departments have different daily patterns.
        """
        # Emergency is busier at night
        if department == "Emergency":
            if 22 <= hour or hour <= 6:
                return 0.08
            elif 10 <= hour <= 14:
                return 0.05
            else:
                return 0.0
        
        # Most departments busier during day
        if 9 <= hour <= 18:
            return 0.05
        elif 6 <= hour <= 8 or 19 <= hour <= 21:
            return 0.02
        else:
            return -0.03
    
    def _get_day_of_week_factor(self, dow: int, department: str) -> float:
        """
        Get day-of-week adjustment factor.
        Weekends typically have lower elective admissions.
        """
        # Emergency stays busy on weekends
        if department == "Emergency":
            if dow >= 5:  # Weekend
                return 0.05
            return 0.0
        
        # Other departments lower on weekends
        if dow >= 5:  # Weekend
            return -0.08
        elif dow == 0:  # Monday often busy
            return 0.03
        return 0.0
    
    def _get_seasonal_factor(self, month: int, department: str) -> float:
        """
        Get seasonal adjustment factor.
        Winter months (flu season) typically busier.
        """
        # Flu season (Dec-Feb)
        if month in [12, 1, 2]:
            if department in ["Emergency", "General Medicine"]:
                return 0.12
            return 0.05
        
        # Summer typically lower
        if month in [6, 7, 8]:
            if department == "Emergency":
                return 0.02  # Accidents/injuries
            return -0.05
        
        return 0.0
    
    def generate_department_data(
        self, 
        department: str, 
        days: int = 365
    ) -> pd.DataFrame:
        """
        Generate historical data for a single department.
        
        Args:
            department: Department name
            days: Number of days to generate
            
        Returns:
            DataFrame with historical data
        """
        full_data = self.generate_historical_data(days=days)
        return full_data[full_data["department"] == department].copy()
    
    def get_current_snapshot(self) -> Dict[str, Dict]:
        """
        Get current bed status snapshot for all departments.
        
        Returns:
            Dictionary with current status per department
        """
        now = datetime.now()
        snapshot = {}
        
        for dept_name, config in self.DEPT_CONFIG.items():
            occupied = self._calculate_occupancy(now, now.hour, dept_name, config)
            total = config["total_beds"]
            
            snapshot[dept_name] = {
                "total_beds": total,
                "occupied": occupied,
                "available": total - occupied,
                "occupancy_rate": round(occupied / total * 100, 1),
            }
        
        return snapshot


# Singleton instance
data_generator = HistoricalDataGenerator()
