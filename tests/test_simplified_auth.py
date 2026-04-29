import os
import pytest
from flask import json
from api.app import create_app
from api.auth import generate_token

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    # Make sure we have a PATIENT_CACHE entry for P001 so it returns patient data
    with app.test_client() as client:
        # Pre-seed patient_cache to ensure Doctor access returns patient data
        from api.patient_cache import PATIENT_CACHE
        PATIENT_CACHE["P001"] = {"unified_data": {"name": "Test Patient"}}
        yield client

def get_patient_headers(patient_id):
    token = generate_token(
        payload={"sub": patient_id, "role": "patient"},
        expiry_seconds=3600
    )
    return {"Authorization": f"Bearer {token}"}

def test_simplified_auth_flow(client):
    patient_id = "P001"
    headers = get_patient_headers(patient_id)
    
    # 1. Patient generates token
    resp1 = client.post(
        f'/api/patient/{patient_id}/generate-access-token',
        headers=headers,
        json={"doctor_email": "dr.amit@hospital.com"}
    )
    assert resp1.status_code == 201
    data1 = json.loads(resp1.data)
    assert "access_token" in data1
    token = data1["access_token"]
    
    # 2. Token appears in active-tokens list
    resp2 = client.get(f'/api/patient/{patient_id}/active-tokens', headers=headers)
    assert resp2.status_code == 200
    data2 = json.loads(resp2.data)
    assert len(data2["active_tokens"]) == 1
    assert data2["active_tokens"][0]["doctor_email"] == "dr.amit@hospital.com"
    
    # 3. Doctor enters token -> access granted
    resp3 = client.post('/api/doctor/access-patient-data', json={"access_token": token})
    assert resp3.status_code == 200
    data3 = json.loads(resp3.data)
    assert data3["status"] == "success"
    assert data3["patient_id"] == "P001"
    assert data3["patient_data"]["name"] == "Test Patient"
    
    # 4. Patient revokes token
    resp4 = client.delete(f'/api/patient/{patient_id}/revoke-token/{token}', headers=headers)
    assert resp4.status_code == 200
    
    # 5. Token no longer active
    resp5 = client.get(f'/api/patient/{patient_id}/active-tokens', headers=headers)
    data5 = json.loads(resp5.data)
    assert len(data5["active_tokens"]) == 0
    
    # 6. Doctor access denied
    resp6 = client.post('/api/doctor/access-patient-data', json={"access_token": token})
    assert resp6.status_code == 401
    assert json.loads(resp6.data)["message"] == "Token has been revoked by patient"
    
    # 7. Check expiration mock
    from datetime import datetime, timezone, timedelta
    from api.app import AUTHORIZATION_TOKENS
    
    # Create an expired token
    expired_token = "expired_token_123"
    AUTHORIZATION_TOKENS[expired_token] = {
        "patient_id": patient_id,
        "doctor_email": "dr.test@hosp.com",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
        "status": "active"
    }
    
    resp7 = client.post('/api/doctor/access-patient-data', json={"access_token": expired_token})
    assert resp7.status_code == 401
    assert json.loads(resp7.data)["message"] == "Token has expired"
