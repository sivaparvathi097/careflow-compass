"""
Departments router for CareFlow AI.
RESTful API endpoints for department and bed management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
from pydantic import BaseModel

from app.models.department import (
    DepartmentListResponse,
    DepartmentQueueResponse,
    DepartmentWithBeds,
    PatientInQueue,
    Ward,
)
from app.services.department_service import department_service
from app.services.bed_service import bed_service


# Response model for bed updates
class WardUpdateResponse(BaseModel):
    """Response for ward bed count updates."""
    department: str
    ward_name: str
    total_beds: int
    occupied: int
    available: int
    occupancy_percentage: float
    message: str


router = APIRouter(
    prefix="/api/departments",
    tags=["departments"],
    responses={404: {"description": "Department not found"}},
)


@router.get("", response_model=DepartmentListResponse)
@router.get("/", response_model=DepartmentListResponse)
async def get_all_departments() -> DepartmentListResponse:
    """
    Get all departments with bed availability information.
    
    Returns a list of all departments including:
    - Ward details
    - Bed availability
    - Occupancy percentages
    """
    return department_service.get_all_departments()


@router.get("/{department_name}", response_model=DepartmentWithBeds)
async def get_department(department_name: str) -> DepartmentWithBeds:
    """
    Get a specific department by name.
    
    Args:
        department_name: Name of the department (e.g., "Cardiology")
        
    Returns:
        Department details with bed information
        
    Raises:
        HTTPException 404 if department not found
    """
    dept = department_service.get_department(department_name)
    if dept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{department_name}' not found",
        )
    return dept


@router.get("/{department_name}/queue", response_model=DepartmentQueueResponse)
async def get_department_queue(department_name: str) -> DepartmentQueueResponse:
    """
    Get the patient queue for a specific department.
    
    Returns patients ordered by risk score (highest first).
    
    Args:
        department_name: Name of the department
        
    Returns:
        List of patients in queue with risk assessments
        
    Raises:
        HTTPException 404 if department not found
    """
    queue = department_service.get_department_queue(department_name)
    if queue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{department_name}' not found",
        )
    return queue


@router.post("/{department_name}/queue", status_code=status.HTTP_201_CREATED)
async def add_patient_to_queue(department_name: str, patient: PatientInQueue):
    """
    Add a patient to a department's queue.
    
    Args:
        department_name: Name of the department
        patient: Patient data to add
        
    Returns:
        Success message with patient ID
        
    Raises:
        HTTPException 404 if department not found
    """
    success = department_service.add_patient_to_queue(department_name, patient)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{department_name}' not found",
        )
    return {"message": "Patient added to queue", "patient_id": patient.id}


@router.delete("/{department_name}/queue/{patient_id}")
async def remove_patient_from_queue(department_name: str, patient_id: str):
    """
    Remove a patient from a department's queue.
    
    Args:
        department_name: Name of the department
        patient_id: ID of the patient to remove
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404 if department or patient not found
    """
    success = department_service.remove_patient_from_queue(department_name, patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' not found in department '{department_name}'",
        )
    return {"message": "Patient removed from queue", "patient_id": patient_id}


@router.get("/{department_name}/beds/available")
async def get_available_beds(department_name: str):
    """
    Get available bed count for a department.
    
    Args:
        department_name: Name of the department
        
    Returns:
        Available bed count and total beds
    """
    dept = department_service.get_department(department_name)
    if dept is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department '{department_name}' not found",
        )
    return {
        "department": department_name,
        "available": dept.available,
        "total": dept.total_beds,
        "occupancy_percentage": dept.occupancy_percentage,
    }


@router.post("/{department_name}/wards/{ward_name}/increment", response_model=WardUpdateResponse)
async def increment_occupied_beds(department_name: str, ward_name: str):
    """
    Increment occupied bed count for a ward (patient admitted).
    
    Args:
        department_name: Name of the department
        ward_name: Name of the ward
        
    Returns:
        Updated ward information
    """
    updated_ward = bed_service.increment_occupied(department_name, ward_name)
    if updated_ward is None:
        existing_ward = bed_service.get_ward(department_name, ward_name)
        if existing_ward is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ward '{ward_name}' not found in department '{department_name}'",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ward '{ward_name}' is at full capacity",
        )
    
    return WardUpdateResponse(
        department=department_name,
        ward_name=updated_ward.name,
        total_beds=updated_ward.total_beds,
        occupied=updated_ward.occupied,
        available=updated_ward.total_beds - updated_ward.occupied,
        occupancy_percentage=updated_ward.occupancy_percentage,
        message="Bed occupied successfully",
    )


@router.post("/{department_name}/wards/{ward_name}/decrement", response_model=WardUpdateResponse)
async def decrement_occupied_beds(department_name: str, ward_name: str):
    """
    Decrement occupied bed count for a ward (patient discharged).
    
    Args:
        department_name: Name of the department
        ward_name: Name of the ward
        
    Returns:
        Updated ward information
    """
    updated_ward = bed_service.decrement_occupied(department_name, ward_name)
    if updated_ward is None:
        existing_ward = bed_service.get_ward(department_name, ward_name)
        if existing_ward is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ward '{ward_name}' not found in department '{department_name}'",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ward '{ward_name}' has no occupied beds to release",
        )
    
    return WardUpdateResponse(
        department=department_name,
        ward_name=updated_ward.name,
        total_beds=updated_ward.total_beds,
        occupied=updated_ward.occupied,
        available=updated_ward.total_beds - updated_ward.occupied,
        occupancy_percentage=updated_ward.occupancy_percentage,
        message="Bed released successfully",
    )


# Expose router as departments_router for imports
departments_router = router
