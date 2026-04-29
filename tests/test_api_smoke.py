"""
test_api_smoke.py — Full API Smoke Test
========================================
Tests all endpoints including the new Patient Portal routes.

Run while api/app.py is serving on port 5000:
    python tests/test_api_smoke.py
"""

import requests
import json
import sys

BASE = "http://localhost:5000"
PASS = 0
FAIL = 0


def pp(label, resp, expect_status=200):
    """Pretty-print a response and track pass/fail."""
    global PASS, FAIL
    status = resp.status_code
    ok = status == expect_status
    tag = "[PASS]" if ok else "[FAIL]"

    if ok:
        PASS += 1
    else:
        FAIL += 1

    print(f"\n{'='*60}")
    print(f"  {tag} {label}  [{status}] (expected {expect_status})")
    print(f"{'='*60}")
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print(resp.text[:500])


# -----------------------------------------------------------------------
# 1. Health Check
# -----------------------------------------------------------------------
pp("GET /api/health", requests.get(f"{BASE}/api/health"))


# -----------------------------------------------------------------------
# 2. Patient Auth (P001)
# -----------------------------------------------------------------------
patient_resp = requests.post(f"{BASE}/api/patient/auth", json={
    "patient_id": "P001",
    "biometric_type": "fingerprint",
    "biometric_data": "P001-fingerprint-template",
    "otp": "123456",
})
pp("POST /api/patient/auth (P001)", patient_resp)
patient_token = patient_resp.json().get("token")

if not patient_token:
    print("\n[FATAL] Could not get patient token. Aborting.")
    sys.exit(1)

PATIENT_HEADERS = {"Authorization": f"Bearer {patient_token}"}


# -----------------------------------------------------------------------
# 3. Doctor Auth
# -----------------------------------------------------------------------
doctor_resp = requests.post(f"{BASE}/api/doctor/auth", json={
    "email": "dr.sharma@cityhospital.in",
    "password": "doctor123",
})
pp("POST /api/doctor/auth (Dr. Sharma)", doctor_resp)
doctor_token = doctor_resp.json().get("token")
DOCTOR_HEADERS = {"Authorization": f"Bearer {doctor_token}"}


# -----------------------------------------------------------------------
# PATIENT PORTAL TESTS
# -----------------------------------------------------------------------

print("\n" + "#" * 60)
print("  PATIENT PORTAL ENDPOINTS")
print("#" * 60)

# 4. Fetch Historical (federated query -> cache)
pp(
    "POST /api/patient/P001/fetch-historical",
    requests.post(f"{BASE}/api/patient/P001/fetch-historical", json={},
                  headers=PATIENT_HEADERS),
)

# 5. Get Cached Data
pp(
    "GET /api/patient/P001/data (after cache)",
    requests.get(f"{BASE}/api/patient/P001/data", headers=PATIENT_HEADERS),
)

# 6. Get Data WITHOUT cache (P002 — never fetched)
patient2_resp = requests.post(f"{BASE}/api/patient/auth", json={
    "patient_id": "P002",
    "biometric_type": "fingerprint",
    "biometric_data": "P002-fingerprint-template",
    "otp": "123456",
})
p2_token = patient2_resp.json().get("token")
pp(
    "GET /api/patient/P002/data (no cache, expect 404)",
    requests.get(f"{BASE}/api/patient/P002/data",
                 headers={"Authorization": f"Bearer {p2_token}"}),
    expect_status=404,
)

# 7. Upload Manual Record (JSON test mode)
pp(
    "POST /api/patient/P001/upload-manual (vaccine card)",
    requests.post(f"{BASE}/api/patient/P001/upload-manual", json={
        "document_type": "vaccine_card",
        "filename": "covid_vaccine_certificate.pdf",
        "file_size": 204800,
    }, headers=PATIENT_HEADERS),
    expect_status=201,
)

# 8. Upload another manual record
pp(
    "POST /api/patient/P001/upload-manual (lab report)",
    requests.post(f"{BASE}/api/patient/P001/upload-manual", json={
        "document_type": "lab_report",
        "filename": "blood_test_jan2024.pdf",
        "file_size": 102400,
    }, headers=PATIENT_HEADERS),
    expect_status=201,
)

# 9. Upload with invalid document type
pp(
    "POST /api/patient/P001/upload-manual (invalid type, expect 400)",
    requests.post(f"{BASE}/api/patient/P001/upload-manual", json={
        "document_type": "xray",
        "filename": "chest_xray.png",
    }, headers=PATIENT_HEADERS),
    expect_status=400,
)

# 10. Verify uploads appear in cached data
resp = requests.get(f"{BASE}/api/patient/P001/data", headers=PATIENT_HEADERS)
pp("GET /api/patient/P001/data (check manual_uploads)", resp)
data = resp.json()
manual_count = len(data.get("manual_uploads", []))
print(f"\n  >> manual_uploads count: {manual_count}")
assert manual_count == 2, f"Expected 2 manual uploads, got {manual_count}"

# 11. Generate Access Token for doctor
pp(
    "POST /api/patient/P001/generate-access-token",
    requests.post(f"{BASE}/api/patient/P001/generate-access-token", json={
        "doctor_id": "DR-SHARMA",
        "duration": 30,
    }, headers=PATIENT_HEADERS),
    expect_status=201,
)

# 12. Generate Access Token — missing doctor_id
pp(
    "POST /api/patient/P001/generate-access-token (no doctor_id, expect 400)",
    requests.post(f"{BASE}/api/patient/P001/generate-access-token", json={},
                  headers=PATIENT_HEADERS),
    expect_status=400,
)

# 13. Patient Audit Log
pp(
    "GET /api/patient/P001/audit-log",
    requests.get(f"{BASE}/api/patient/P001/audit-log", headers=PATIENT_HEADERS),
)

# 14. Access denied — wrong patient
pp(
    "GET /api/patient/P002/data (P001 token, expect 403)",
    requests.get(f"{BASE}/api/patient/P002/data", headers=PATIENT_HEADERS),
    expect_status=403,
)

# 15. Access denied — no token
pp(
    "POST /api/patient/P001/fetch-historical (no token, expect 401)",
    requests.post(f"{BASE}/api/patient/P001/fetch-historical", json={}),
    expect_status=401,
)


# -----------------------------------------------------------------------
# EXISTING ENDPOINT TESTS
# -----------------------------------------------------------------------

print("\n" + "#" * 60)
print("  EXISTING ENDPOINTS")
print("#" * 60)

# 16. Legacy patient data
pp("GET /api/patient/data (legacy)", requests.get(
    f"{BASE}/api/patient/data", headers=PATIENT_HEADERS))

# 17. Doctor session
session_resp = requests.post(f"{BASE}/api/doctor/session", json={
    "patient_id": "P001",
}, headers=DOCTOR_HEADERS)
pp("POST /api/doctor/session", session_resp)
session_token = session_resp.json().get("session_token")

# 18. Doctor views patient
pp("GET /api/doctor/patient/P001", requests.get(
    f"{BASE}/api/doctor/patient/P001",
    headers={"Authorization": f"Bearer {session_token}"}))

# 19. Global audit log
pp("GET /api/audit/log", requests.get(
    f"{BASE}/api/audit/log", headers=DOCTOR_HEADERS))

# 20. Wrong OTP
pp("POST /api/patient/auth (wrong OTP, expect 401)", requests.post(
    f"{BASE}/api/patient/auth", json={
        "patient_id": "P001",
        "biometric_type": "fingerprint",
        "biometric_data": "P001-fingerprint-template",
        "otp": "999999",
    }), expect_status=401)


# -----------------------------------------------------------------------
# SUMMARY
# -----------------------------------------------------------------------
print("\n" + "=" * 60)
print(f"  SMOKE TEST RESULTS: {PASS} passed, {FAIL} failed, {PASS+FAIL} total")
print("=" * 60)

if FAIL > 0:
    print("  [FAIL] Some tests failed!")
    sys.exit(1)
else:
    print("  [PASS] All tests passed!")
    sys.exit(0)
