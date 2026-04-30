from flask import Blueprint, request, jsonify
from services.auth_service import authenticate_patient, verify_otp, verify_biometric, generate_jwt_token
from services.data_service import fetch_patient_data, get_patient_records, upload_manual_report
from utils.logger import log_info, log_error

bp = Blueprint('patient', __name__)

@bp.route('/patient/login', methods=['POST'])
def login():
    data = request.json
    patient_id = authenticate_patient(data.get('email'), data.get('password'))
    if not patient_id:
        return {'status': 'error', 'message': 'Invalid credentials'}, 401
    
    token = generate_jwt_token(patient_id, 'patient', duration=86400)
    log_info(f"Patient {patient_id} logged in")
    return {'status': 'success', 'patient_id': patient_id, 'token': token}

@bp.route('/patient/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.json
    if verify_otp(data.get('patient_id'), data.get('otp')):
        return {'status': 'success'}
    return {'status': 'error', 'message': 'Invalid OTP'}, 401

@bp.route('/patient/verify-biometric', methods=['POST'])
def verify_biometric_route():
    data = request.json
    if verify_biometric(data.get('patient_id'), data.get('biometric_type')):
        return {'status': 'success'}
    return {'status': 'error', 'message': 'Biometric verification failed'}, 401

@bp.route('/patient/<patient_id>/fetch-historical', methods=['POST'])
def fetch_historical(patient_id):
    try:
        data = fetch_patient_data(patient_id)
        log_info(f"Fetched historical data for {patient_id}")
        return {'status': 'success', 'data': data}
    except Exception as e:
        log_error(f"Error fetching historical data: {str(e)}")
        return {'status': 'error', 'message': str(e)}, 500

@bp.route('/patient/<patient_id>/my-records', methods=['GET'])
def my_records(patient_id):
    data = get_patient_records(patient_id)
    return {'status': 'success', 'data': data}

@bp.route('/patient/<patient_id>/upload-manual', methods=['POST'])
def upload_manual(patient_id):
    if 'file' not in request.files:
        return {'status': 'error', 'message': 'No file provided'}, 400
    upload_manual_report(patient_id, request.files['file'])
    return {'status': 'success'}

@bp.route('/patient/<patient_id>/generate-access-token', methods=['POST'])
def generate_access_token(patient_id):
    # Stub for generating token
    return {'status': 'success', 'access_token': 'test-token-123'}

@bp.route('/patient/<patient_id>/active-tokens', methods=['GET'])
def active_tokens(patient_id):
    return {'status': 'success', 'tokens': []}

@bp.route('/patient/<patient_id>/revoke-token/<token>', methods=['DELETE'])
def revoke_token(patient_id, token):
    return {'status': 'success'}
