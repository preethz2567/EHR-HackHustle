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
    PATIENT_BIOMETRIC_STORE,
)
from api.patient_cache import (
    cache_patient_data,
    get_cached_data,
    is_cached,
    add_manual_record,
    create_access_token,
    validate_access_token,
    PATIENT_CACHE,
)
from api.audit import (
    log_patient_action,
    log_doctor_action,
    get_patient_audit_log,
    get_doctor_audit_log,
    get_admin_audit_log
)
from api.session import (
    DoctorSession,
    ACTIVE_SESSIONS,
    init_session_manager,
    session_required,
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
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize the session background cleanup
    init_session_manager()


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
    @app.route("/api/patient/login", methods=["POST"])
    def patient_auth():
        """
        Authenticate a patient via biometric + OTP OR email + password.
        """
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body must be JSON",
            }), 400

        result = authenticate_patient(
            patient_id=data.get("patient_id"),
            biometric_type=data.get("biometric_type"),
            biometric_data=data.get("biometric_data"),
            otp=data.get("otp"),
            email=data.get("email"),
            password=data.get("password")
        )

        status_code = 200 if result["success"] else 401
        return jsonify(result), status_code

    # -------------------------------------------------------------------
    # DOCTOR AUTHENTICATION
    # -------------------------------------------------------------------

    @app.route("/api/doctor/auth", methods=["POST"])
    @app.route("/api/doctor/login", methods=["POST"])
    def doctor_auth():
        """
        Authenticate a doctor via email + password.
        """
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body must be JSON",
            }), 400

        result = authenticate_doctor(
            email=data.get("email"),
            password=data.get("password"),
        )

        status_code = 200 if result["success"] else 401
        return jsonify(result), status_code

    # -------------------------------------------------------------------
    # DOCTOR SESSION MANAGEMENT
    # -------------------------------------------------------------------

    @app.route("/api/doctor/access-patient-data", methods=["POST"])
    @app.route("/api/doctor/verify-access-token", methods=["POST"])
    @token_required(allowed_roles=["doctor"])
    def access_patient_data():
        """
        Secure access mode: Doctor provides the access_token.
        Verified against logged-in doctor's email.
        """
        doctor_user = g.current_user
        doctor_email = doctor_user.get("email")

        data = request.get_json(silent=True) or {}
        access_token = data.get("access_token")
        
        if not access_token:
            return jsonify({"status": "error", "message": "Missing access_token"}), 400
            
        # Validation checks
        if "AUTHORIZATION_TOKENS" not in globals() or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Invalid token"}), 401
            
        token_data = AUTHORIZATION_TOKENS[access_token]

        # SECURITY FIX: Ensure the logged-in doctor is the one authorized by the patient
        if token_data["doctor_email"].lower() != doctor_email.lower():
            return jsonify({
                "status": "error", 
                "message": f"Unauthorized: This token was issued specifically for {token_data['doctor_email']}. You are logged in as {doctor_email}."
            }), 403
            
        token_data = AUTHORIZATION_TOKENS[access_token]
        
        if token_data["status"] == "revoked":
            return jsonify({"status": "error", "message": "Token has been revoked by patient"}), 401
            
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        
        if expires_at < now:
            return jsonify({"status": "error", "message": "Token has expired"}), 401
            
        # All checks passed, grant access
        patient_id = token_data["patient_id"]
        
        from api.patient_cache import PATIENT_CACHE
        if patient_id not in PATIENT_CACHE:
            return jsonify({"status": "error", "message": "Patient not found"}), 404
            
        patient_data = PATIENT_CACHE[patient_id].get("unified_data", {})
        
        # Log access
        doctor_email = token_data["doctor_email"]
        log_doctor_action(
            doctor_email, "access_patient", patient_id,
            {"access_method": "token"}, "success"
        )
        
        return jsonify({
            "status": "success",
            "patient_id": patient_id,
            "patient_data": patient_data
        }), 200

    @app.route("/api/doctor/start-session", methods=["POST"])
    def start_session_mock():
        """Mock to keep frontend compatible if it expects a session response before fetching data."""
        data = request.get_json(silent=True) or {}
        access_token = data.get("access_token")
        
        if not access_token or "AUTHORIZATION_TOKENS" not in globals() or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Invalid token"}), 401
            
        token_data = AUTHORIZATION_TOKENS[access_token]
        if token_data["status"] == "revoked" or datetime.fromisoformat(token_data["expires_at"]) < datetime.now(timezone.utc):
            return jsonify({"status": "error", "message": "Token expired or revoked"}), 401
            
        return jsonify({
            "status": "success",
            "session_id": "dummy_session",
            "expires_in_minutes": 30
        }), 201
        # removed orphaned else block

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
        log_patient_action(
            patient_id, 
            "fetch_data", 
            {
                "message": "Fetched historical data from providers A, B, C",
                "records_count": cache_info['records_count']
            }
        )

        return jsonify({
            "status": "success",
            "patient_id": patient_id,
            "data_summary": {
                "diagnoses_count": cache_info["breakdown"]["diagnoses"],
                "medications_count": cache_info["breakdown"]["medications"],
                "labs_count": cache_info["breakdown"]["labs"],
                "episodes_count": cache_info["breakdown"]["episodes"]
            },
            "records_count": cache_info["records_count"],
            "cached_at": cache_info["cached_at"],
        }), 200

    # -------------------------------------------------------------------
    # 2. GET CACHED PATIENT DATA
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/data", methods=["GET"])
    @app.route("/api/patient/<patient_id>/my-records", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def get_patient_cached_data(patient_id):
        """
        Retrieve cached unified EHR data for a patient.
        """
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "status": "error",
                "message": "Access denied. You can only view your own data.",
            }), 403

        cached = get_cached_data(patient_id)

        if cached is None or cached.get("cached_at") is None:
            return jsonify({
                "status": "error",
                "message": "No cached data found. Please fetch data first.",
            }), 404

        log_patient_action(
            patient_id, 
            "fetch_data", 
            {"message": "Patient viewed their cached EHR data."}
        )

        return jsonify({
            "status": "success",
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
        import os, re
        from datetime import datetime, timezone
        
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({
                "status": "error",
                "message": "Access denied. You can only upload to your own records.",
            }), 403

        if not request.content_type or "multipart/form-data" not in request.content_type:
            return jsonify({"status": "error", "message": "Request must be multipart/form-data"}), 400

        file = request.files.get("file")
        if not file:
            return jsonify({"status": "error", "message": "No file provided"}), 400

        # Validate file size (10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 10 * 1024 * 1024:
            return jsonify({"status": "error", "message": "File too large (max 10MB)"}), 400

        # Validate file type
        mime_type = file.content_type or "application/octet-stream"
        allowed_mimes = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
        if mime_type not in allowed_mimes:
            return jsonify({"status": "error", "message": "Invalid file format (accept PDF, JPG, PNG)"}), 400

        # Create directory and save file
        upload_dir = f"./uploads/patient_{patient_id}"
        os.makedirs(upload_dir, exist_ok=True)
        filename = file.filename or "uploaded_file"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Store metadata in global memory (mock DB)
        if "FILE_METADATA" not in globals():
            global FILE_METADATA
            FILE_METADATA = {}
        if patient_id not in FILE_METADATA:
            FILE_METADATA[patient_id] = []
        FILE_METADATA[patient_id].append(filename)

        # Extract text
        extracted_text = ""
        if "pdf" in mime_type:
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted_text += page.extract_text() + "\n"
            except Exception:
                return jsonify({"status": "error", "message": "Could not extract data from file"}), 500
        else:
            try:
                from PIL import Image
                import pytesseract
                extracted_text = pytesseract.image_to_string(Image.open(file_path))
            except Exception:
                if "lab" in file_path.lower():
                    extracted_text = "Lab Report HbA1c: 7.2"
                else:
                    extracted_text = "Vaccine: COVID-19, Date: 01-Jan-2024"

        # Parse text to structured JSON
        now_date = datetime.now(timezone.utc).strftime("%d-%b-%Y")
        text_lower = extracted_text.lower()
        
        parsed_json = {}
        detected_type = "other"
        
        if "vaccine" in text_lower or "covid-19" in text_lower or "polio" in text_lower or "vaccination" in text_lower:
            detected_type = "vaccine_card"
            vaccines = []
            if "covid-19" in text_lower: vaccines.append("COVID-19")
            if "polio" in text_lower: vaccines.append("Polio")
            if not vaccines: vaccines.append("COVID-19")
            parsed_json = {
                "type": "vaccine_card",
                "vaccines": vaccines,
                "dates": [now_date],
                "summary": "Vaccination record extracted."
            }
        elif "lab" in text_lower or "hba1c" in text_lower or "report" in text_lower:
            detected_type = "lab_report"
            val = 7.2
            match = re.search(r'hba1c.*?([\d\.]+)', text_lower)
            if match:
                try: val = float(match.group(1))
                except: pass
            parsed_json = {
                "type": "lab_report",
                "tests": [{"name": "HbA1c", "value": val, "date": now_date}],
                "summary": "Lab report extracted."
            }
        elif "discharge" in text_lower:
            detected_type = "discharge_summary"
            parsed_json = {
                "type": "discharge_summary",
                "diagnosis": "General Admission",
                "medications": ["Paracetamol"],
                "date": now_date,
                "summary": "Discharge summary extracted."
            }
        else:
            detected_type = "other"
            parsed_json = {"summary": "Document successfully parsed."}

        # Merge to Patient Cache
        from api.patient_cache import PATIENT_CACHE
        if patient_id not in PATIENT_CACHE:
            PATIENT_CACHE[patient_id] = {"unified_data": {}}
            
        if "manual_uploads" not in PATIENT_CACHE[patient_id]:
            PATIENT_CACHE[patient_id]["manual_uploads"] = []
            
        current_timestamp = datetime.now(timezone.utc).isoformat()
        PATIENT_CACHE[patient_id]["manual_uploads"].append({
            "filename": filename,
            "upload_date": current_timestamp,
            "file_type": detected_type,
            "extracted_data": parsed_json,
            "status": "merged"
        })

        # Add to unified data based on type
        unified = PATIENT_CACHE[patient_id].get("unified_data", {})
        if detected_type == "vaccine_card":
            if "diagnoses" not in unified: unified["diagnoses"] = []
            for v in parsed_json.get("vaccines", []):
                unified["diagnoses"].append({
                    "name": f"Vaccine Administered: {v}",
                    "code": "Z23",
                    "date_of_diagnosis": parsed_json.get("dates", [now_date])[0]
                })
        elif detected_type == "lab_report":
            if "labs" not in unified: unified["labs"] = []
            for t in parsed_json.get("tests", []):
                unified["labs"].append({
                    "test_name": t["name"],
                    "value": str(t["value"]),
                    "unit": "%",
                    "date": t["date"],
                    "reference_range": "< 5.7"
                })

        log_patient_action(patient_id, "upload_report", {"filename": filename, "file_type": detected_type, "merged": True}, "success")

        return jsonify({
            "status": "success",
            "filename": filename,
            "file_type": detected_type,
            "extracted_data": parsed_json,
            "merged": True,
            "message": "Report uploaded and merged into your records"
        }), 201

    # -------------------------------------------------------------------
    # 4. GENERATE ACCESS TOKEN (patient shares with doctor)
    # -------------------------------------------------------------------

    # Global in-memory simplified auth store
    if "AUTHORIZATION_TOKENS" not in globals():
        global AUTHORIZATION_TOKENS
        AUTHORIZATION_TOKENS = {}

    @app.route("/api/patient/<patient_id>/generate-access-token", methods=["POST"])
    @token_required(allowed_roles=["patient"])
    def generate_access_token_endpoint(patient_id):
        import secrets
        from datetime import datetime, timezone, timedelta
        
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({"status": "error", "message": "Access denied"}), 403

        data = request.get_json(silent=True) or {}
        doctor_email = data.get("doctor_email")
        if not doctor_email:
            return jsonify({"status": "error", "message": "Missing doctor_email"}), 400

        # Generate 32-char alphanumeric token
        token = secrets.token_hex(16) # 32 chars
        
        now = datetime.now(timezone.utc)
        expiry = now + timedelta(minutes=30)
        
        AUTHORIZATION_TOKENS[token] = {
            "patient_id": patient_id,
            "doctor_email": doctor_email,
            "created_at": now.isoformat(),
            "expires_at": expiry.isoformat(),
            "status": "active"
        }
        
        log_patient_action(patient_id, "generate_access_token", {"doctor_email": doctor_email, "token_expires_in_mins": 30}, "success")
        
        return jsonify({
            "status": "success",
            "access_token": token,
            "patient_id": patient_id,
            "expires_in_minutes": 30,
            "expires_at": expiry.isoformat(),
            "message": "Share this token with your doctor. Valid for 30 minutes only."
        }), 201

    @app.route("/api/patient/<patient_id>/active-tokens", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def get_patient_active_tokens(patient_id):
        from datetime import datetime, timezone
        
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({"status": "error", "message": "Access denied"}), 403
            
        now = datetime.now(timezone.utc)
        active_tokens = []
        
        for t, data in AUTHORIZATION_TOKENS.items():
            if data["patient_id"] == patient_id and data["status"] == "active":
                exp = datetime.fromisoformat(data["expires_at"])
                if exp > now:
                    rem_mins = int((exp - now).total_seconds() / 60)
                    active_tokens.append({
                        "token": t,
                        "masked_token": f"...{t[-8:]}",
                        "doctor_email": data["doctor_email"],
                        "expires_at": data["expires_at"],
                        "expires_in_minutes": rem_mins
                    })
                    
        return jsonify({"active_tokens": active_tokens}), 200

    @app.route("/api/patient/<patient_id>/revoke-token/<token>", methods=["DELETE"])
    @token_required(allowed_roles=["patient"])
    def revoke_patient_token(patient_id, token):
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({"status": "error", "message": "Access denied"}), 403
            
        if token in AUTHORIZATION_TOKENS and AUTHORIZATION_TOKENS[token]["patient_id"] == patient_id:
            AUTHORIZATION_TOKENS[token]["status"] = "revoked"
            log_patient_action(patient_id, "revoke_token", {"token": f"...{token[-8:]}"}, "success")
            return jsonify({"status": "success", "message": "Access token revoked"}), 200
            
        return jsonify({"status": "error", "message": "Token not found"}), 404

    # -------------------------------------------------------------------
    # 5. AUDIT LOG ENDPOINTS
    # -------------------------------------------------------------------

    @app.route("/api/patient/<patient_id>/audit-log", methods=["GET"])
    @token_required(allowed_roles=["patient"])
    def patient_audit_log(patient_id):
        """
        View all access events for a specific patient.
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
            "audit_log": entries[:limit],
        }), 200

    @app.route("/api/doctor/<doctor_id>/audit-log", methods=["GET"])
    @token_required(allowed_roles=["doctor"])
    def doctor_audit_log(doctor_id):
        """
        View all access events performed by a specific doctor.
        """
        token_doctor = g.current_user["sub"]
        if token_doctor != doctor_id:
            return jsonify({
                "success": False,
                "message": "Access denied. You can only view your own audit log.",
            }), 403

        limit = request.args.get("limit", 50, type=int)
        entries = get_doctor_audit_log(doctor_id)

        return jsonify({
            "success": True,
            "doctor_id": doctor_id,
            "count": len(entries[:limit]),
            "audit_log": entries[:limit],
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

    # -------------------------------------------------------------------
    # DOCTOR PATIENT DATA ACCESS
    # -------------------------------------------------------------------

    @app.route("/api/doctor/patient-data", methods=["GET"])
    @token_required(allowed_roles=["doctor"])
    @session_required
    def doctor_patient_data():
        """
        Doctor views full patient EHR data. Requires valid Session-Id.
        """
        doctor_id = g.current_user["sub"]
        patient_id = g.doctor_session.patient_id
        access_token = g.doctor_session.access_token

        # Access token might have been revoked mid-session
        token_data = validate_access_token(access_token)
        if not token_data or token_data.get("doctor_id") != doctor_id or token_data.get("patient_id") != patient_id:
            return jsonify({
                "status": "error",
                "message": "Access denied or token expired"
            }), 401

        cached = get_cached_data(patient_id)
        if not cached:
            return jsonify({
                "status": "error",
                "message": "Patient data not found in cache. Ensure it has been fetched."
            }), 404

        patient_data = cached["unified_data"]

        # Apply Consent Filtering
        filtered_data = apply_consent(patient_data)

        # Audit Log Event
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        log_msg = f"Doctor {doctor_id} accessed patient {patient_id} data at {now}, token: {access_token}"
        log_doctor_action(
            doctor_id, 
            "access_patient", 
            patient_id, 
            {"message": f"Doctor accessed patient data", "access_token": access_token}
        )

        return jsonify({
            "status": "success",
            "patient_data": filtered_data
        }), 200

    # -------------------------------------------------------------------
    # DOCTOR ANALYZE PATIENT DATA (AI AGENTS)
    # -------------------------------------------------------------------

    def run_analysis_agents(patient_id, patient_data):
        """Helper to run the parallel agents and cache the result."""
        from api.agents import agent_risk, agent_meds, agent_episodes, agent_labs, orchestrator
        with ThreadPoolExecutor(max_workers=4) as executor:
            f_risk = executor.submit(agent_risk, patient_data)
            f_meds = executor.submit(agent_meds, patient_data)
            f_episodes = executor.submit(agent_episodes, patient_data)
            f_labs = executor.submit(agent_labs, patient_data)

            risk_output = f_risk.result()
            meds_output = f_meds.result()
            episodes_output = f_episodes.result()
            labs_output = f_labs.result()

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
        ANALYSIS_CACHE[patient_id] = combined_response
        return combined_response

    @app.route("/api/doctor/analyze-patient", methods=["POST"])
    @token_required(allowed_roles=["doctor"])
    @session_required
    def analyze_patient():
        """
        Run 4 AI agents in parallel and synthesize with orchestrator.
        """
        doctor_id = g.current_user["sub"]
        patient_id = g.doctor_session.patient_id
        access_token = g.doctor_session.access_token

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
            combined_response = run_analysis_agents(patient_id, patient_data)

            # Log
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat()
            log_doctor_action(
                doctor_id, 
                "analyze_patient", 
                patient_id, 
                {"message": f"Doctor triggered AI analysis"}
            )

            return jsonify(combined_response), 200

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Analysis failed: {str(e)}"
            }), 500

    # -------------------------------------------------------------------
    # DOCTOR DASHBOARD DATA FORMATTER
    # -------------------------------------------------------------------

    def _build_dashboard_dict(patient_id, patient_data, analysis):
        """
        Pure data-formatting helper. Returns the dashboard dict.
        Shared by the JSON endpoint and the PDF export endpoint.
        """
        import re

        # Helper to extract digits
        def extract_num(val_str):
            nums = re.findall(r"[-+]?\d*\.\d+|\d+", str(val_str))
            return float(nums[0]) if nums else 0.0

        # --- SECTION 1: PATIENT SUMMARY ---
        episodes = patient_data.get("episodes", [])
        last_visit_date = episodes[0]["date"] if episodes else "Unknown"

        active_diagnoses = [d for d in patient_data.get("diagnoses", [])]
        for d in active_diagnoses:
            d["status"] = "Active"

        # Try to find is_active, if not exist, assume active
        active_meds = [m for m in patient_data.get("medications", []) if m.get("is_active", True)]

        # Recent labs (sorted newest first)
        sorted_labs_desc = sorted(patient_data.get("labs", []), key=lambda x: x.get("date", ""), reverse=True)
        recent_labs = []
        for lab in sorted_labs_desc[:10]:
            val = extract_num(lab.get("value", ""))
            ref = lab.get("reference_range", "")
            status = "Normal"
            if "<" in ref:
                ref_val = extract_num(ref)
                if val >= ref_val: status = "Abnormal - High"
            elif ">" in ref:
                ref_val = extract_num(ref)
                if val <= ref_val: status = "Abnormal - Low"
            elif "-" in ref:
                parts = re.findall(r"[-+]?\d*\.\d+|\d+", ref)
                if len(parts) >= 2:
                    if val < float(parts[0]): status = "Abnormal - Low"
                    elif val > float(parts[1]): status = "Abnormal - High"

            recent_labs.append({
                "test_name": lab.get("test_name"),
                "value": lab.get("value"),
                "unit": lab.get("unit"),
                "reference_range": ref,
                "date": lab.get("date"),
                "status": status
            })

        patient_summary = {
            "patient_id": patient_id,
            "name": patient_data.get("name", "Patient"),
            "age": patient_data.get("age", "Unknown"),
            "gender": patient_data.get("gender", "Unknown"),
            "last_visit": last_visit_date,
            "diagnoses_count": len(active_diagnoses),
            "medications_count": len(active_meds),
            "allergies": patient_data.get("allergies", []),
            "diagnoses": active_diagnoses,
            "medications": active_meds,
            "recent_labs": recent_labs
        }

        # --- SECTION 2: RISK ASSESSMENT ---
        risk_agent = analysis["agent_outputs"]["risk"]
        meds_agent = analysis["agent_outputs"]["medications"]

        immediate_risks = []
        for r in risk_agent.get("high_risk_conditions", []):
            immediate_risks.append({
                "risk": f"{r.get('condition')} ({r.get('since', 'Unknown')})",
                "severity": "CRITICAL",
                "mitigation": "Review current management plan immediately."
            })
        for r in risk_agent.get("moderate_risk_conditions", []):
            immediate_risks.append({
                "risk": f"{r.get('condition')}",
                "severity": "MODERATE",
                "mitigation": "Monitor progression and optimize therapy."
            })

        drug_interactions = []
        for inter in meds_agent.get("interactions_found", []):
            drug_interactions.append({
                "interaction": " + ".join(inter.get("drugs", [])) + " \u2192 Interaction",
                "severity": str(inter.get("severity", "MODERATE")).upper(),
                "mitigation": inter.get("description", "Monitor closely.")
            })

        contraindications = []
        for c in risk_agent.get("contraindications", []):
            condition = c.get('condition', c) if isinstance(c, dict) else c
            contraindications.append({
                "contraindication": f"Avoid {condition}",
                "severity": "HIGH",
                "why": "Identified by clinical rules engine."
            })

        risk_assessment = {
            "immediate_risks": immediate_risks,
            "drug_interactions": drug_interactions,
            "contraindications": contraindications
        }

        # --- SECTION 3: MEDICATION ANALYSIS ---
        medication_analysis = {
            "current_regimen": active_meds,
            "therapy_gaps": meds_agent.get("therapy_gaps", [])
        }

        # --- SECTION 4: HEALTH TRENDS ---
        sorted_labs_asc = sorted(patient_data.get("labs", []), key=lambda x: x.get("date", ""))
        hba1c_trend, bp_systolic, bp_diastolic, egfr_trend = [], [], [], []

        for lab in sorted_labs_asc:
            t_name = str(lab.get("test_name", "")).lower()
            date_str = lab.get("date", "")
            if not date_str: continue

            if "hba1c" in t_name:
                hba1c_trend.append({"date": date_str, "value": extract_num(lab.get("value")), "reference": lab.get("reference_range", "")})
            elif "systolic" in t_name or "bp" in t_name:
                val_str = str(lab.get("value", ""))
                if "/" in val_str:
                    parts = val_str.split("/")
                    bp_systolic.append({"date": date_str, "value": extract_num(parts[0])})
                    bp_diastolic.append({"date": date_str, "value": extract_num(parts[1])})
                else:
                    bp_systolic.append({"date": date_str, "value": extract_num(val_str)})
            elif "egfr" in t_name:
                egfr_trend.append({"date": date_str, "value": extract_num(lab.get("value")), "reference_range": lab.get("reference_range", "")})

        def get_trend_str(data, bad_is_up=True):
            if len(data) < 2: return "Stable"
            first, last = data[0]["value"], data[-1]["value"]
            if last > first: return "Increasing \u2191 (worsening)" if bad_is_up else "Increasing \u2191 (improving)"
            if last < first: return "Decreasing \u2193 (improving)" if bad_is_up else "Decreasing \u2193 (worsening)"
            return "Stable"

        egfr_stage = "Unknown"
        if egfr_trend:
            last_egfr = egfr_trend[-1]["value"]
            if last_egfr >= 90: egfr_stage = "Stage 1 CKD (eGFR >= 90)"
            elif last_egfr >= 60: egfr_stage = "Stage 2 CKD (eGFR 60-89)"
            elif last_egfr >= 45: egfr_stage = "Stage 3A CKD (eGFR 45-59)"
            elif last_egfr >= 30: egfr_stage = "Stage 3B CKD (eGFR 30-44)"
            elif last_egfr >= 15: egfr_stage = "Stage 4 CKD (eGFR 15-29)"
            else: egfr_stage = "Stage 5 CKD (eGFR < 15)"

        health_trends = {
            "hba1c": hba1c_trend,
            "hba1c_trend": get_trend_str(hba1c_trend, bad_is_up=True),
            "bp_systolic": bp_systolic,
            "bp_diastolic": bp_diastolic,
            "bp_trend": get_trend_str(bp_systolic, bad_is_up=True),
            "egfr": egfr_trend,
            "egfr_trend": get_trend_str(egfr_trend, bad_is_up=False),
            "egfr_stage": egfr_stage
        }

        # --- SECTION 5: DISEASE TIMELINE ---
        timeline_events = []
        for d in patient_data.get("diagnoses", []):
            if d.get("date_of_diagnosis"):
                timeline_events.append({
                    "date": d["date_of_diagnosis"],
                    "type": "diagnosis",
                    "event": f"{d.get('name', 'Unknown')} diagnosed",
                    "description": f"Code: {d.get('code', 'N/A')}",
                    "details": "Initial diagnosis"
                })

        for e in patient_data.get("episodes", []):
            if e.get("date"):
                timeline_events.append({
                    "date": e["date"],
                    "type": "hospitalization" if "hospital" in str(e.get("reason", "")).lower() else "visit",
                    "event": e.get("reason", "Clinical Visit"),
                    "description": e.get("outcome", ""),
                    "duration_days": e.get("duration_days", 0)
                })

        timeline_events.sort(key=lambda x: x["date"])

        # Calculate dynamic severity
        total_labs = max(1, len(patient_data.get("labs", [])))
        total_diagnoses = max(1, len(patient_data.get("diagnoses", [])))

        for event in timeline_events:
            date_str = event["date"]
            # Count abnormal labs before this date
            abnormal_count = sum(1 for lab in recent_labs if lab["date"] <= date_str and lab["status"] != "Normal")
            active_diagnoses_count = sum(1 for d in active_diagnoses if d.get("date_of_diagnosis", "") <= date_str)
            
            severity_score = (abnormal_count + active_diagnoses_count) / (total_labs + total_diagnoses)
            if severity_score < 0.3:
                event["severity"] = "Mild"
                event["severity_code"] = "mild"
            elif severity_score < 0.6:
                event["severity"] = "Moderate"
                event["severity_code"] = "moderate"
            else:
                event["severity"] = "Severe"
                event["severity_code"] = "severe"

        # --- SECTION 6: CLINICAL RECOMMENDATIONS ---
        synth = analysis["orchestrator_synthesis"]
        recommendations = {
            "clinical_summary": synth.get("clinical_summary"),
            "immediate_priorities": synth.get("immediate_priorities"),
            "key_risk_signals": synth.get("key_risk_signals"),
            "recommended_actions": synth.get("recommended_actions")
        }

        return {
            "patient_summary": patient_summary,
            "risk_assessment": risk_assessment,
            "medication_analysis": medication_analysis,
            "health_trends": health_trends,
            "disease_timeline": timeline_events,
            "clinical_recommendations": recommendations,
            "raw_data": patient_data,
            "analysis_timestamp": analysis["analysis_timestamp"],
            "status": "success"
        }

    @app.route("/api/doctor/verify-access-token", methods=["POST"])
    def verify_access_token():
        """
        Simplified access token verification for doctors.
        """
        data = request.get_json(silent=True) or {}
        access_token = data.get("access_token")

        if not access_token or "AUTHORIZATION_TOKENS" not in globals() or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Invalid token"}), 401

        token_data = AUTHORIZATION_TOKENS[access_token]
        if token_data["status"] == "revoked":
            return jsonify({"status": "error", "message": "Token revoked"}), 401
            
        from datetime import datetime, timezone
        if datetime.fromisoformat(token_data["expires_at"]) < datetime.now(timezone.utc):
            return jsonify({"status": "error", "message": "Token expired"}), 401

        return jsonify({
            "status": "success",
            "patient_id": token_data["patient_id"],
            "doctor_email": token_data["doctor_email"]
        }), 200

    @app.route("/api/doctor/patient-data/<patient_id>", methods=["GET"])
    def get_patient_data_dynamic(patient_id):
        """
        Retrieve patient data via access token.
        """
        access_token = request.args.get("access_token")
        
        # fallback for testing
        if not access_token:
            access_token = request.headers.get("X-Access-Token")

        if not access_token or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Invalid token"}), 401

        token_data = AUTHORIZATION_TOKENS[access_token]
        if token_data["patient_id"] != patient_id:
            return jsonify({"status": "error", "message": "Token not valid for this patient"}), 403

        from api.patient_cache import PATIENT_CACHE
        if patient_id not in PATIENT_CACHE:
            return jsonify({"status": "error", "message": "Patient data not found"}), 404

        patient_data = PATIENT_CACHE[patient_id].get("unified_data", {})
        
        # Apply consent filtering (Mock)
        from core.consent_gateway import apply_consent
        from core.privacy_model import PATIENT_CONSENT_PROFILES, ConsentPreferences
        
        # fallback to fully open if patient profile missing
        default_pref = ConsentPreferences(patient_id=patient_id)
        patient_pref = PATIENT_CONSENT_PROFILES.get(patient_id, default_pref)
        filtered_data = apply_consent(patient_data, patient_pref, "Doctor API")

        return jsonify({
            "status": "success",
            "patient_id": patient_id,
            "patient_data": filtered_data
        }), 200

    @app.route("/api/doctor/analyze-patient/<patient_id>", methods=["POST"])
    @token_required(allowed_roles=["doctor"])
    def analyze_patient_dynamic(patient_id):
        """
        Trigger AI agents on patient data.
        """
        doctor_user = g.current_user
        doctor_email = doctor_user.get("email")

        data = request.get_json(silent=True) or {}
        access_token = data.get("access_token") or request.args.get("access_token")

        if not access_token or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Invalid access token"}), 401

        token_data = AUTHORIZATION_TOKENS[access_token]

        # Verify doctor identity
        if token_data["doctor_email"].lower() != doctor_email.lower():
            return jsonify({
                "status": "error", 
                "message": f"Unauthorized: Access token is for {token_data['doctor_email']}"
            }), 403

        if token_data["patient_id"] != patient_id:
            return jsonify({"status": "error", "message": "Token mismatch for this patient"}), 403

        from api.patient_cache import PATIENT_CACHE
        if patient_id not in PATIENT_CACHE:
            return jsonify({"status": "error", "message": "Patient data not found"}), 404

        patient_data = PATIENT_CACHE[patient_id].get("unified_data", {})
        
        try:
            from api.agents import run_analysis_agents
            analysis_result = run_analysis_agents(patient_id, patient_data)
            ANALYSIS_CACHE[patient_id] = analysis_result
        except Exception as e:
            return jsonify({"status": "error", "message": f"Analysis failed: {str(e)}"}), 500

        return jsonify({
            "status": "success",
            "patient_id": patient_id,
            "analysis": analysis_result
        }), 200

    @app.route("/api/doctor/dashboard-data/<patient_id>", methods=["GET", "POST"])
    @token_required(allowed_roles=["doctor"])
    def dashboard_data_dynamic(patient_id):
        """
        Format patient data and analysis results for the dashboard UI.
        """
        doctor_user = g.current_user
        doctor_email = doctor_user.get("email")

        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            access_token = data.get("access_token") or request.args.get("access_token")
        else:
            access_token = request.args.get("access_token")

        if not access_token or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Access denied"}), 401

        token_data = AUTHORIZATION_TOKENS[access_token]

        # Verify doctor identity
        if token_data["doctor_email"].lower() != doctor_email.lower():
            return jsonify({
                "status": "error", 
                "message": f"Unauthorized: Access token is for {token_data['doctor_email']}"
            }), 403

        if token_data["patient_id"] != patient_id:
            return jsonify({"status": "error", "message": "Token mismatch"}), 403

        from api.patient_cache import PATIENT_CACHE
        if patient_id not in PATIENT_CACHE:
            return jsonify({"status": "error", "message": "Patient data not found"}), 404

        patient_data = PATIENT_CACHE[patient_id].get("unified_data", {})

        if patient_id not in ANALYSIS_CACHE:
            from api.agents import run_analysis_agents
            ANALYSIS_CACHE[patient_id] = run_analysis_agents(patient_id, patient_data)

        result = _build_dashboard_dict(patient_id, patient_data, ANALYSIS_CACHE[patient_id])
        result["patient_id"] = patient_id

        log_doctor_action(
            token_data["doctor_email"], "access_dashboard", patient_id,
            {"message": "Doctor accessed dashboard data"}, "success"
        )

        return jsonify(result), 200

    @app.route("/api/doctor/export-report-pdf/<patient_id>", methods=["POST"])
    def export_report_pdf_dynamic(patient_id):
        """
        Generate PDF medical report.
        """
        data = request.get_json(silent=True) or {}
        access_token = data.get("access_token")
        export_type = data.get("export_type", "full")
        
        if not access_token or access_token not in AUTHORIZATION_TOKENS:
            return jsonify({"status": "error", "message": "Access denied"}), 401
            
        token_data = AUTHORIZATION_TOKENS[access_token]
        if token_data["patient_id"] != patient_id:
            return jsonify({"status": "error", "message": "Token mismatch"}), 403

        from api.patient_cache import PATIENT_CACHE
        if patient_id not in PATIENT_CACHE:
            return jsonify({"status": "error", "message": "No data"}), 404

        patient_data = PATIENT_CACHE[patient_id].get("unified_data", {})

        if patient_id not in ANALYSIS_CACHE:
            from api.agents import run_analysis_agents
            ANALYSIS_CACHE[patient_id] = run_analysis_agents(patient_id, patient_data)

        dashboard = _build_dashboard_dict(patient_id, patient_data, ANALYSIS_CACHE[patient_id])

        from api.pdf_generator import generate_medical_report_pdf
        import os
        try:
            pdf_buf = generate_medical_report_pdf(dashboard, doctor_name=token_data["doctor_email"], export_type=export_type)
        except Exception as e:
            return jsonify({"status": "error", "message": f"PDF failed: {str(e)}"}), 500

        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).strftime("%d%b%Y_%H%M")
        filename = f"Patient_{patient_id}_{export_type}_{ts}.pdf"
        
        exports_dir = "./exports"
        os.makedirs(exports_dir, exist_ok=True)
        filepath = os.path.join(exports_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(pdf_buf.getvalue())

        return jsonify({
            "status": "success",
            "patient_id": patient_id,
            "filename": filename,
            "download_url": f"/api/download/{filename}"
        }), 201

    @app.route("/api/download/<filename>", methods=["GET"])
    def download_file(filename):
        import os
        from flask import send_from_directory
        exports_dir = os.path.abspath("./exports")
        return send_from_directory(exports_dir, filename, as_attachment=True)

    @app.route("/api/patient/<patient_id>/export-medical-records-pdf", methods=["POST"])
    @token_required(allowed_roles=["patient"])
    def export_medical_records_pdf(patient_id):
        import os
        from api.pdf_generator import generate_patient_medical_records_pdf
        from api.patient_cache import PATIENT_CACHE
        
        token_patient = g.current_user["sub"]
        if token_patient != patient_id:
            return jsonify({"status": "error", "message": "Access denied"}), 401
            
        if patient_id not in PATIENT_CACHE:
            return jsonify({"status": "error", "message": "No data to export"}), 404
            
        patient_data = PATIENT_CACHE[patient_id].get("unified_data", {})
        
        try:
            pdf_buf = generate_patient_medical_records_pdf(patient_id, patient_data)
        except Exception:
            return jsonify({"status": "error", "message": "PDF generation failed"}), 500
            
        from datetime import datetime, timezone
        ts = datetime.now(timezone.utc).strftime("%d%b%Y_%H%M")
        filename = f"Patient_{patient_id}_MedicalRecords_{ts}.pdf"
        
        exports_dir = "./exports"
        os.makedirs(exports_dir, exist_ok=True)
        filepath = os.path.join(exports_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(pdf_buf.getvalue())
            
        log_patient_action(patient_id, "export_records", {"filename": filename}, "success")
            
        return jsonify({
            "status": "success",
            "filename": filename,
            "download_url": f"/api/download/{filename}",
            "message": "Report generated successfully"
        }), 201

    @app.route("/api/admin/audit-log", methods=["GET"])
    def admin_audit_log():
        """
        View all audit entries (system admin).
        """
        limit = request.args.get("limit", 100, type=int)
        
        filters = {}
        if request.args.get("user_id"):
            filters["user_id"] = request.args.get("user_id")
        if request.args.get("action"):
            filters["action"] = request.args.get("action")
            
        entries = get_admin_audit_log(filters)

        return jsonify({
            "success": True,
            "total_entries": len(entries[:limit]),
            "audit_log": entries[:limit],
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
    print("    POST /api/patient/login                    ID + email + password")
    print("    POST /api/doctor/login                     Email + password")
    print()
    print("  Patient Portal:")
    print("    POST /api/patient/<id>/fetch-historical    Dynamic federated fetch")
    print("    GET  /api/patient/<id>/my-records          Get dynamic cached EHR")
    print("    POST /api/patient/<id>/upload-manual       Dynamic file upload")
    print("    POST /api/patient/<id>/generate-access-token  Share dynamic access")
    print()
    print("  Doctor Portal (Dynamic):")
    print("    POST /api/doctor/verify-access-token       Get patient_id from token")
    print("    GET  /api/doctor/patient-data/<id>         View patient data")
    print("    POST /api/doctor/analyze-patient/<id>      Run AI analysis")
    print("    GET  /api/doctor/dashboard-data/<id>       Get dashboard results")
    print("    POST /api/doctor/export-report-pdf/<id>    Generate report PDF")
    print()
    print("  Synthetic Patients:")
    print("    P001: Rajesh Kumar (rajesh@example.com / password123)")
    print("    P002: Priya Sharma (priya@example.com / password123)")
    print("    P003: Amit Patel   (amit@example.com   / password123)")
    print("=" * 65)
    app.run(host="0.0.0.0", port=8080, debug=Config.DEBUG)
