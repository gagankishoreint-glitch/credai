"""
Quick verification script to test the fixed schema
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Login
print("1. Logging in...")
response = requests.post(
    f"{BASE_URL}/token",
    data={"username": "applicant_001", "password": "secret"}
)
print(f"Login Status: {response.status_code}")

if response.status_code != 200:
    print(f"Login failed: {response.text}")
    exit(1)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✓ Login successful\n")

# Test Case: Safe Applicant (without applicant_id and monthly_debt_obligations)
print("2. Testing Safe Applicant (minimal fields)...")
application = {
    "age": 42,
    "annual_income": 95000,
    "credit_score": 750,
    "total_debt": 15000,
    "business_type": "IT"
}

print(f"Request: {json.dumps(application, indent=2)}")

response = requests.post(
    f"{BASE_URL}/decide",
    headers=headers,
    json=application
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    result = response.json()
    print("\n✓ SUCCESS!")
    print(f"  - Applicant ID (auto-generated): {result.get('application_id')}")
    print(f"  - Decision ID: {result.get('decision_id')}")
    print(f"  - Tier: {result.get('tier')}")
    print(f"  - Risk Score (PD): {result.get('risk_score'):.3f}")
    print(f"  - Confidence: {result.get('confidence_score'):.3f}")
    print(f"  - Model Version: {result.get('model_version')}")
else:
    print(f"\n✗ FAILED: {response.json()}")
