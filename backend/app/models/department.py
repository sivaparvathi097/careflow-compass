"""
Department and Ward data models for CareFlow AI.
Defines the core entities for hospital department management.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BedStatus(str, Enum):
    """Status of a hospital bed."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"
    RESERVED = "reserved"


class Bed(BaseModel):
    """Individual bed within a ward."""
    id: int
    status: BedStatus = BedStatus.AVAILABLE
    patient_id: Optional[str] = None
    assigned_at: Optional[datetime] = None


class Ward(BaseModel):
    """Ward within a department containing multiple beds."""
    name: str
    total_beds: int = Field(ge=0, description="Total number of beds in ward")
    occupied: int = Field(ge=0, description="Number of occupied beds")
    
    @property
    def available(self) -> int:
        """Calculate available beds."""
        return self.total_beds - self.occupied
    
    @property
    def occupancy_percentage(self) -> float:
        """Calculate occupancy percentage."""
        if self.total_beds == 0:
            return 0.0
        return round((self.occupied / self.total_beds) * 100, 1)


class Department(BaseModel):
    """Hospital department with associated wards."""
    name: str
    description: Optional[str] = None
    total_beds: int = Field(ge=0, description="Total beds across all wards")
    available: int = Field(ge=0, description="Total available beds")
    occupied: int = Field(ge=0, description="Total occupied beds")
    wards: List[Ward] = []
    
    @property
    def occupancy_percentage(self) -> float:
        """Calculate overall department occupancy."""
        if self.total_beds == 0:
            return 0.0
        return round((self.occupied / self.total_beds) * 100, 1)


class DepartmentWithBeds(BaseModel):
    """Department response model with full bed details."""
    name: str
    total_beds: int
    available: int
    occupied: int
    wards: List[Ward]
    occupancy_percentage: float


class RiskLevel(str, Enum):
    """Patient risk classification levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PatientInQueue(BaseModel):
    """Patient representation for queue listings."""
    id: str
    age: int
    gender: str
    symptoms: str
    arrival_time: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    department: str


class PatientQueue(BaseModel):
    """Response model for department patient queue."""
    department: str
    patients: List[PatientInQueue]
    total_count: int


class DepartmentListResponse(BaseModel):
    """Response model for listing all departments."""
    departments: List[DepartmentWithBeds]


class DepartmentQueueResponse(BaseModel):
    """Response model for department queue endpoint."""
    patients: List[PatientInQueue]
