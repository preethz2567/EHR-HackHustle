"""
auth.py — Authentication Module
================================
Handles patient biometric+OTP auth and doctor email+password auth.
Generates and verifies JWT tokens.
"""

import hashlib
import time
from datetime import datetime, timezone, timedelta
from functools import wraps

import bcrypt
import jwt
from flask import request, jsonify, g

from api.config import Config


# ---------------------------------------------------------------------------
# Mock credential stores (replace with DB in production)
# ---------------------------------------------------------------------------

# Simulated patient biometric hashes (fingerprint hash per patient)
# In production: stored in a secure biometric vault, never raw
PATIENT_BIOMETRIC_STORE = {
    "P001": {
        "fingerprint_hash": hashlib.sha256(b"P001-fingerprint-template").hexdigest(),
        "iris_hash": hashlib.sha256(b"P001-iris-template").hexdigest(),
        "name": "Rajesh Kumar",
        "email": "rajesh@example.com",
        "abha_id": "ABHA-1234-5678-9001",
    },
    "P002": {
        "fingerprint_hash": hashlib.sha256(b"P002-fingerprint-template").hexdigest(),
        "iris_hash": hashlib.sha256(b"P002-iris-template").hexdigest(),
        "name": "Priya Sharma",
        "abha_id": "ABHA-1234-5678-9002",
    },
    "P003": {
        "fingerprint_hash": hashlib.sha256(b"P003-fingerprint-template").hexdigest(),
        "iris_hash": hashlib.sha256(b"P003-iris-template").hexdigest(),
        "name": "Amit Patel",
        "abha_id": "ABHA-1234-5678-9003",
    },
    "P004": {
        "fingerprint_hash": hashlib.sha256(b"P004-fingerprint-template").hexdigest(),
        "iris_hash": hashlib.sha256(b"P004-iris-template").hexdigest(),
        "name": "Sunita Reddy",
        "abha_id": "ABHA-1234-5678-9004",
    },
    "P005": {
        "fingerprint_hash": hashlib.sha256(b"P005-fingerprint-template").hexdigest(),
        "iris_hash": hashlib.sha256(b"P005-iris-template").hexdigest(),
        "name": "Vikram Singh",
        "abha_id": "ABHA-1234-5678-9005",
    },
}

# Simulated doctor credentials
# Passwords are bcrypt-hashed versions of the plaintext shown in comments
_DOCTOR_PASSWORDS = {
    "dr.amit@hospital.com": "doctor123",            # Demo password
    "dr.sharma@cityhospital.in": "doctor123",       # Demo password
    "dr.gupta@metromed.in": "doctor123",
    "dr.iyer@regional.in": "doctor123",
}

DOCTOR_CREDENTIAL_STORE = {}
for _email, _pw in _DOCTOR_PASSWORDS.items():
    DOCTOR_CREDENTIAL_STORE[_email] = {
        "password_hash": bcrypt.hashpw(_pw.encode(), bcrypt.gensalt()).decode(),
        "doctor_id": f"DR-{_email.split('@')[0].replace('dr.', '').upper()}",
        "name": _email.split("@")[0].replace("dr.", "Dr. ").replace(".", " ").title(),
        "hospital": _email.split("@")[1].split(".")[0].title() + " Hospital",
    }


from api.audit import log_patient_action, log_doctor_action


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def generate_token(payload: dict, expiry_seconds: int) -> str:
    """Create a signed JWT with an expiry."""
    now = datetime.now(timezone.utc)
    payload.update({
        "iat": now,
        "exp": now + timedelta(seconds=expiry_seconds),
    })
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT.
    Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure.
    """
    return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])


# ---------------------------------------------------------------------------
# Patient authentication
# ---------------------------------------------------------------------------

def authenticate_patient(patient_id: str, biometric_type: str,
                         biometric_data: str, otp: str) -> dict:
    """
    Simulate biometric + OTP verification for a patient.

    Args:
        patient_id:      e.g. "P001"
        biometric_type:  "fingerprint" or "iris"
        biometric_data:  raw biometric string (simulated)
        otp:             one-time password string

    Returns:
        dict with 'success', 'token', 'patient_id', 'message'
    """
    # 1. Check patient exists
    if patient_id not in PATIENT_BIOMETRIC_STORE:
        log_patient_action(patient_id, "login", {"message": "Unknown patient ID"}, "failed")
        return {
            "success": False,
            "token": None,
            "patient_id": patient_id,
            "message": "Patient not found",
        }

    patient = PATIENT_BIOMETRIC_STORE[patient_id]

    # 2. Verify biometric (simulated hash comparison)
    if biometric_type not in ("fingerprint", "iris"):
        log_patient_action(patient_id, "login", {"message": f"Invalid biometric type: {biometric_type}"}, "failed")
        return {
            "success": False,
            "token": None,
            "patient_id": patient_id,
            "message": "Invalid biometric type. Use 'fingerprint' or 'iris'.",
        }

    submitted_hash = hashlib.sha256(biometric_data.encode()).hexdigest()
    stored_hash = patient[f"{biometric_type}_hash"]

    if submitted_hash != stored_hash:
        log_patient_action(patient_id, "login", {"message": f"Biometric mismatch ({biometric_type})"}, "failed")
        return {
            "success": False,
            "token": None,
            "patient_id": patient_id,
            "message": "Biometric verification failed",
        }

    # 3. Verify OTP
    if otp != Config.SIMULATED_OTP:
        log_patient_action(patient_id, "login", {"message": "Invalid OTP"}, "failed")
        return {
            "success": False,
            "token": None,
            "patient_id": patient_id,
            "message": "Invalid OTP",
        }

    # 4. Generate token
    token = generate_token(
        payload={
            "sub": patient_id,
            "role": "patient",
            "name": patient["name"],
            "abha_id": patient["abha_id"],
        },
        expiry_seconds=Config.PATIENT_TOKEN_EXPIRY,
    )

    log_patient_action(patient_id, "login", {"message": "Authenticated successfully"}, "success")

    return {
        "success": True,
        "token": token,
        "patient_id": patient_id,
        "name": patient["name"],
        "message": "Authentication successful",
    }


# ---------------------------------------------------------------------------
# Doctor authentication
# ---------------------------------------------------------------------------

def authenticate_doctor(email: str, password: str) -> dict:
    """
    Verify doctor email + password and return a JWT.

    Args:
        email:    Doctor's email
        password: Plaintext password

    Returns:
        dict with 'success', 'token', 'doctor_id', 'message'
    """
    if email not in DOCTOR_CREDENTIAL_STORE:
        log_doctor_action(email, "login", status="failed", details={"message": "Unknown email"})
        return {
            "success": False,
            "token": None,
            "doctor_id": None,
            "message": "Invalid credentials",
        }

    doctor = DOCTOR_CREDENTIAL_STORE[email]

    # Verify password
    if not bcrypt.checkpw(password.encode(), doctor["password_hash"].encode()):
        log_doctor_action(email, "login", status="failed", details={"message": "Password mismatch"})
        return {
            "success": False,
            "token": None,
            "doctor_id": None,
            "message": "Invalid credentials",
        }

    # Generate token
    token = generate_token(
        payload={
            "sub": doctor["doctor_id"],
            "role": "doctor",
            "email": email,
            "name": doctor["name"],
            "hospital": doctor["hospital"],
        },
        expiry_seconds=Config.DOCTOR_TOKEN_EXPIRY,
    )

    log_doctor_action(doctor["doctor_id"], "login", status="success", details={"message": "Authenticated successfully"})

    return {
        "success": True,
        "token": token,
        "doctor_id": doctor["doctor_id"],
        "message": "Authentication successful",
    }


# ---------------------------------------------------------------------------
# Session token (doctor requesting patient data — 30 min)
# ---------------------------------------------------------------------------

def generate_session_token(doctor_id: str, patient_id: str) -> dict:
    """
    Generate a short-lived session token for a doctor to view patient data.
    This simulates the patient granting a 30-minute access window.

    Returns:
        dict with 'session_token', 'expires_in', 'message'
    """
    if patient_id not in PATIENT_BIOMETRIC_STORE:
        return {
            "success": False,
            "session_token": None,
            "message": "Patient not found",
        }

    token = generate_token(
        payload={
            "sub": doctor_id,
            "role": "session",
            "patient_id": patient_id,
            "type": "patient_data_access",
        },
        expiry_seconds=Config.SESSION_TOKEN_EXPIRY,
    )

    _log_audit(
        "SESSION_GRANT", doctor_id,
        f"30-min session granted for patient {patient_id}", True
    )

    return {
        "success": True,
        "session_token": token,
        "patient_id": patient_id,
        "expires_in": Config.SESSION_TOKEN_EXPIRY,
        "message": f"Session granted for {Config.SESSION_TOKEN_EXPIRY // 60} minutes",
    }


# ---------------------------------------------------------------------------
# JWT middleware decorator
# ---------------------------------------------------------------------------

def token_required(allowed_roles=None):
    """
    Flask route decorator that enforces JWT authentication.

    Usage:
        @app.route("/protected")
        @token_required(allowed_roles=["doctor", "patient"])
        def protected_route():
            user = g.current_user  # decoded token payload
            ...

    Returns 401 if token is missing, expired, or role is unauthorized.
    """
    if allowed_roles is None:
        allowed_roles = ["patient", "doctor", "session"]

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extract token from header
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({
                    "success": False,
                    "message": "Missing or malformed Authorization header. "
                               "Expected: Bearer <token>",
                }), 401

            token = auth_header.split(" ", 1)[1]

            try:
                payload = decode_token(token)
            except jwt.ExpiredSignatureError:
                return jsonify({
                    "success": False,
                    "message": "Token expired. Please re-authenticate.",
                }), 401
            except jwt.InvalidTokenError as e:
                return jsonify({
                    "success": False,
                    "message": f"Invalid token: {e}",
                }), 401

            # Check role
            role = payload.get("role", "")
            if role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": f"Access denied. Role '{role}' is not authorized.",
                }), 403

            # Store decoded user info for the route handler
            g.current_user = payload
            return f(*args, **kwargs)

        return wrapper
    return decorator
