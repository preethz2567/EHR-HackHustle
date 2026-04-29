import pytest
from flask import json
from api.app import create_app
from api.auth import generate_token
import os

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    
    # Pre-seed patient_cache and analysis_cache
    from api.patient_cache import PATIENT_CACHE
    from api.app import ANALYSIS_CACHE
    PATIENT_CACHE["P001"] = {
        "unified_data": {
            "name": "Test Patient",
            "diagnoses": [{"name": "Diabetes", "code": "E11", "date_of_diagnosis": "2023-01-01"}],
            "medications": [{"name": "Metformin", "dosage": "500mg", "status": "active"}],
            "labs": [{"test_name": "HbA1c", "value": 7.0, "unit": "%", "date": "2024-01-01", "reference_range": "<5.7"}]
        }
    }
    ANALYSIS_CACHE["P001"] = {
        "agent_outputs": {
            "risk": {
                "high_risk_conditions": [{"condition": "Diabetes", "level": "High"}],
                "moderate_risk_conditions": []
            },
            "medications": {
                "interactions_found": []
            }
        },
        "orchestrator_synthesis": {
            "clinical_summary": "Patient is diabetic.",
            "immediate_priorities": ["Monitor HbA1c"],
            "recommended_actions": ["Continue Metformin"],
            "key_risk_signals": {"HbA1c": "Elevated at 7.0%"}
        },
        "analysis_timestamp": "2024-04-29T10:00:00"
    }
    
    with app.test_client() as client:
        yield client

def get_patient_headers(patient_id):
    token = generate_token(
        payload={"sub": patient_id, "role": "patient"},
        expiry_seconds=3600
    )
    return {"Authorization": f"Bearer {token}"}

def test_patient_medical_records_export(client):
    headers = get_patient_headers("P001")
    resp = client.post('/api/patient/P001/export-medical-records-pdf', headers=headers)
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert "download_url" in data
    assert "status" in data and data["status"] == "success"
    
    filename = data["filename"]
    assert os.path.exists(f"./exports/{filename}")
    
    # Test download endpoint
    dl_resp = client.get(data["download_url"])
    assert dl_resp.status_code == 200
    assert dl_resp.headers["Content-Disposition"].startswith("attachment")
    assert dl_resp.mimetype == "application/pdf"

def test_doctor_export(client):
    # 1. Create a token
    headers = get_patient_headers("P001")
    resp1 = client.post('/api/patient/P001/generate-access-token', headers=headers, json={"doctor_email": "dr.amit@hospital.com"})
    token = json.loads(resp1.data)["access_token"]
    
    # 2. Doctor exports "summary"
    resp2 = client.post('/api/doctor/export-report-pdf', json={"access_token": token, "export_type": "summary"})
    assert resp2.status_code == 201
    data2 = json.loads(resp2.data)
    assert data2["status"] == "success"
    
    filename = data2["filename"]
    assert "summary" in filename
    assert os.path.exists(f"./exports/{filename}")
