import requests, json

BASE = "http://localhost:5000"

# 1. Patient login + fetch
r = requests.post(f"{BASE}/api/patient/auth", json={"patient_id":"P001","biometric_type":"fingerprint","biometric_data":"P001-fingerprint-template","otp":"123456"})
pat_token = r.json()["token"]
pat_h = {"Authorization": f"Bearer {pat_token}"}
requests.post(f"{BASE}/api/patient/P001/fetch-historical", headers=pat_h)

# 2. Generate token + Doctor login
r = requests.post(f"{BASE}/api/patient/P001/generate-access-token", headers=pat_h, json={"doctor_email":"dr.sharma@cityhospital.in","duration_minutes":30})
access_token = r.json()["access_token"]

r = requests.post(f"{BASE}/api/doctor/auth", json={"email":"dr.sharma@cityhospital.in","password":"doctor123"})
doc_token = r.json()["token"]
doc_h = {"Authorization": f"Bearer {doc_token}"}

# 3. Start session
r = requests.post(f"{BASE}/api/doctor/start-session", headers=doc_h, json={"access_token": access_token})
session_id = r.json()["session_id"]
sess_h = {"Authorization": f"Bearer {doc_token}", "Session-Id": session_id}

# 4. Trigger analysis
r = requests.post(f"{BASE}/api/doctor/analyze-patient", headers=sess_h)
print("=== ANALYSIS RESULT ===")
print(json.dumps(r.json(), indent=2))

# 5. Dashboard data
r = requests.get(f"{BASE}/api/doctor/dashboard-data", headers=sess_h)
print("\n=== DASHBOARD DATA ===")
print(json.dumps(r.json(), indent=2))
