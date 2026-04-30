import pytest
import os
import sys

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_patient_p001_fetch(client):
    # P001 login
    response = client.post('/api/patient/login', json={
        'email': 'rajesh@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert response.json['patient_id'] == 'P001'
    token_p001 = response.json['token']
    
    # P001 fetch
    response = client.post('/api/patient/P001/fetch-historical', 
        headers={'Authorization': f'Bearer {token_p001}'})
    assert response.status_code == 200
    assert response.json['patient_id'] == 'P001'
    assert 'data_summary' in response.json
    p001_diagnoses = response.json['data_summary']['diagnoses_count']
    
    assert p001_diagnoses > 0

def test_patient_p002_fetch(client):
    # P002 login
    response = client.post('/api/patient/login', json={
        'email': 'priya@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert response.json['patient_id'] == 'P002'
    token_p002 = response.json['token']
    
    # P002 fetch
    response = client.post('/api/patient/P002/fetch-historical', 
        headers={'Authorization': f'Bearer {token_p002}'})
    assert response.status_code == 200
    assert response.json['patient_id'] == 'P002'
    assert 'data_summary' in response.json
    p002_diagnoses = response.json['data_summary']['diagnoses_count']
    
    assert p002_diagnoses > 0

def test_doctor_access_p001(client):
    # Fetch P001 first to populate cache
    p001_login = client.post('/api/patient/login', json={'email': 'rajesh@example.com', 'password': 'password123'})
    client.post('/api/patient/P001/fetch-historical', headers={'Authorization': f"Bearer {p001_login.json['token']}"})

    # Generate P001 token
    p001_response = client.post('/api/patient/P001/generate-access-token', 
        json={'doctor_email': 'dr.sharma@cityhospital.in'},
        headers={'Authorization': f"Bearer {p001_login.json['token']}"})
    assert p001_response.status_code in [200, 201]
    access_token = p001_response.json['access_token']
    
    # Doctor logs in
    doctor_response = client.post('/api/doctor/login', json={
        'email': 'dr.sharma@cityhospital.in',
        'password': 'doctor123'
    })
    assert doctor_response.status_code == 200
    doctor_token = doctor_response.json['token']
    
    # Doctor verifies token
    verify_response = client.post('/api/doctor/verify-access-token', 
        json={'access_token': access_token},
        headers={'Authorization': f'Bearer {doctor_token}'})
    assert verify_response.status_code == 200
    assert verify_response.json['patient_id'] == 'P001'
    
    # Doctor accesses P001 data
    data_response = client.get(f'/api/doctor/patient-data/P001?access_token={access_token}',
        headers={
            'Authorization': f'Bearer {doctor_token}'
        })
    assert data_response.status_code == 200
    assert data_response.json['patient_id'] == 'P001'
    assert len(data_response.json['patient_data']['diagnoses']) > 0

def test_cross_patient_access_denied(client):
    # Populate P001 cache & generate token
    p001_login = client.post('/api/patient/login', json={'email': 'rajesh@example.com', 'password': 'password123'})
    client.post('/api/patient/P001/fetch-historical', headers={'Authorization': f"Bearer {p001_login.json['token']}"})
    
    p001_response = client.post('/api/patient/P001/generate-access-token', 
        json={'doctor_email': 'dr.sharma@cityhospital.in'},
        headers={'Authorization': f"Bearer {p001_login.json['token']}"})
    p001_access_token = p001_response.json['access_token']
    
    # Doctor logs in
    doc_login = client.post('/api/doctor/login', json={'email': 'dr.sharma@cityhospital.in', 'password': 'doctor123'})
    doc_token = doc_login.json['token']
    
    # Doctor tries to access P002 with P001's token
    response = client.get(f'/api/doctor/patient-data/P002?access_token={p001_access_token}',
        headers={'Authorization': f'Bearer {doc_token}'})
    # Should be 401 or 403 due to token patient_id mismatch
    assert response.status_code in [401, 403]

def test_disease_timeline_unique(client):
    # Populate caches and run analysis for both P001 and P002
    
    # P001
    p1 = client.post('/api/patient/login', json={'email': 'rajesh@example.com', 'password': 'password123'})
    client.post('/api/patient/P001/fetch-historical', headers={'Authorization': f"Bearer {p1.json['token']}"})
    a1 = client.post('/api/patient/P001/generate-access-token', json={'doctor_email': 'dr.sharma@cityhospital.in'}, headers={'Authorization': f"Bearer {p1.json['token']}"})
    
    # P002
    p2 = client.post('/api/patient/login', json={'email': 'priya@example.com', 'password': 'password123'})
    client.post('/api/patient/P002/fetch-historical', headers={'Authorization': f"Bearer {p2.json['token']}"})
    a2 = client.post('/api/patient/P002/generate-access-token', json={'doctor_email': 'dr.sharma@cityhospital.in'}, headers={'Authorization': f"Bearer {p2.json['token']}"})
    
    doc = client.post('/api/doctor/login', json={'email': 'dr.sharma@cityhospital.in', 'password': 'doctor123'})
    dtok = doc.json['token']
    
    # Run analysis for P001
    client.post(f"/api/doctor/analyze-patient/P001?access_token={a1.json['access_token']}", 
                headers={'Authorization': f"Bearer {dtok}"},
                json={"chief_complaint": "Test", "context": "Test"})
                
    # Run analysis for P002
    client.post(f"/api/doctor/analyze-patient/P002?access_token={a2.json['access_token']}", 
                headers={'Authorization': f"Bearer {dtok}"},
                json={"chief_complaint": "Test", "context": "Test"})
                
    # Get P001 dashboard
    resp1 = client.get(f"/api/doctor/dashboard-data/P001?access_token={a1.json['access_token']}", headers={'Authorization': f"Bearer {dtok}"})
    timeline_p001 = resp1.json['disease_timeline']
    
    # Get P002 dashboard
    resp2 = client.get(f"/api/doctor/dashboard-data/P002?access_token={a2.json['access_token']}", headers={'Authorization': f"Bearer {dtok}"})
    timeline_p002 = resp2.json['disease_timeline']
    
    # Ensure they are different
    assert timeline_p001 != timeline_p002
