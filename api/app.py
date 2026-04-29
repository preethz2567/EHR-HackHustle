"""
app.py — Flask REST API
========================
PS-1: Privacy-Preserving Patient Memory Layer

Auth Endpoints:
  POST /api/patient/auth              — Patient biometric + OTP authentication
  POST /api/doctor/auth               — Doctor email + password authentication
  POST /api/doctor/session            — Generate 30-min session token

Patient Portal Endpoints:
  POST /api/patient/<id>/fetch-historical  — Fetch & cache from providers A,B,C
  GET  /api/patient/<id>/data              — Get cached unified EHR
  POST /api/patient/<id>/upload-manual     — Upload manual records
  POST /api/patient/<id>/generate-access-token — Share access with doctor
  GET  /api/patient/<id>/audit-log         — Patient-specific audit trail

Doctor Endpoints:
  GET  /api/doctor/patient/<id>       — Doctor views patient (session-gated)

System Endpoints:
  GET  /api/patient/data              — Legacy: patient self-access
  GET  /api/audit/log                 — Global audit trail
  GET  /api/health                    — Health check

Run:  python api/app.py
"""

import os
import sys

# Ensure project root is on path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, request, jsonify, g
from flask_cors import CORS

from api.config import Config
from api.auth import (
    authenticate_patient,
    authenticate_doctor,
    generate_session_token,
    decode_token,
    token_required,
    AUDIT_LOG,
    PATIENT_BIOMETRIC_STORE,
    _log_audit,
)
from api.patient_cache import (
    cache_patient_data,
    get_cached_data,
    is_cached,
    add_manual_record,
    create_access_token,
    validate_access_token,
    get_patient_audit_log,
    _log_patient_audit,
    PATIENT_CACHE,
)
from concurrent.futures import ThreadPoolExecutor

# In-memory cache for analysis results to avoid re-triggering on refresh
ANALYSIS_CACHE: dict = {}

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # -------------------------------------------------------------------
    # HEALTH CHECK
    # -------------------------------------------------------------------

    @app.route("/api/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "PS-1 EHR Privacy Layer",
            "version": "1.0.0",
        }), 200

    # -------------------------------------------------------------------
    # PATIENT AUTHENTICATION
    # -------------------------------------------------------------------

    @app.route("/api/patient/auth", methods=["POST"])
    def patient_auth():
        """
        Authenticate a patient via biometric + OTP.

        Request JSON:
            {
                "patient_id": "P001",
                "biometric_type": "fingerprint",  // or "iris"
                "biometric_data": "<raw-biometric-string>",
                "otp": "123456"
            }

        Response:
            {
                "success": true,
                "token": "<jwt>",
                "patient_id": "P001",
                "message": "Authentication successful"
            }
        """
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body must be JSON",
            }), 400

        # Required fields
        required = ["patient_id", "biometric_type", "biometric_data", "otp"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing)}",
            }), 400

        result = authenticate_patient(
            patient_id=data["patient_id"],
            biometric_type=data["biometric_type"],
            biometric_data=data["biometric_data"],
            otp=data["otp"],
        )

        status_code = 200 if result["success"] else 401
        return jsonify(result), status_code

    # -------------------------------------------------------------------
    # DOCTOR AUTHENTICATION
    # -------------------------------------------------------------------

    @app.route("/api/doctor/auth", methods=["POST"])
    def doctor_auth():
        """
        Authenticate a doctor via email + password.

        Request JSON:
            {
                "email": "dr.sharma@cityhospital.in",
                "password": "doctor123"
            }

        Response:
            {
                "success": true,
                "token": "<jwt>",
                "doctor_id": "DR-SHARMA",
                "message": "Authentication successful"
            }
        """
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body must be JSON",
            }), 400

        required = ["email", "password"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                "success": False,
                "message": f"Missing required fields: {', '.join(missing)}",
            }), 400

        result = authenticate_doctor(
            email=data["email"],
            password=data["password"],
        )

        status_code = 200 if result["success"] else 401
        return jsonify(result), status_code

    # -------------------------------------------------------------------
    # DOCTOR SESSION TOKEN (30-min patient data access)
    # -------------------------------------------------------------------

    @app.route("/api/doctor/session", methods=["POST"])
    @token_required(allowed_roles=["doctor"])
    def doctor_session():
        """
        Generate a 30-minute session token for doctor to access patient data.

        Requires: Doctor JWT in Authorization header.

        Request JSON:
            {
                "patient_id": "P001"
            }

        Response:
            {
                "success": true,
                "session_token": "<jwt>",
                "patient_id": "P001",
                "expires_in": 1800,
                "message": "Session granted for 30 minutes"
            }
        """
        data = request.get_json(silent=True)
        if not data or "patient_id" not in data:
            return jsonify({
                "success": False,
                "message": "Missing required field: patient_id",
            }), 400

        doctor_id = g.current_user["sub"]
        result = generate_session_token(doctor_id, data["patient_id"])

        status_code = 200 if result["success"] else 404
        return jsonify(result), status_code

    # -------------------------------------------------------------------
    # PATIENT DATA — legacy self-access (kept for backward compat)
    # -------------------------------------------------------------------

    @app.route("/api/patient/data", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def patient_data():
        """
        Fetch the authenticated patient's own EHR data.

        Requires: Patient JWT in Authorization header.

        Response:
            Full patient data object from the federated sources.
        """
        patient_id = g.current_user["sub"]

        try:
            from data.synthetic_ehr_generator import generate_patient
            patient = generate_patient(patient_id)
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to fetch patient data: {str(e)}",
            }), 500

        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "data": patient,
        }), 200

    # ===================================================================
    # PATIENT PORTAL ENDPOINTS
    # ===================================================================

    # -------------------------------------------------------------------
    # 1. FETCH HISTORICAL DATA (federated query → cache)
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/fetch-historical", methods=["POST"])
    @token_required(allowed_roles=["patient"])
    def fetch_historical(patient_id):
        """
        Fetch patient data from all 3 federated providers and cache it.

        Requires: Patient JWT. Patient can only fetch their own data.

        Request JSON (optional):
            {
                "biometric_type": "fingerprint"   // re-verification step
            }

        Response:
            {
                "success": true,
                "data_cached": true,
                "records_count": 12,
                "breakdown": {"diagnoses": 3, "medications": 4, ...},
                "cached_at": "2026-04-29T13:30:00+00:00"
            }
        """
        # Verify patient is accessing their own data
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "success": False,
                "message": f"Access denied. You can only fetch your own data.",
            }), 403

        try:
            from data.federated_sources import federated_query
            unified_data = federated_query(patient_id)
        except ValueError as e:
            return jsonify({
                "success": False,
                "message": f"Federated query failed: {str(e)}",
            }), 404
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Failed to fetch data from providers: {str(e)}",
            }), 500

        # Cache the unified data
        cache_info = cache_patient_data(patient_id, unified_data)

        # Audit
        _log_patient_audit(
            patient_id, "FETCH_HISTORICAL", patient_id, "patient",
            f"Fetched from providers A,B,C. {cache_info['records_count']} records cached."
        )
        _log_audit(
            "FETCH_HISTORICAL", patient_id,
            f"Patient fetched historical data. {cache_info['records_count']} records.", True
        )

        return jsonify({
            "success": True,
            "data_cached": True,
            "records_count": cache_info["records_count"],
            "breakdown": cache_info["breakdown"],
            "cached_at": cache_info["cached_at"],
        }), 200

    # -------------------------------------------------------------------
    # 2. GET CACHED PATIENT DATA
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/data", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def get_patient_cached_data(patient_id):
        """
        Retrieve cached unified EHR data for a patient.

        Requires: Patient JWT. Must fetch-historical first.

        Response (cached):
            {
                "success": true,
                "patient_id": "P001",
                "cached_at": "...",
                "data": {diagnoses, medications, labs, episodes, ...},
                "manual_uploads": [...]
            }
        """
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "success": False,
                "message": "Access denied. You can only view your own data.",
            }), 403

        cached = get_cached_data(patient_id)

        if cached is None or cached.get("cached_at") is None:
            return jsonify({
                "success": False,
                "message": "No cached data found. Please call POST /api/patient/<id>/fetch-historical first.",
                "data_cached": False,
            }), 404

        _log_patient_audit(
            patient_id, "DATA_ACCESS", patient_id, "patient",
            "Patient viewed their cached EHR data."
        )

        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "cached_at": cached["cached_at"],
            "last_refreshed": cached["last_refreshed"],
            "data": cached["unified_data"],
            "manual_uploads": cached.get("manual_records", []),
        }), 200

    # -------------------------------------------------------------------
    # 3. UPLOAD MANUAL RECORDS
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/upload-manual", methods=["POST"])
    @token_required(allowed_roles=["patient"])
    def upload_manual(patient_id):
        """
        Upload a manual health record (vaccine card, lab report, prescription).

        Requires: Patient JWT.

        Accepts multipart/form-data with:
            - file: the document (pdf/image)
            - document_type: "vaccine_card" | "lab_report" | "prescription"

        OR JSON body (for demo/testing without actual file upload):
            {
                "document_type": "vaccine_card",
                "filename": "covid_vaccine_certificate.pdf",
                "file_size": 204800
            }

        Response:
            {
                "success": true,
                "status": "uploaded",
                "record": {record_id, document_type, filename, uploaded_at}
            }
        """
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "success": False,
                "message": "Access denied. You can only upload to your own records.",
            }), 403

        VALID_DOCUMENT_TYPES = ["vaccine_card", "lab_report", "prescription", "discharge_summary", "other"]

        # Check for multipart file upload
        if request.content_type and "multipart/form-data" in request.content_type:
            file = request.files.get("file")
            document_type = request.form.get("document_type", "")

            if not file:
                return jsonify({
                    "success": False,
                    "message": "No file provided.",
                }), 400

            if document_type not in VALID_DOCUMENT_TYPES:
                return jsonify({
                    "success": False,
                    "message": f"Invalid document_type. Must be one of: {', '.join(VALID_DOCUMENT_TYPES)}",
                }), 400

            # Read file info (don't actually save in demo)
            file_content = file.read()
            file_size = len(file_content)
            
            # 10MB size limit check
            if file_size > 10 * 1024 * 1024:
                return jsonify({
                    "success": False,
                    "message": "File size exceeds 10MB limit.",
                }), 400

            # Mock Extraction and Parsing
            from datetime import datetime, timezone
            now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            parsed_data = {}
            if document_type == "vaccine_card":
                parsed_data = {
                    "date": now_date,
                    "type": "vaccine_card",
                    "vaccines": ["COVID-19", "Flu"],
                    "summary": "Routine vaccinations administered."
                }
            elif document_type == "lab_report":
                parsed_data = {
                    "date": now_date,
                    "type": "lab_report",
                    "labs": [
                        {"test_name": "Extracted Glucose", "value": "95 mg/dL", "reference_range": "70-100 mg/dL"},
                        {"test_name": "Extracted eGFR", "value": "62 mL/min", "reference_range": "> 60 mL/min"}
                    ],
                    "summary": "Routine lab panel results extracted."
                }
            else:
                parsed_data = {
                    "date": now_date,
                    "type": document_type,
                    "summary": "Document successfully parsed and indexed."
                }

            record = add_manual_record(
                patient_id=patient_id,
                document_type=document_type,
                filename=file.filename or "unknown",
                file_size=file_size,
                content_type=file.content_type or "application/octet-stream",
                parsed_data=parsed_data
            )
        else:
            # JSON body (for testing)
            data = request.get_json(silent=True)
            if not data:
                return jsonify({
                    "success": False,
                    "message": "Request must be multipart/form-data with a file, or JSON body for testing.",
                }), 400

            document_type = data.get("document_type", "")
            if document_type not in VALID_DOCUMENT_TYPES:
                return jsonify({
                    "success": False,
                    "message": f"Invalid document_type. Must be one of: {', '.join(VALID_DOCUMENT_TYPES)}",
                }), 400

            file_size = data.get("file_size", 0)
            if file_size > 10 * 1024 * 1024:
                return jsonify({
                    "success": False,
                    "message": "File size exceeds 10MB limit.",
                }), 400

            # Mock Parsing for JSON fallback
            from datetime import datetime, timezone
            parsed_data = {
                "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "type": document_type,
                "summary": "Document JSON metadata uploaded and parsed."
            }

            record = add_manual_record(
                patient_id=patient_id,
                document_type=document_type,
                filename=data.get("filename", "manual_upload.pdf"),
                file_size=file_size,
                content_type=data.get("content_type", "application/pdf"),
                parsed_data=parsed_data
            )

        _log_patient_audit(
            patient_id, "MANUAL_UPLOAD", patient_id, "patient",
            f"Uploaded {document_type}: {record['filename']}"
        )

        return jsonify({
            "success": True,
            "status": "success",
            "document_type": document_type,
            "message": "Report merged into your records",
            "timestamp": record["uploaded_at"],
            "record": record,
        }), 201

    # -------------------------------------------------------------------
    # 4. GENERATE ACCESS TOKEN (patient shares with doctor)
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/generate-access-token", methods=["POST"])
    @token_required(allowed_roles=["patient"])
    def generate_access_token_endpoint(patient_id):
        """
        Patient generates a short-lived access token for a specific doctor.

        Requires: Patient JWT.

        Request JSON:
            {
                "doctor_email": "dr.sharma@cityhospital.in",
                "duration_minutes": 30
            }

        Response:
            {
                "status": "success",
                "access_token": "<token>",
                "expires_in_minutes": 30,
                "message": "Share this token with doctor"
            }
        """
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "success": False,
                "message": "Access denied. You can only generate tokens for your own data.",
            }), 403

        data = request.get_json(silent=True)
        if not data or "doctor_email" not in data:
            return jsonify({
                "success": False,
                "message": "Missing required field: doctor_email",
            }), 400

        doctor_email = data["doctor_email"]
        duration = data.get("duration_minutes", 30)

        if duration not in [15, 30, 60]:
            duration = 30 # fallback to default if invalid

        result = create_access_token(patient_id, doctor_email, duration)

        return jsonify({
            "status": "success",
            "access_token": result["access_token"],
            "expires_in_minutes": result["expires_in_minutes"],
            "message": "Share this token with doctor"
        }), 201

    @app.route("/api/patient/<patient_id>/active-authorizations", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def get_patient_active_authorizations(patient_id):
        """Return all active tokens for this patient."""
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({"success": False, "message": "Access denied"}), 403
            
        from api.patient_cache import get_active_authorizations
        active = get_active_authorizations(patient_id)
        
        return jsonify({
            "status": "success",
            "authorizations": active
        }), 200

    @app.route("/api/patient/<patient_id>/revoke-token/<access_token>", methods=["DELETE"])
    @token_required(allowed_roles=["patient"])
    def revoke_patient_token(patient_id, access_token):
        """Revoke a specific token."""
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({"success": False, "message": "Access denied"}), 403
            
        from api.patient_cache import revoke_token
        success = revoke_token(patient_id, access_token)
        
        if success:
            return jsonify({"status": "success", "message": "Access revoked"}), 200
        else:
            return jsonify({"status": "error", "message": "Token not found or unauthorized"}), 404

    # -------------------------------------------------------------------
    # 5. PATIENT-SPECIFIC AUDIT LOG
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/audit-log", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def patient_audit_log(patient_id):
        """
        View all access events for a specific patient.

        Requires: Patient JWT. Patients can only view their own audit log.

        Query params:
            ?limit=50  (default 50)

        Response:
            {
                "success": true,
                "patient_id": "P001",
                "count": 5,
                "entries": [
                    {"event_type": "ACCESS_TOKEN_GRANTED", "actor_id": "P001", ...},
                    ...
                ]
            }
        """
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "success": False,
                "message": "Access denied. You can only view your own audit log.",
            }), 403

        limit = request.args.get("limit", 50, type=int)
        entries = get_patient_audit_log(patient_id)

        return jsonify({
            "success": True,
            "patient_id": patient_id,
            "count": len(entries[:limit]),
            "entries": entries[:limit],
        }), 200

    # -------------------------------------------------------------------
    # DOCTOR VIEW PATIENT DATA
    # -------------------------------------------------------------------

    def apply_consent(patient_data: dict) -> dict:
        """Person D's apply_consent function."""
        # Mock consent filtering based on patient's preferences
        consent = patient_data.get("consent_preferences", {})
        if not consent.get("share_mental_health", True):
            patient_data["diagnoses"] = [
                d for d in patient_data.get("diagnoses", [])
                if "mental" not in str(d.get("name", "")).lower()
            ]
        return patient_data

    @app.route("/api/doctor/patient-data", methods=["GET"])
    @token_required(allowed_roles=["doctor"])
    def doctor_patient_data():
        """
        Doctor retrieves patient data.

        Requires: Doctor JWT in Authorization header.
        Headers:
            patient_id: "P001"
            access_token: "<share_token>"
        """
        doctor_id = g.current_user["sub"]
        patient_id = request.headers.get("Patient-Id")
        access_token = request.headers.get("Access-Token")

        if not patient_id or not access_token:
            return jsonify({
                "status": "error",
                "message": "Missing Patient-Id or Access-Token in headers."
            }), 400

        # Validate access token
        token_data = validate_access_token(access_token)
        if not token_data or token_data.get("doctor_id") != doctor_id or token_data.get("patient_id") != patient_id:
            return jsonify({
                "status": "error",
                "message": "Access denied or token expired"
            }), 401

        # Retrieve patient_cache
        cached = get_cached_data(patient_id)
        if not cached:
            return jsonify({
                "status": "error",
                "message": "Patient data not found in cache."
            }), 404

        patient_data = cached["unified_data"]
        
        # Apply consent filtering
        filtered_data = apply_consent(patient_data)

        # Audit Log
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        log_msg = f"Doctor {doctor_id} accessed patient {patient_id} data at {now}, token: {access_token}"
        _log_audit("DOCTOR_ACCESS", doctor_id, log_msg, True)
        _log_patient_audit(patient_id, "DOCTOR_ACCESS", doctor_id, "doctor", log_msg)

        return jsonify({
            "status": "success",
            "patient_data": filtered_data
        }), 200

    # -------------------------------------------------------------------
    # DOCTOR ANALYZE PATIENT DATA (AI AGENTS)
    # -------------------------------------------------------------------

    @app.route("/api/doctor/analyze-patient", methods=["POST"])
    @token_required(allowed_roles=["doctor"])
    def analyze_patient():
        """
        Run 4 AI agents in parallel and synthesize with orchestrator.
        """
        doctor_id = g.current_user["sub"]
        patient_id = request.headers.get("Patient-Id")
        access_token = request.headers.get("Access-Token")

        if not patient_id or not access_token:
            return jsonify({
                "status": "error",
                "message": "Missing Patient-Id or Access-Token in headers."
            }), 400

        token_data = validate_access_token(access_token)
        if not token_data or token_data.get("doctor_id") != doctor_id or token_data.get("patient_id") != patient_id:
            return jsonify({
                "status": "error",
                "message": "Access denied or token expired"
            }), 401

        # Check if already analyzed to save time
        if patient_id in ANALYSIS_CACHE:
            return jsonify(ANALYSIS_CACHE[patient_id]), 200

        cached = get_cached_data(patient_id)
        if not cached:
            return jsonify({
                "status": "error",
                "message": "Patient data not found in cache."
            }), 404

        patient_data = apply_consent(cached["unified_data"])

        try:
            from api.agents import agent_risk, agent_meds, agent_episodes, agent_labs, orchestrator
            
            # Run 4 Agents in parallel
            with ThreadPoolExecutor(max_workers=4) as executor:
                f_risk = executor.submit(agent_risk, patient_data)
                f_meds = executor.submit(agent_meds, patient_data)
                f_episodes = executor.submit(agent_episodes, patient_data)
                f_labs = executor.submit(agent_labs, patient_data)

                risk_output = f_risk.result()
                meds_output = f_meds.result()
                episodes_output = f_episodes.result()
                labs_output = f_labs.result()

            # Run Orchestrator
            orchestrator_output = orchestrator(risk_output, meds_output, episodes_output, labs_output)

            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat()
            
            combined_response = {
                "agent_outputs": {
                    "risk": risk_output,
                    "medications": meds_output,
                    "episodes": episodes_output,
                    "labs": labs_output
                },
                "orchestrator_synthesis": orchestrator_output,
                "analysis_timestamp": now,
                "status": "success"
            }

            # Cache the result
            ANALYSIS_CACHE[patient_id] = combined_response

            # Log
            log_msg = f"Doctor {doctor_id} triggered analysis for patient {patient_id} at {now}"
            _log_audit("DOCTOR_ANALYSIS", doctor_id, log_msg, True)
            _log_patient_audit(patient_id, "DOCTOR_ANALYSIS", doctor_id, "doctor", log_msg)

            return jsonify(combined_response), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }), 500

    # -------------------------------------------------------------------
    # AUDIT LOG
    # -------------------------------------------------------------------

    @app.route("/api/audit/log", methods=["GET"])
    @token_required(allowed_roles=["doctor", "patient"])
    def audit_log():
        """
        View audit trail. Patients see only their own events.
        Doctors see all events.

        Query params:
            ?limit=20  (default 50)
        """
        limit = request.args.get("limit", 50, type=int)
        user = g.current_user
        role = user.get("role")

        if role == "patient":
            # Filter to only this patient's events
            patient_id = user["sub"]
            entries = [e for e in AUDIT_LOG if e.get("actor_id") == patient_id]
        else:
            entries = AUDIT_LOG

        # Return most recent first
        return jsonify({
            "success": True,
            "count": len(entries[-limit:]),
            "entries": list(reversed(entries[-limit:])),
        }), 200

    # -------------------------------------------------------------------
    # ERROR HANDLERS
    # -------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "message": "Endpoint not found",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success": False,
            "message": "Method not allowed",
        }), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({
            "success": False,
            "message": "Internal server error",
        }), 500

    return app


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = create_app()
    print("=" * 65)
    print("  PS-1: Privacy-Preserving Patient Memory Layer API")
    print("=" * 65)
    print()
    print("  Auth:")
    print("    POST /api/patient/auth                     Biometric + OTP")
    print("    POST /api/doctor/auth                      Email + password")
    print("    POST /api/doctor/session                   30-min session")
    print()
    print("  Patient Portal:")
    print("    POST /api/patient/<id>/fetch-historical    Fetch & cache EHR")
    print("    GET  /api/patient/<id>/data                Get cached data")
    print("    POST /api/patient/<id>/upload-manual       Upload records")
    print("    POST /api/patient/<id>/generate-access-token  Share access")
    print("    GET  /api/patient/<id>/audit-log           Audit trail")
    print()
    print("  Doctor:")
    print("    GET  /api/doctor/patient/<id>              View patient (session)")
    print()
    print("  System:")
    print("    GET  /api/patient/data                     Legacy self-access")
    print("    GET  /api/audit/log                        Global audit")
    print("    GET  /api/health                           Health check")
    print()
    print("  Demo Credentials:")
    print("    Patient: P001, fingerprint: P001-fingerprint-template, OTP: 123456")
    print("    Doctor:  dr.sharma@cityhospital.in / doctor123")
    print("=" * 65)
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
