"""
Department service for CareFlow AI.
Orchestrates department operations using BedService for bed management.
"""

from typing import List, Optional
from datetime import datetime
import random

from app.models.department import (
    Department,
    DepartmentWithBeds,
    Ward,
    PatientInQueue,
    PatientQueue,
    RiskLevel,
    DepartmentListResponse,
    DepartmentQueueResponse,
)
from app.services.bed_service import bed_service, BedService


class DepartmentService:
    """
    Service for department management operations.
    Coordinates with BedService for bed-related queries.
    """
    
    # Department descriptions
    _DEPT_DESCRIPTIONS = {
        "Cardiology": "Cardiovascular and heart-related conditions",
        "Neurology": "Nervous system and brain disorders",
        "General Medicine": "General medical conditions and internal medicine",
        "Emergency": "Emergency and trauma care",
        "Gynecology": "Women's health and reproductive care",
    }
    
    # Mock patient queue data for demo (simulates frontend synthetic patients)
    _SYMPTOMS_POOL = [
        "Chest pain", "Headache", "Fever", "Shortness of breath", "Dizziness",
        "Nausea", "Abdominal pain", "Fatigue", "Cough", "Back pain",
        "Palpitations", "Blurred vision", "Joint pain", "Numbness", "Swelling",
    ]
    
    def __init__(self, bed_svc: BedService = bed_service):
        """
        Initialize department service with bed service dependency.
        
        Args:
            bed_svc: BedService instance for bed operations
        """
        self._bed_service = bed_svc
        self._patient_queues: dict[str, List[PatientInQueue]] = {}
        self._initialize_mock_queues()
    
    def _initialize_mock_queues(self):
        """Generate initial mock patient queues for each department."""
        departments = self._bed_service.get_all_department_names()
        for dept in departments:
            self._patient_queues[dept] = self._generate_mock_patients(dept, count=random.randint(3, 8))
    
    def _generate_mock_patients(self, department: str, count: int) -> List[PatientInQueue]:
        """
        Generate mock patients for demonstration purposes.
        
        Args:
            department: Department name
            count: Number of patients to generate
            
        Returns:
            List of mock PatientInQueue objects
        """
        patients = []
        for i in range(count):
            risk_score = random.randint(10, 95)
            if risk_score >= 70:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 40:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            symptoms = ", ".join(random.sample(self._SYMPTOMS_POOL, random.randint(1, 3)))
            
            patient = PatientInQueue(
                id=f"Q-{department[:3].upper()}-{i+1:03d}",
                age=random.randint(18, 85),
                gender=random.choice(["Male", "Female"]),
                symptoms=symptoms,
                arrival_time=datetime.now().strftime("%H:%M:%S"),
                risk_score=risk_score,
                risk_level=risk_level,
                department=department,
            )
            patients.append(patient)
        
        # Sort by risk score descending (higher risk first)
        return sorted(patients, key=lambda p: p.risk_score, reverse=True)
    
    def get_all_departments(self) -> DepartmentListResponse:
        """
        Get all departments with their bed information.
        
        Returns:
            DepartmentListResponse containing all departments
        """
        departments = []
        dept_names = self._bed_service.get_all_department_names()
        
        for name in dept_names:
            dept = self._build_department_with_beds(name)
            departments.append(dept)
        
        return DepartmentListResponse(departments=departments)
    
    def _build_department_with_beds(self, name: str) -> DepartmentWithBeds:
        """
        Build a DepartmentWithBeds object for a given department.
        
        Args:
            name: Department name
            
        Returns:
            DepartmentWithBeds object with full bed details
        """
        wards = self._bed_service.get_wards_for_department(name)
        total_beds = self._bed_service.get_total_beds(name)
        occupied = self._bed_service.get_occupied_beds(name)
        available = self._bed_service.get_available_beds(name)
        occupancy = self._bed_service.get_department_occupancy(name)
        
        return DepartmentWithBeds(
            name=name,
            total_beds=total_beds,
            available=available,
            occupied=occupied,
            wards=wards,
            occupancy_percentage=occupancy,
        )
    
    def get_department(self, name: str) -> Optional[DepartmentWithBeds]:
        """
        Get a specific department by name.
        
        Args:
            name: Department name
            
        Returns:
            DepartmentWithBeds object or None if not found
        """
        dept_names = self._bed_service.get_all_department_names()
        if name not in dept_names:
            return None
        return self._build_department_with_beds(name)
    
    def get_department_queue(self, department_name: str) -> Optional[DepartmentQueueResponse]:
        """
        Get the patient queue for a specific department.
        
        Args:
            department_name: Name of the department
            
        Returns:
            DepartmentQueueResponse or None if department not found
        """
        if department_name not in self._patient_queues:
            # Check if it's a valid department without queue
            if department_name in self._bed_service.get_all_department_names():
                return DepartmentQueueResponse(patients=[])
            return None
        
        return DepartmentQueueResponse(patients=self._patient_queues[department_name])
    
    def add_patient_to_queue(self, department_name: str, patient: PatientInQueue) -> bool:
        """
        Add a patient to a department's queue.
        
        Args:
            department_name: Name of the department
            patient: Patient to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if department_name not in self._bed_service.get_all_department_names():
            return False
        
        if department_name not in self._patient_queues:
            self._patient_queues[department_name] = []
        
        self._patient_queues[department_name].append(patient)
        # Re-sort by risk score
        self._patient_queues[department_name].sort(key=lambda p: p.risk_score, reverse=True)
        return True
    
    def remove_patient_from_queue(self, department_name: str, patient_id: str) -> bool:
        """
        Remove a patient from a department's queue.
        
        Args:
            department_name: Name of the department
            patient_id: ID of patient to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if department_name not in self._patient_queues:
            return False
        
        original_length = len(self._patient_queues[department_name])
        self._patient_queues[department_name] = [
            p for p in self._patient_queues[department_name] if p.id != patient_id
        ]
        return len(self._patient_queues[department_name]) < original_length
    
    def get_department_description(self, name: str) -> Optional[str]:
        """
        Get the description for a department.
        
        Args:
            name: Department name
            
        Returns:
            Description string or None if not found
        """
        return self._DEPT_DESCRIPTIONS.get(name)
    
    def get_high_risk_departments(self, threshold: float = 30.0) -> List[DepartmentWithBeds]:
        """
        Get departments with high-risk patient percentage above threshold.
        
        Args:
            threshold: Minimum percentage of high-risk patients
            
        Returns:
            List of departments exceeding threshold
        """
        high_risk_depts = []
        
        for dept_name, patients in self._patient_queues.items():
            if not patients:
                continue
            high_risk_count = sum(1 for p in patients if p.risk_level == RiskLevel.HIGH)
            high_risk_pct = (high_risk_count / len(patients)) * 100
            
            if high_risk_pct >= threshold:
                dept = self._build_department_with_beds(dept_name)
                high_risk_depts.append(dept)
        
        return high_risk_depts
    
    def get_total_beds_available(self) -> int:
        """
        Get total available beds across all departments.
        
        Returns:
            Total number of available beds
        """
        return self._bed_service.get_total_available_hospital_beds()


# Singleton instance for application-wide use
department_service = DepartmentService()


# Standalone function for patients.py compatibility
def assign_department(symptoms: str, heart_rate: int, blood_pressure: str, temperature: float) -> str:
    """
    Assign a department based on symptoms and vitals.
    Simple rule-based assignment for demo purposes.
    """
    symptoms_lower = symptoms.lower()
    
    # Parse blood pressure
    try:
        systolic, _ = map(int, blood_pressure.split("/"))
    except:
        systolic = 120
    
    # Emergency conditions
    if systolic > 180 or systolic < 90 or heart_rate > 130 or temperature > 39.5:
        return "Emergency"
    
    # Cardiology
    if any(s in symptoms_lower for s in ["chest pain", "palpitation", "heart"]):
        return "Cardiology"
    
    # Neurology
    if any(s in symptoms_lower for s in ["headache", "dizziness", "numbness", "seizure", "vision"]):
        return "Neurology"
    
    # Gynecology
    if any(s in symptoms_lower for s in ["pregnancy", "menstrual", "pelvic"]):
        return "Gynecology"
    
    # Default
    return "General Medicine"
