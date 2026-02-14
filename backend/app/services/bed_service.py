"""
Bed management service for CareFlow AI.
Handles bed allocation, availability tracking, and occupancy calculations.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.models.department import Bed, BedStatus, Ward


class BedService:
    """
    Service for managing hospital beds across wards and departments.
    Provides bed allocation, status tracking, and availability queries.
    """
    
    # Static ward data matching frontend mock (for demo purposes)
    _WARD_DATA: Dict[str, List[Ward]] = {
        "Cardiology": [
            Ward(name="CCU", total_beds=12, occupied=9),
            Ward(name="Ward A", total_beds=16, occupied=10),
            Ward(name="Ward B", total_beds=12, occupied=8),
        ],
        "Neurology": [
            Ward(name="Neuro ICU", total_beds=8, occupied=7),
            Ward(name="Ward C", total_beds=14, occupied=8),
        ],
        "General Medicine": [
            Ward(name="Ward D", total_beds=20, occupied=14),
            Ward(name="Ward E", total_beds=20, occupied=16),
            Ward(name="Ward F", total_beds=20, occupied=12),
        ],
        "Emergency": [
            Ward(name="ER Bay", total_beds=15, occupied=13),
            Ward(name="Observation", total_beds=10, occupied=7),
        ],
        "Gynecology": [
            Ward(name="Ward G", total_beds=10, occupied=5),
            Ward(name="Ward H", total_beds=10, occupied=7),
        ],
    }
    
    def __init__(self):
        """Initialize bed service with ward data."""
        self._ward_data = self._WARD_DATA.copy()
        # Admission logs: maps "dept:ward" to list of admission timestamps
        self._admission_logs: Dict[str, List[datetime]] = {}
    
    def get_wards_for_department(self, department_name: str) -> List[Ward]:
        """
        Get all wards for a specific department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            List of Ward objects for the department
        """
        return self._ward_data.get(department_name, [])
    
    def get_total_beds(self, department_name: str) -> int:
        """
        Calculate total beds for a department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            Total number of beds across all wards
        """
        wards = self.get_wards_for_department(department_name)
        return sum(ward.total_beds for ward in wards)
    
    def get_occupied_beds(self, department_name: str) -> int:
        """
        Calculate occupied beds for a department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            Number of occupied beds across all wards
        """
        wards = self.get_wards_for_department(department_name)
        return sum(ward.occupied for ward in wards)
    
    def get_available_beds(self, department_name: str) -> int:
        """
        Calculate available beds for a department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            Number of available beds across all wards
        """
        return self.get_total_beds(department_name) - self.get_occupied_beds(department_name)
    
    def get_department_occupancy(self, department_name: str) -> float:
        """
        Calculate occupancy percentage for a department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            Occupancy percentage (0-100)
        """
        total = self.get_total_beds(department_name)
        if total == 0:
            return 0.0
        occupied = self.get_occupied_beds(department_name)
        return round((occupied / total) * 100, 1)
    
    def get_ward_occupancy(self, department_name: str, ward_name: str) -> Optional[float]:
        """
        Calculate occupancy percentage for a specific ward.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            
        Returns:
            Occupancy percentage or None if ward not found
        """
        wards = self.get_wards_for_department(department_name)
        for ward in wards:
            if ward.name == ward_name:
                return ward.occupancy_percentage
        return None
    
    def allocate_bed(self, department_name: str, ward_name: str, patient_id: str) -> bool:
        """
        Allocate an available bed to a patient.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            patient_id: ID of the patient to assign
            
        Returns:
            True if allocation successful, False otherwise
        """
        wards = self._ward_data.get(department_name, [])
        for i, ward in enumerate(wards):
            if ward.name == ward_name and ward.occupied < ward.total_beds:
                # Update occupied count
                self._ward_data[department_name][i] = Ward(
                    name=ward.name,
                    total_beds=ward.total_beds,
                    occupied=ward.occupied + 1
                )
                return True
        return False
    
    def release_bed(self, department_name: str, ward_name: str, patient_id: str) -> bool:
        """
        Release a bed when patient is discharged.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            patient_id: ID of the patient being discharged
            
        Returns:
            True if release successful, False otherwise
        """
        wards = self._ward_data.get(department_name, [])
        for i, ward in enumerate(wards):
            if ward.name == ward_name and ward.occupied > 0:
                # Update occupied count
                self._ward_data[department_name][i] = Ward(
                    name=ward.name,
                    total_beds=ward.total_beds,
                    occupied=ward.occupied - 1
                )
                return True
        return False
    
    def get_all_department_names(self) -> List[str]:
        """
        Get list of all department names.
        
        Returns:
            List of department name strings
        """
        return list(self._ward_data.keys())
    
    def get_total_hospital_beds(self) -> int:
        """
        Calculate total beds across entire hospital.
        
        Returns:
            Total number of beds in hospital
        """
        total = 0
        for dept_name in self._ward_data:
            total += self.get_total_beds(dept_name)
        return total
    
    def get_total_available_hospital_beds(self) -> int:
        """
        Calculate total available beds across entire hospital.
        
        Returns:
            Total number of available beds in hospital
        """
        available = 0
        for dept_name in self._ward_data:
            available += self.get_available_beds(dept_name)
        return available
    
    def increment_occupied(self, department_name: str, ward_name: str) -> Optional[Ward]:
        """
        Increment occupied bed count for a ward (patient admitted).
        Also logs the admission timestamp for forecast calculations.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            
        Returns:
            Updated Ward object or None if operation failed
        """
        wards = self._ward_data.get(department_name, [])
        for i, ward in enumerate(wards):
            if ward.name == ward_name:
                if ward.occupied < ward.total_beds:
                    updated_ward = Ward(
                        name=ward.name,
                        total_beds=ward.total_beds,
                        occupied=ward.occupied + 1
                    )
                    self._ward_data[department_name][i] = updated_ward
                    # Log admission timestamp for forecast calculations
                    self.log_admission(department_name, ward_name)
                    return updated_ward
                return None  # Already at capacity
        return None  # Ward not found
    
    def decrement_occupied(self, department_name: str, ward_name: str) -> Optional[Ward]:
        """
        Decrement occupied bed count for a ward (patient discharged).
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            
        Returns:
            Updated Ward object or None if operation failed
        """
        wards = self._ward_data.get(department_name, [])
        for i, ward in enumerate(wards):
            if ward.name == ward_name:
                if ward.occupied > 0:
                    updated_ward = Ward(
                        name=ward.name,
                        total_beds=ward.total_beds,
                        occupied=ward.occupied - 1
                    )
                    self._ward_data[department_name][i] = updated_ward
                    return updated_ward
                return None  # Already at 0
        return None  # Ward not found
    
    def get_ward(self, department_name: str, ward_name: str) -> Optional[Ward]:
        """
        Get a specific ward by department and ward name.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            
        Returns:
            Ward object or None if not found
        """
        wards = self._ward_data.get(department_name, [])
        for ward in wards:
            if ward.name == ward_name:
                return ward
        return None
    
    def log_admission(self, department_name: str, ward_name: str) -> None:
        """
        Log an admission timestamp for a ward.
        Should be called every time a bed is allocated.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
        """
        key = f"{department_name}:{ward_name}"
        if key not in self._admission_logs:
            self._admission_logs[key] = []
        self._admission_logs[key].append(datetime.now())
    
    def predict_bed_exhaustion(
        self, 
        department_name: str, 
        ward_name: str
    ) -> Dict[str, Optional[float]]:
        """
        Predict hours until all beds are full based on admission rate.
        Uses current total beds, current occupied beds, and current admission logs.
        
        Args:
            department_name: Name of the department
            ward_name: Name of the ward
            
        Returns:
            Dict with 'forecast_hours': float, None (no data), or 0 (already full)
        """
        ward = self.get_ward(department_name, ward_name)
        if not ward:
            return {"forecast_hours": None}
        
        total = ward.total_beds
        occupied = ward.occupied
        remaining = total - occupied
        
        # Already full
        if remaining <= 0:
            return {"forecast_hours": 0}
        
        # Check admissions in last 1 hour
        key = f"{department_name}:{ward_name}"
        logs = self._admission_logs.get(key, [])
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_admissions = [t for t in logs if t >= one_hour_ago]
        
        rate = len(recent_admissions)
        
        # No data to calculate rate
        if rate == 0:
            return {"forecast_hours": None}
        
        forecast_hours = remaining / rate
        
        return {"forecast_hours": round(forecast_hours, 2)}


# Singleton instance for application-wide use
bed_service = BedService()
