from flask import Blueprint, request, jsonify
from services.auth_service import authenticate_doctor, generate_jwt_token
from services.data_service import get_patient_records
from services.agent_service import analyze_patient
from services.export_service import generate_pdf_report
from utils.logger import log_info, log_error

bp = Blueprint('doctor', __name__)

@bp.route('/doctor/login', methods=['POST'])
def login():
    data = request.json
    doctor_id = authenticate_doctor(data.get('email'), data.get('password'))
    if not doctor_id:
        return {'status': 'error', 'message': 'Invalid credentials'}, 401
    token = generate_jwt_token(doctor_id, 'doctor', 1800)
    return {'status': 'success', 'doctor_id': doctor_id, 'token': token}

@bp.route('/doctor/verify-access-token', methods=['POST'])
def verify_access_token():
    return {'status': 'success'}

@bp.route('/doctor/patient-data', methods=['GET'])
def patient_data():
    patient_id = request.args.get('patient_id')
    return {'status': 'success', 'data': get_patient_records(patient_id)}

@bp.route('/doctor/analyze-patient', methods=['POST'])
def analyze_patient_route():
    data = request.json
    result = analyze_patient(data.get('patient_id'), data.get('chief_complaint'))
    return {'status': 'success', 'analysis': result}

@bp.route('/doctor/dashboard-data', methods=['GET'])
def dashboard_data():
    return {'status': 'success', 'data': {}}

@bp.route('/doctor/export-report-pdf', methods=['POST'])
def export_report_pdf():
    data = request.json
    pdf_url = generate_pdf_report(data.get('patient_id'), {}, data.get('export_type', 'full'))
    return {'status': 'success', 'pdf_url': pdf_url}

@bp.route('/doctor/audit-log', methods=['GET'])
def audit_log():
    return {'status': 'success', 'log': []}

@bp.route('/doctor/session-status', methods=['POST'])
def session_status():
    return {'status': 'success', 'time_remaining': 1800}
