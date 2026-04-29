import os
import pytest
import io
from flask import json
from api.app import create_app
from api.auth import generate_token

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def get_patient_headers(patient_id):
    token = generate_token(
        payload={"sub": patient_id, "role": "patient"},
        expiry_seconds=3600
    )
    return {"Authorization": f"Bearer {token}"}

def test_pdf_vaccine_upload(client):
    patient_id = "P001"
    headers = get_patient_headers(patient_id)
    
    # Create a dummy PDF file in memory
    from reportlab.pdfgen import canvas
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 100, "Vaccination Certificate: COVID-19, Polio")
    c.save()
    pdf_buffer.seek(0)
    
    data = {
        'file': (pdf_buffer, 'vaccine_cert.pdf', 'application/pdf')
    }
    
    response = client.post(
        f'/api/patient/{patient_id}/upload-manual',
        headers=headers,
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["status"] == "success"
    assert resp_data["file_type"] == "vaccine_card"
    assert "COVID-19" in resp_data["extracted_data"]["vaccines"]
    
def test_jpg_lab_upload(client):
    patient_id = "P001"
    headers = get_patient_headers(patient_id)
    
    # Create a dummy image
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (200, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Lab Report HbA1c: 7.2", fill=(0, 0, 0))
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG')
    img_buffer.seek(0)
    
    data = {
        'file': (img_buffer, 'lab_report.jpg', 'image/jpeg')
    }
    
    response = client.post(
        f'/api/patient/{patient_id}/upload-manual',
        headers=headers,
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    resp_data = json.loads(response.data)
    assert resp_data["status"] == "success"
    assert resp_data["file_type"] == "lab_report"
    assert resp_data["extracted_data"]["tests"][0]["name"] == "HbA1c"
