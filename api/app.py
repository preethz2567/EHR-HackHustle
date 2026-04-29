"""
app.py — Flask REST API
========================
PS-1: Privacy-Preserving Patient Memory Layer

Endpoints:
  POST /api/patient/auth     — Patient biometric + OTP authentication
  POST /api/doctor/auth      — Doctor email + password authentication
  POST /api/doctor/session    — Generate 30-min session token for patient data
  GET  /api/patient/data      — Fetch patient EHR (patient token required)
  GET  /api/doctor/patient/<id> — Doctor views patient dashboard (session required)
  GET  /api/audit/log         — View audit trail
  GET  /api/health            — Health check

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
)


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
    # PATIENT DATA (self-access)
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

    # -------------------------------------------------------------------
    # DOCTOR VIEW PATIENT (session-gated)
    # -------------------------------------------------------------------

    @app.route("/api/doctor/patient/<patient_id>", methods=["GET"])
    @token_required(allowed_roles=["session"])
    def doctor_view_patient(patient_id):
        """
        Doctor views a patient's unified dashboard data.

        Requires: Session JWT in Authorization header (30-min window).
        The session token must match the requested patient_id.

        Response:
            Full patient data + AI-ready structure.
        """
        # Verify session is for this specific patient
        session_patient = g.current_user.get("patient_id")
        if session_patient != patient_id:
            return jsonify({
                "success": False,
                "message": f"Session token is for patient {session_patient}, "
                           f"not {patient_id}",
            }), 403

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
            "doctor_id": g.current_user["sub"],
            "data": patient,
            "session_info": {
                "type": "patient_data_access",
                "expires_at": g.current_user.get("exp"),
            },
        }), 200

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
    print("=" * 60)
    print("  PS-1: Privacy-Preserving Patient Memory Layer API")
    print("=" * 60)
    print()
    print("  Endpoints:")
    print("    POST /api/patient/auth        Patient biometric + OTP login")
    print("    POST /api/doctor/auth         Doctor email + password login")
    print("    POST /api/doctor/session      Get 30-min session token")
    print("    GET  /api/patient/data        Patient fetches own EHR")
    print("    GET  /api/doctor/patient/<id> Doctor views patient (session)")
    print("    GET  /api/audit/log           Audit trail")
    print("    GET  /api/health              Health check")
    print()
    print("  Demo Credentials:")
    print("    Patient: P001, fingerprint: P001-fingerprint-template, OTP: 123456")
    print("    Doctor:  dr.sharma@cityhospital.in / doctor123")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
