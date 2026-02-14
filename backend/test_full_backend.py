"""
CareFlow AI Backend - Full Integration Test Suite
Tests the running backend without modifying any code
"""

import requests
import json
import time
from datetime import datetime
import io

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} | {name}")
    if details:
        print(f"    {details}")

def test_1_health_check():
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        passed = (
            response.status_code == 200 and
            data.get("status") == "ok"
        )
        print_test("Health Check", passed, f"Service: {data.get('service')}")
        return passed
    except Exception as e:
        print(f"ERROR: {e}")
        print_test("Health Check", False, str(e))
        return False

def test_2_manual_patient_ingestion():
    print_section("TEST 2: Manual Patient Ingestion (POST /api/patients)")
    
    payload = {
        "name": "Jane Smith",
        "age": 67,
        "gender": "F",
        "chiefComplaint": "Severe chest pain radiating to left arm, shortness of breath",
        "heartRate": 125,
        "bloodPressure": "165/95",
        "temperature": 37.8,
        "respiratoryRate": 24,
        "oxygenSaturation": 92,
        "medicalHistory": ["Coronary Artery Disease", "Hypertension"],
        "currentMedications": ["Aspirin", "Lisinopril", "Atorvastatin"]
    }
    
    try:
        print("Sending payload:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/api/patients", 
            json=payload, 
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response:")
        print(json.dumps(data, indent=2))
        
        checks = {
            "HTTP 201 Created": response.status_code == 201,
            "Has patientId": bool(data.get("patient", {}).get("patientId") or data.get("patientId")),
            "Has riskScore": "riskScore" in data,
            "Has riskLevel": "riskLevel" in data,
            "Has department": "department" in data,
            "Has contributingFactors": "contributingFactors" in data,
            "Has reasonSummary": "reasonSummary" in data,
            "Has confidenceScore": "confidenceScore" in data,
        }
        
        print("\n✓ Validation Checks:")
        for check, result in checks.items():
            print(f"  {'✅' if result else '❌'} {check}")
        
        passed = all(checks.values())
        patient_id = data.get("patient", {}).get("patientId") or data.get("patientId")
        
        print_test(
            "Manual Patient Ingestion", 
            passed, 
            f"Patient ID: {patient_id}, Risk: {data.get('riskLevel')}, Dept: {data.get('department')}"
        )
        return passed, patient_id
        
    except Exception as e:
        print(f"ERROR: {e}")
        print_test("Manual Patient Ingestion", False, str(e))
        return False, None

def test_3_list_patients():
    print_section("TEST 3: List Patients (GET /api/patients)")
    
    try:
        response = requests.get(f"{BASE_URL}/api/patients", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        patients = data.get("patients", [])
        count = len(patients)
        print(f"\nTotal patients: {count}")
        
        if count > 0:
            print(f"\nFirst 3 patients:")
            for i, p in enumerate(patients[:3]):
                print(f"\n  Patient {i+1}:")
                print(f"    ID: {p.get('patientId')}")
                print(f"    Age: {p.get('age')}, Gender: {p.get('gender')}")
                print(f"    Risk: {p.get('riskLevel')}, Score: {p.get('riskScore')}")
                print(f"    Department: {p.get('department')}")
        
        checks = {
            "HTTP 200": response.status_code == 200,
            "Has patients array": "patients" in data,
            "Patients is list": isinstance(patients, list),
            "Has patients": count > 0,
        }
        
        print("\n✓ Validation Checks:")
        for check, result in checks.items():
            print(f"  {'✅' if result else '❌'} {check}")
        
        passed = all(checks.values())
        print_test("List Patients", passed, f"Found {count} patient(s)")
        return passed
        
    except Exception as e:
        print(f"ERROR: {e}")
        print_test("List Patients", False, str(e))
        return False

def test_4_realtime_streaming():
    print_section("TEST 4: Real-time Streaming / SSE (GET /api/patients/realtime)")
    
    try:
        print("Opening SSE stream (will listen for 12 seconds)...")
        response = requests.get(
            f"{BASE_URL}/api/patients/realtime", 
            stream=True, 
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        checks = {
            "HTTP 200": response.status_code == 200,
            "Content-Type is SSE": "text/event-stream" in response.headers.get("Content-Type", ""),
        }
        
        events = []
        start_time = time.time()
        
        print("\nListening for events...")
        for line in response.iter_lines():
            if time.time() - start_time > 12:
                break
                
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    try:
                        event_data = json.loads(decoded[6:])
                        events.append(event_data)
                        
                        elapsed = int(time.time() - start_time)
                        print(f"\n  📨 Event #{len(events)} at T+{elapsed}s")
                        print(f"     Type: {event_data.get('event')}")
                        if 'patient' in event_data:
                            p = event_data['patient']
                            print(f"     Patient ID: {p.get('patientId')}")
                            print(f"     Risk: {p.get('riskLevel')}, Dept: {p.get('department')}")
                    except json.JSONDecodeError as e:
                        print(f"     ⚠️  JSON Parse Error: {e}")
        
        print(f"\nTotal events received: {len(events)}")
        
        if events:
            checks["Events received"] = len(events) > 0
            checks["Event format valid"] = all(
                e.get("event") == "patient_created" and "patient" in e
                for e in events
            )
            checks["Patient has ID"] = all(
                "patientId" in e.get("patient", {})
                for e in events
            )
        
        print("\n✓ Validation Checks:")
        for check, result in checks.items():
            print(f"  {'✅' if result else '❌'} {check}")
        
        passed = all(checks.values())
        print_test("Real-time Streaming", passed, f"{len(events)} events in 12 seconds")
        return passed
        
    except Exception as e:
        print(f"ERROR: {e}")
        print_test("Real-time Streaming", False, str(e))
        return False

def test_5_emr_upload():
    print_section("TEST 5: EMR/EHR File Upload (POST /api/upload)")
    
    # Create a sample EMR text file
    emr_content = """
PATIENT MEDICAL RECORD
=====================

Patient Name: Robert Johnson
Age: 58 years
Gender: Male
Date of Visit: 2026-02-14

CHIEF COMPLAINT:
Severe headache, dizziness, and blurred vision for the past 3 hours

VITAL SIGNS:
- Heart Rate: 98 bpm
- Blood Pressure: 185/110 mmHg
- Temperature: 37.2°C
- Respiratory Rate: 18 breaths/min
- Oxygen Saturation: 96%

MEDICAL HISTORY:
- Hypertension (diagnosed 5 years ago)
- Type 2 Diabetes (diagnosed 3 years ago)
- Hyperlipidemia

CURRENT MEDICATIONS:
- Metformin 1000mg twice daily
- Amlodipine 10mg once daily
- Simvastatin 40mg at bedtime

ASSESSMENT:
Patient presenting with hypertensive urgency. Elevated blood pressure with concerning neurological symptoms.

PLAN:
Immediate medical evaluation required. Consider CT scan to rule out intracranial event.
"""
    
    try:
        # Create file-like object
        files = {
            'file': ('patient_record.txt', io.BytesIO(emr_content.encode('utf-8')), 'text/plain')
        }
        
        print("Uploading EMR file: patient_record.txt")
        print(f"File size: {len(emr_content)} bytes")
        
        response = requests.post(
            f"{BASE_URL}/api/upload",
            files=files,
            timeout=30
        )
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response:")
        print(json.dumps(data, indent=2))
        
        checks = {
            "HTTP 200 or 201": response.status_code in [200, 201],
            "Has success indicator": data.get("success") or "patient" in data or "patientId" in data,
        }
        
        # Check for extracted data
        if "patient" in data:
            patient = data["patient"]
            checks["Extracted patient name"] = bool(patient.get("name") or patient.get("patientId"))
            checks["Extracted age"] = patient.get("age") is not None
            checks["Extracted vitals"] = patient.get("heartRate") is not None
            checks["Has risk assessment"] = patient.get("riskLevel") is not None
            checks["Has department"] = patient.get("department") is not None
        
        print("\n✓ Validation Checks:")
        for check, result in checks.items():
            print(f"  {'✅' if result else '❌'} {check}")
        
        passed = all(checks.values())
        
        # Get department and risk from patient object
        dept = "N/A"
        risk = "N/A"
        if "patient" in data:
            dept = data["patient"].get("department", "N/A")
            risk = data["patient"].get("riskLevel", "N/A")
        print_test("EMR Upload & Extraction", passed, f"Risk: {risk}, Dept: {dept}")
        return passed
        
    except Exception as e:
        print(f"ERROR: {e}")
        print_test("EMR Upload & Extraction", False, str(e))
        return False

def main():
    print("\n" + "🏥" * 35)
    print("  CareFlow AI Backend - Full Integration Test")
    print(f"  Target: {BASE_URL}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🏥" * 35)
    
    results = {}
    
    # Test 1: Health Check
    time.sleep(0.5)
    results["Health Check"] = test_1_health_check()
    
    # Test 2: Manual Patient Ingestion
    time.sleep(1)
    manual_pass, patient_id = test_2_manual_patient_ingestion()
    results["Manual Patient Ingestion"] = manual_pass
    
    # Test 3: List Patients
    time.sleep(1)
    results["List Patients"] = test_3_list_patients()
    
    # Test 4: Real-time Streaming
    time.sleep(1)
    results["Real-time Streaming (SSE)"] = test_4_realtime_streaming()
    
    # Test 5: EMR Upload
    time.sleep(1)
    results["EMR/EHR Upload"] = test_5_emr_upload()
    
    # Final Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("\n📊 Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Tests Passed: {passed}/{total}")
    print(f"  Success Rate: {(passed/total)*100:.1f}%")
    print(f"{'='*70}")
    
    # Module validation summary
    print("\n🔍 MODULE VALIDATION:")
    modules = {
        "Patient Ingestion (Manual)": results.get("Manual Patient Ingestion"),
        "Real-time Simulation (SSE)": results.get("Real-time Streaming (SSE)"),
        "EMR/EHR Upload & Extraction": results.get("EMR/EHR Upload"),
        "ML Service with Fallback": results.get("Manual Patient Ingestion"),
        "In-memory Storage": results.get("List Patients"),
        "Safe Router Loading": results.get("Health Check"),
    }
    
    for module, status in modules.items():
        icon = "✅" if status else "❌"
        print(f"  {icon}  {module}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend is fully operational.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
