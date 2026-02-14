"""
JSON-based persistence for department ward bed data.
Provides reusable functions for loading, saving, and updating ward data.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


# Path to the JSON database file
DB_FILE_PATH = Path(__file__).parent.parent / "data" / "departments_db.json"


def load_departments_db() -> Dict[str, Any]:
    """
    Load the departments database from JSON file.
    
    Returns:
        Dictionary containing all department/ward data.
        Returns empty structure if file doesn't exist or is invalid.
    """
    try:
        if not DB_FILE_PATH.exists():
            return {"last_updated": None, "departments": {}}
        
        with open(DB_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading departments DB: {e}")
        return {"last_updated": None, "departments": {}}


def save_departments_db(data: Dict[str, Any]) -> bool:
    """
    Save the departments database to JSON file.
    Updates the timestamp automatically.
    
    Args:
        data: Dictionary containing all department/ward data.
        
    Returns:
        True if save successful, False otherwise.
    """
    try:
        # Update timestamp
        data["last_updated"] = datetime.now().isoformat()
        
        # Ensure directory exists
        DB_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        with open(DB_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving departments DB: {e}")
        return False


def update_ward_capacity(
    department_name: str, 
    ward_name: str, 
    new_total: int
) -> Optional[Dict[str, Any]]:
    """
    Update the total bed capacity for a specific ward.
    Reads current values from JSON, updates total, and saves back.
    
    Args:
        department_name: Name of the department
        ward_name: Name of the ward
        new_total: New total bed capacity
        
    Returns:
        Updated ward data dict, or None if department/ward not found.
    """
    data = load_departments_db()
    departments = data.get("departments", {})
    
    # Check if department exists
    if department_name not in departments:
        print(f"Department '{department_name}' not found")
        return None
    
    dept_data = departments[department_name]
    wards = dept_data.get("wards", [])
    
    # Find and update the ward
    for ward in wards:
        if ward.get("name") == ward_name:
            # Read current occupied (don't hardcode)
            current_occupied = ward.get("occupied", 0)
            
            # Update total and recalculate available
            ward["total"] = new_total
            ward["available"] = max(0, new_total - current_occupied)
            
            # Adjust occupied if it exceeds new total
            if current_occupied > new_total:
                ward["occupied"] = new_total
                ward["available"] = 0
            
            # Save back to file
            save_departments_db(data)
            return ward
    
    print(f"Ward '{ward_name}' not found in department '{department_name}'")
    return None


def update_ward_occupied(
    department_name: str,
    ward_name: str,
    change: int
) -> Optional[Dict[str, Any]]:
    """
    Increment or decrement occupied beds for a ward.
    
    Args:
        department_name: Name of the department
        ward_name: Name of the ward
        change: +1 for admission, -1 for discharge
        
    Returns:
        Updated ward data dict, or None if operation failed.
    """
    data = load_departments_db()
    departments = data.get("departments", {})
    
    if department_name not in departments:
        return None
    
    dept_data = departments[department_name]
    wards = dept_data.get("wards", [])
    
    for ward in wards:
        if ward.get("name") == ward_name:
            current_total = ward.get("total", 0)
            current_occupied = ward.get("occupied", 0)
            new_occupied = current_occupied + change
            
            # Bounds check
            if new_occupied < 0 or new_occupied > current_total:
                return None
            
            ward["occupied"] = new_occupied
            ward["available"] = current_total - new_occupied
            
            # Log admission timestamp if incrementing
            if change > 0:
                admission_logs = dept_data.get("admission_logs", [])
                admission_logs.append({
                    "ward": ward_name,
                    "timestamp": datetime.now().isoformat()
                })
                dept_data["admission_logs"] = admission_logs
            
            save_departments_db(data)
            return ward
    
    return None


def get_ward_data(department_name: str, ward_name: str) -> Optional[Dict[str, Any]]:
    """
    Get current data for a specific ward.
    
    Args:
        department_name: Name of the department
        ward_name: Name of the ward
        
    Returns:
        Ward data dict, or None if not found.
    """
    data = load_departments_db()
    departments = data.get("departments", {})
    
    if department_name not in departments:
        return None
    
    wards = departments[department_name].get("wards", [])
    for ward in wards:
        if ward.get("name") == ward_name:
            return ward
    
    return None


def get_department_data(department_name: str) -> Optional[Dict[str, Any]]:
    """
    Get all data for a specific department.
    
    Args:
        department_name: Name of the department
        
    Returns:
        Department data dict, or None if not found.
    """
    data = load_departments_db()
    departments = data.get("departments", {})
    return departments.get(department_name)


def get_all_departments() -> Dict[str, Any]:
    """
    Get all departments data.
    
    Returns:
        Dictionary of all departments.
    """
    data = load_departments_db()
    return data.get("departments", {})
