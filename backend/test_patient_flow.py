"""Test patient end-to-end flow"""
import urllib.request
import json

BASE_URL = "http://127.0.0.1:8001"

def post_json(url, data):
    payload = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

def get_json(url):
    req = urllib.request.Request(url)
    try:
        resp = urllib.request.urlopen(req)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

print("=" * 60)
print("STEP 1: Create Manual Patient")
print("=" * 60)

payload = {
    "age": 62,
    "gender": "male",
    "symptoms": ["chest pain", "shortness of breath"],
    "bloodPressure": "180/100",
    "heartRate": 115,
    "temperature": 37.4,
    "preExistingConditions": ["hypertension"]
}

status, response = post_json(f"{BASE_URL}/api/patients", payload)
print(f"Status: {status}")
print(f"Response: {json.dumps(response, indent=2)}")

if status == 201:
    patient_id = response.get("patient", {}).get("patientId") or response.get("patientId")
    print(f"\nPatient ID: {patient_id}")
else:
    patient_id = None
    print("\nFAILED to create patient")

print("\n" + "=" * 60)
print("STEP 2: Verify Storage - GET /api/patients")
print("=" * 60)

status, response = get_json(f"{BASE_URL}/api/patients")
print(f"Status: {status}")
print(f"Patient count: {len(response.get('patients', []))}")
if response.get('patients'):
    print(f"First patient: {json.dumps(response['patients'][0], indent=2)[:500]}")

print("\n" + "=" * 60)
print("STEP 3: Verify Analysis Endpoint")
print("=" * 60)

if patient_id:
    status, response = get_json(f"{BASE_URL}/api/patients/{patient_id}/analysis")
    print(f"Status: {status}")
    print(f"Response: {json.dumps(response, indent=2)}")
else:
    print("Skipped - no patient ID")

print("\n" + "=" * 60)
print("STEP 4: Verify Bed Update - GET /api/departments")
print("=" * 60)

status, response = get_json(f"{BASE_URL}/api/departments")
print(f"Status: {status}")
if status == 200:
    for dept in response.get("departments", []):
        print(f"  {dept['name']}: {dept['occupied']}/{dept['total_beds']} beds")

print("\n" + "=" * 60)
print("STEP 5: Verify Admin Analytics")
print("=" * 60)

status, response = get_json(f"{BASE_URL}/api/admin/overview")
print(f"GET /api/admin/overview - Status: {status}")
if status == 200:
    print(f"Response: {json.dumps(response, indent=2)[:500]}")

status, response = get_json(f"{BASE_URL}/api/admin/risk-summary")
print(f"\nGET /api/admin/risk-summary - Status: {status}")
if status == 200:
    print(f"Response: {json.dumps(response, indent=2)[:500]}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
