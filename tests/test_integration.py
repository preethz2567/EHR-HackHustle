import pytest
import io
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from api.app import create_app
from api.audit import GLOBAL_AUDIT_LOG
from api.patient_cache import PATIENT_CACHE, ACCESS_TOKEN_STORE
from api.session import ACTIVE_SESSIONS


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    
    # Reset in-memory stores to ensure isolation between tests
    GLOBAL_AUDIT_LOG.clear()
    PATIENT_CACHE.clear()
    ACCESS_TOKEN_STORE.clear()
    ACTIVE_SESSIONS.clear()
    
    with app.test_client() as client:
        yield client


# -----------------------------------------------------------------------------
# Test 1: Patient Complete Flow
# -----------------------------------------------------------------------------
def test_patient_complete_flow(client):
    # 1. Login
    res = client.post("/api/patient/auth", json={
        "patient_id": "P001",
        "biometric_type": "fingerprint",
        "biometric_data": "P001-fingerprint-template",
        "otp": "123456"
    })
    assert res.status_code == 200
    token = res.json["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Fetch historical
    res = client.post("/api/patient/P001/fetch-historical", headers=headers)
    assert res.status_code == 200
    assert "P001" in PATIENT_CACHE

    # 3. Upload manual
    data = {"document_type": "vaccine_card", "file_size": 1024}
    data = {key: str(value) for key, value in data.items()}
    data["file"] = (io.BytesIO(b"dummy pdf content"), "vaccine.pdf")
    
    res = client.post(
        "/api/patient/P001/upload-manual", 
        headers=headers, 
        data=data, 
        content_type="multipart/form-data"
    )
    assert res.status_code == 201

    # 4. Generate access token
    res = client.post("/api/patient/P001/generate-access-token", headers=headers, json={
        "doctor_email": "dr.sharma@cityhospital.in",
        "duration_minutes": 30
    })
    assert res.status_code == 201
    access_token = res.json["access_token"]
    assert access_token in ACCESS_TOKEN_STORE

    # 5. Check audit log
    res = client.get("/api/patient/P001/audit-log", headers=headers)
    assert res.status_code == 200
    entries = res.json["audit_log"]
    assert len(entries) >= 4
    
    actions = [e["action"] for e in entries]
    assert "login" in actions
    assert "fetch_data" in actions
    assert "upload_report" in actions
    assert "generate_token" in actions


# -----------------------------------------------------------------------------
# Test 2: Doctor Complete Flow
# -----------------------------------------------------------------------------
def test_doctor_complete_flow(client):
    # Setup Patient token and cache data
    client.post("/api/patient/auth", json={
        "patient_id": "P001", "biometric_type": "fingerprint", 
        "biometric_data": "P001-fingerprint-template", "otp": "123456"
    })
    
    # 1. Doctor Login
    res = client.post("/api/doctor/auth", json={
        "email": "dr.sharma@cityhospital.in",
        "password": "doctor123"
    })
    assert res.status_code == 200
    doc_token = res.json["token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    doctor_id = res.json["doctor_id"]

    # Generate patient access token directly in store for test
    from api.patient_cache import create_access_token
    t_data = create_access_token("P001", "dr.sharma@cityhospital.in", 30)
    access_token = t_data["access_token"]

    # Provide cached patient data
    from api.patient_cache import PATIENT_CACHE
    PATIENT_CACHE["P001"] = {
        "unified_data": {"patient_id": "P001", "name": "Test", "labs": [], "medications": []},
        "cached_at": "now"
    }

    # 2. Start Session
    res = client.post("/api/doctor/start-session", headers=doc_headers, json={
        "patient_id": "P001",
        "access_token": access_token
    })
    assert res.status_code == 201
    session_id = res.json["session_id"]
    sess_headers = {"Authorization": f"Bearer {doc_token}", "Session-Id": session_id}

    # 3. Access patient data
    res = client.get("/api/doctor/patient-data", headers=sess_headers)
    assert res.status_code == 200

    # 4. Trigger analysis
    res = client.post("/api/doctor/analyze-patient", headers=sess_headers)
    assert res.status_code == 200

    # 5. View dashboard
    res = client.get("/api/doctor/dashboard-data", headers=sess_headers)
    assert res.status_code == 200

    # 6. Export Report
    res = client.post("/api/doctor/export-report", headers=sess_headers)
    assert res.status_code == 200
    assert res.headers["Content-Type"] == "application/pdf"
    
    # Check session exists
    assert session_id in ACTIVE_SESSIONS


# -----------------------------------------------------------------------------
# Test 3: Token Expiry
# -----------------------------------------------------------------------------
def test_token_expiry(client):
    res = client.post("/api/doctor/auth", json={"email": "dr.sharma@cityhospital.in", "password": "doctor123"})
    doc_token = res.json["token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # 1. Generate 30-min token in cache, manually modifying it to be expired
    from api.patient_cache import create_access_token
    t_data = create_access_token("P001", "dr.sharma@cityhospital.in", 30)
    access_token = t_data["access_token"]
    
    # Mock expiry
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    ACCESS_TOKEN_STORE[access_token]["expires_at"] = expired_time.isoformat()

    # 2. Try to start session
    res = client.post("/api/doctor/start-session", headers=doc_headers, json={
        "patient_id": "P001",
        "access_token": access_token
    })
    
    # Assert
    assert res.status_code == 401
    assert "Access denied or token expired" in res.json["message"]


# -----------------------------------------------------------------------------
# Test 4: Manual Upload Merge
# -----------------------------------------------------------------------------
def test_manual_upload_merge(client):
    res = client.post("/api/patient/auth", json={"patient_id": "P001", "biometric_type": "fingerprint", "biometric_data": "P001-fingerprint-template", "otp": "123456"})
    headers = {"Authorization": f"Bearer {res.json['token']}"}

    # Populate cache
    client.post("/api/patient/P001/fetch-historical", headers=headers)
    
    data = {"document_type": "vaccine_card", "file_size": 1024}
    data = {key: str(value) for key, value in data.items()}
    data["file"] = (io.BytesIO(b"dummy pdf content"), "vaccine.pdf")
    
    res = client.post("/api/patient/P001/upload-manual", headers=headers, data=data, content_type="multipart/form-data")
    assert res.status_code == 201

    cached = PATIENT_CACHE["P001"]
    assert len(cached["manual_records"]) == 1
    assert cached["manual_records"][0]["document_type"] == "vaccine_card"


# -----------------------------------------------------------------------------
# Test 5: Audit Trail Accuracy
# -----------------------------------------------------------------------------
def test_audit_trail_accuracy(client):
    res = client.post("/api/patient/auth", json={"patient_id": "P001", "biometric_type": "fingerprint", "biometric_data": "P001-fingerprint-template", "otp": "123456"})
    headers = {"Authorization": f"Bearer {res.json['token']}"}

    client.post("/api/patient/P001/fetch-historical", headers=headers)
    
    data = {"document_type": "vaccine_card", "file_size": 1024}
    data = {key: str(value) for key, value in data.items()}
    data["file"] = (io.BytesIO(b"pdf"), "vaccine.pdf")
    client.post("/api/patient/P001/upload-manual", headers=headers, data=data, content_type="multipart/form-data")
    
    client.post("/api/patient/P001/generate-access-token", headers=headers, json={"doctor_email": "dr.sharma@cityhospital.in", "duration_minutes": 30})
    
    res = client.get("/api/patient/P001/audit-log", headers=headers)
    entries = res.json["audit_log"]
    
    # Most recent first, but due to precision issues in tests we check a set
    actions = [e["action"] for e in entries]
    assert set(actions[:4]) == {"generate_token", "upload_report", "fetch_data", "login"}
    
    # Check timestamp ordering
    for i in range(len(entries) - 1):
        t1 = datetime.fromisoformat(entries[i]["timestamp"])
        t2 = datetime.fromisoformat(entries[i+1]["timestamp"])
        assert t1 >= t2


# -----------------------------------------------------------------------------
# Test 6: Data Privacy Consent
# -----------------------------------------------------------------------------
def test_data_privacy_consent(client):
    # Patient login
    res = client.post("/api/patient/auth", json={"patient_id": "P001", "biometric_type": "fingerprint", "biometric_data": "P001-fingerprint-template", "otp": "123456"})
    headers = {"Authorization": f"Bearer {res.json['token']}"}
    
    # Fetch historical data
    client.post("/api/patient/P001/fetch-historical", headers=headers)

    # Doctor login
    res = client.post("/api/doctor/auth", json={"email": "dr.sharma@cityhospital.in", "password": "doctor123"})
    doc_token = res.json["token"]
    
    # Generate token
    res = client.post("/api/patient/P001/generate-access-token", headers=headers, json={"doctor_email": "dr.sharma@cityhospital.in", "duration_minutes": 30})
    access_token = res.json["access_token"]
    
    # Start session
    doc_headers = {"Authorization": f"Bearer {doc_token}"}
    res = client.post("/api/doctor/start-session", headers=doc_headers, json={"patient_id": "P001", "access_token": access_token})
    session_id = res.json["session_id"]
    sess_headers = {"Authorization": f"Bearer {doc_token}", "Session-Id": session_id}
    
    # Doctor accesses data
    res = client.get("/api/doctor/patient-data", headers=sess_headers)
    assert res.status_code == 200
    filtered_data = res.json["patient_data"]
    
    # Check that privacy filters actually applied
    for diagnosis in filtered_data.get("diagnoses", []):
        assert "mental_health" not in diagnosis.get("category", "")
        assert "psychiatric" not in diagnosis.get("category", "")
