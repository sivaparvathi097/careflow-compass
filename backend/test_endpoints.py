import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_result(test_name, passed, details=""):
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status} | {test_name}")
    if details:
        print(f"  └─ {details}")

def test_health_check():
    print_header("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        passed = (
            response.status_code == 200 and
            response.json().get("status") == "ok" and
            response.json().get("service") == "CareFlow AI Backend"
        )
        print_result("Health Check", passed)
        return passed
    except Exception as e:
        print(f"Error: {e}")
        print_result("Health Check", False, str(e))
        return False

def test_create_patient():
    print_header("TEST 2: Create Patient (Manual Ingestion)")
    
    payload = {
        "name": "John Doe",
        "age": 45,
        "gender": "M",
        "chiefComplaint": "Severe chest pain and shortness of breath",
        "heartRate": 110,
        "bloodPressure": "150/95",
        "temperature": 38.2,
        "respiratoryRate": 22,
        "oxygenSaturation": 94,
        "medicalHistory": ["Hypertension", "Type 2 Diabetes"],
        "currentMedications": ["Lisinopril", "Metformin"]
    }
    
    try:
        print(f"Sending payload:\n{json.dumps(payload, indent=2)}")
        response = requests.post(f"{BASE_URL}/api/patients", json=payload, timeout=30)
        
        print(f"\nStatus: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        patient_data = data.get("patient", data)
        patient_id = patient_data.get("patientId") or data.get("patientId")
        
        checks = {
            "HTTP 201": response.status_code == 201,
            "patientId exists": bool(patient_id),
            "riskScore valid": 0.0 <= data.get("riskScore", -1) <= 1.0,
            "riskLevel valid": data.get("riskLevel") in ["Low", "Medium", "High", "Critical"],
            "department exists": bool(data.get("department")),
            "contributingFactors is list": isinstance(data.get("contributingFactors"), list),
            "reasonSummary exists": bool(data.get("reasonSummary")),
            "confidenceScore valid": 0.0 <= data.get("confidenceScore", -1) <= 1.0
        }
        
        print("\nValidation Checks:")
        for check, result in checks.items():
            print(f"  {'✓' if result else '✗'} {check}")
        
        passed = all(checks.values())
        print_result("Create Patient", passed)
        
        return patient_id if passed else None
        
    except Exception as e:
        print(f"Error: {e}")
        print_result("Create Patient", False, str(e))
        return None

def test_list_patients(expected_patient_id):
    print_header("TEST 3: List Patients")
    
    try:
        response = requests.get(f"{BASE_URL}/api/patients", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        
        patient_count = len(data.get("patients", []))
        print(f"Patients returned: {patient_count}")
        
        if patient_count > 0:
            print(f"\nSample patient (first):\n{json.dumps(data['patients'][0], indent=2)}")
        
        checks = {
            "HTTP 200": response.status_code == 200,
            "patients list exists": "patients" in data,
            "patients is list": isinstance(data.get("patients"), list),
        }
        
        if expected_patient_id:
            patient_ids = [p.get("patientId") for p in data.get("patients", [])]
            checks["created patient in list"] = expected_patient_id in patient_ids
        
        print("\nValidation Checks:")
        for check, result in checks.items():
            print(f"  {'✓' if result else '✗'} {check}")
        
        passed = all(checks.values())
        print_result("List Patients", passed)
        return passed
        
    except Exception as e:
        print(f"Error: {e}")
        print_result("List Patients", False, str(e))
        return False

def test_get_patient_analysis(patient_id):
    print_header("TEST 4: Get Patient Analysis")
    
    if not patient_id:
        print("Skipping: No patient ID from previous test")
        print_result("Get Patient Analysis", False, "No patient ID available")
        return False
    
    try:
        response = requests.get(f"{BASE_URL}/api/patients/{patient_id}/analysis", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response:\n{json.dumps(data, indent=2)}")
        
        checks = {
            "HTTP 200": response.status_code == 200,
            "riskScore exists": "riskScore" in data,
            "riskLevel exists": "riskLevel" in data,
            "department exists": "department" in data,
            "contributingFactors exists": "contributingFactors" in data,
            "reasonSummary exists": "reasonSummary" in data,
            "confidenceScore exists": "confidenceScore" in data,
            "no patient data fields": "name" not in data and "age" not in data
        }
        
        print("\nValidation Checks:")
        for check, result in checks.items():
            print(f"  {'✓' if result else '✗'} {check}")
        
        passed = all(checks.values())
        print_result("Get Patient Analysis", passed)
        return passed
        
    except Exception as e:
        print(f"Error: {e}")
        print_result("Get Patient Analysis", False, str(e))
        return False

def test_realtime_stream():
    print_header("TEST 5: Realtime Streaming (SSE)")
    
    try:
        print("Opening SSE stream (will listen for 15 seconds)...")
        response = requests.get(f"{BASE_URL}/api/patients/realtime", stream=True, timeout=20)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        
        checks = {
            "HTTP 200": response.status_code == 200,
            "Content-Type is SSE": "text/event-stream" in response.headers.get("Content-Type", ""),
        }
        
        events_received = []
        start_time = time.time()
        
        for line in response.iter_lines():
            if time.time() - start_time > 15:
                break
                
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    try:
                        event_data = json.loads(decoded[6:])
                        events_received.append(event_data)
                        print(f"\n📨 Event received at {datetime.now().strftime('%H:%M:%S')}")
                        print(f"   Event type: {event_data.get('event')}")
                        if 'patient' in event_data:
                            print(f"   Patient ID: {event_data['patient'].get('patientId')}")
                            print(f"   Risk Level: {event_data['patient'].get('riskLevel')}")
                    except json.JSONDecodeError:
                        pass
        
        print(f"\nTotal events received: {len(events_received)}")
        
        if events_received:
            checks["events received"] = len(events_received) > 0
            checks["event format valid"] = all(
                e.get("event") == "patient_created" and "patient" in e
                for e in events_received
            )
            checks["patient has patientId"] = all(
                "patientId" in e.get("patient", {})
                for e in events_received
            )
        
        print("\nValidation Checks:")
        for check, result in checks.items():
            print(f"  {'✓' if result else '✗'} {check}")
        
        passed = all(checks.values())
        print_result("Realtime Streaming", passed)
        return passed
        
    except Exception as e:
        print(f"Error: {e}")
        print_result("Realtime Streaming", False, str(e))
        return False

def main():
    print(f"\n{'#'*60}")
    print("#  CareFlow AI Backend - QA Test Suite")
    print(f"#  Target: {BASE_URL}")
    print(f"#  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*60}")
    
    results = []
    
    # Test 1: Health Check
    results.append(test_health_check())
    time.sleep(1)
    
    # Test 2: Create Patient
    patient_id = test_create_patient()
    results.append(patient_id is not None)
    time.sleep(1)
    
    # Test 3: List Patients
    results.append(test_list_patients(patient_id))
    time.sleep(1)
    
    # Test 4: Get Patient Analysis
    results.append(test_get_patient_analysis(patient_id))
    time.sleep(1)
    
    # Test 5: Realtime Streaming
    results.append(test_realtime_stream())
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
