"""Quick API smoke test — run while api/app.py is serving on port 5000."""
import requests, json

BASE = "http://localhost:5000"

def pp(label, resp):
    print(f"\n{'='*50}")
    print(f"  {label}  [{resp.status_code}]")
    print(f"{'='*50}")
    print(json.dumps(resp.json(), indent=2))

# 1. Health
pp("GET /api/health", requests.get(f"{BASE}/api/health"))

# 2. Patient auth
patient_resp = requests.post(f"{BASE}/api/patient/auth", json={
    "patient_id": "P001",
    "biometric_type": "fingerprint",
    "biometric_data": "P001-fingerprint-template",
    "otp": "123456",
})
pp("POST /api/patient/auth (P001)", patient_resp)
patient_token = patient_resp.json().get("token")

# 3. Doctor auth
doctor_resp = requests.post(f"{BASE}/api/doctor/auth", json={
    "email": "dr.sharma@cityhospital.in",
    "password": "doctor123",
})
pp("POST /api/doctor/auth (Dr. Sharma)", doctor_resp)
doctor_token = doctor_resp.json().get("token")

# 4. Patient fetches own data
pp("GET /api/patient/data", requests.get(
    f"{BASE}/api/patient/data",
    headers={"Authorization": f"Bearer {patient_token}"},
))

# 5. Doctor requests session for P001
session_resp = requests.post(f"{BASE}/api/doctor/session", json={
    "patient_id": "P001",
}, headers={"Authorization": f"Bearer {doctor_token}"})
pp("POST /api/doctor/session (P001)", session_resp)
session_token = session_resp.json().get("session_token")

# 6. Doctor views patient with session token
pp("GET /api/doctor/patient/P001", requests.get(
    f"{BASE}/api/doctor/patient/P001",
    headers={"Authorization": f"Bearer {session_token}"},
))

# 7. Audit log
pp("GET /api/audit/log", requests.get(
    f"{BASE}/api/audit/log",
    headers={"Authorization": f"Bearer {doctor_token}"},
))

# 8. Test: no token → 401
pp("GET /api/patient/data (no token)", requests.get(f"{BASE}/api/patient/data"))

# 9. Test: wrong OTP → 401
pp("POST /api/patient/auth (wrong OTP)", requests.post(f"{BASE}/api/patient/auth", json={
    "patient_id": "P001",
    "biometric_type": "fingerprint",
    "biometric_data": "P001-fingerprint-template",
    "otp": "999999",
}))

print("\n" + "="*50)
print("  ALL SMOKE TESTS COMPLETE")
print("="*50)
