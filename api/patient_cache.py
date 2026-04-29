"""
patient_cache.py — In-Memory Patient Data Cache & Manual Records
=================================================================
Stores unified patient data fetched from federated providers,
manual document uploads, and access token mappings.

All data is stored in-memory (dict). No database.
"""

import secrets
from datetime import datetime, timezone, timedelta
from typing import Any


# ---------------------------------------------------------------------------
# In-memory stores
# ---------------------------------------------------------------------------

# patient_id -> {unified_data, timestamp, manual_records}
PATIENT_CACHE: dict[str, dict[str, Any]] = {}

# access_token -> {patient_id, doctor_id, expires_at, created_at}
ACCESS_TOKEN_STORE: dict[str, dict[str, Any]] = {}

# patient_id -> [{event_type, actor_id, actor_role, timestamp, details}]
PATIENT_AUDIT_LOG: dict[str, list[dict[str, Any]]] = {}


# ---------------------------------------------------------------------------
# Audit helpers
# ---------------------------------------------------------------------------

def _log_patient_audit(patient_id: str, event_type: str, actor_id: str,
                       actor_role: str, details: str):
    """Append an audit entry for a specific patient."""
    if patient_id not in PATIENT_AUDIT_LOG:
        PATIENT_AUDIT_LOG[patient_id] = []

    entry = {
        "event_type": event_type,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }
    PATIENT_AUDIT_LOG[patient_id].append(entry)
    return entry


# ---------------------------------------------------------------------------
# Cache operations
# ---------------------------------------------------------------------------

def cache_patient_data(patient_id: str, unified_data: dict) -> dict:
    """
    Store federated query results in the patient cache.

    Returns summary dict with record counts.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Preserve any existing manual records
    existing_manual = []
    if patient_id in PATIENT_CACHE:
        existing_manual = PATIENT_CACHE[patient_id].get("manual_records", [])

    PATIENT_CACHE[patient_id] = {
        "unified_data": unified_data,
        "cached_at": now,
        "last_refreshed": now,
        "manual_records": existing_manual,
    }

    # Count records
    counts = {
        "diagnoses": len(unified_data.get("diagnoses", [])),
        "medications": len(unified_data.get("medications", [])),
        "labs": len(unified_data.get("labs", [])),
        "episodes": len(unified_data.get("episodes", [])),
        "allergies": len(unified_data.get("allergies", [])),
        "manual_records": len(existing_manual),
    }
    total = sum(counts.values())

    return {
        "records_count": total,
        "breakdown": counts,
        "cached_at": now,
    }


def get_cached_data(patient_id: str) -> dict | None:
    """
    Retrieve cached patient data. Returns None if not cached.
    """
    if patient_id not in PATIENT_CACHE:
        return None
    return PATIENT_CACHE[patient_id]


def is_cached(patient_id: str) -> bool:
    """Check if patient data is in the cache."""
    return patient_id in PATIENT_CACHE


# ---------------------------------------------------------------------------
# Manual record uploads
# ---------------------------------------------------------------------------

def add_manual_record(patient_id: str, document_type: str,
                      filename: str, file_size: int,
                      content_type: str, parsed_data: dict = None) -> dict:
    """
    Store metadata for a manually uploaded document (vaccine card, lab report, etc.).

    In a real system this would save the file to object storage.
    Here we store metadata only.
    """
    if patient_id not in PATIENT_CACHE:
        PATIENT_CACHE[patient_id] = {
            "unified_data": {},
            "cached_at": None,
            "last_refreshed": None,
            "manual_records": [],
        }

    record_id = f"MR-{patient_id}-{len(PATIENT_CACHE[patient_id]['manual_records']) + 1:03d}"
    now = datetime.now(timezone.utc).isoformat()

    record = {
        "record_id": record_id,
        "document_type": document_type,
        "filename": filename,
        "file_size_bytes": file_size,
        "content_type": content_type,
        "uploaded_at": now,
        "status": "uploaded",
        "parsed_data": parsed_data
    }

    PATIENT_CACHE[patient_id]["manual_records"].append(record)
    
    # Merge structured data into unified_data
    if parsed_data:
        unified_data = PATIENT_CACHE[patient_id]["unified_data"]
        
        if document_type == "vaccine_card":
            if "diagnoses" not in unified_data:
                unified_data["diagnoses"] = []
            
            for v in parsed_data.get("vaccines", []):
                # Add as preventive care/diagnosis 
                unified_data["diagnoses"].append({
                    "name": f"Vaccine Administered: {v}",
                    "code": "Z23", # standard ICD-10 for encounter for immunization
                    "date_of_diagnosis": parsed_data.get("date", now[:10])
                })
                
        elif document_type == "lab_report":
            if "labs" not in unified_data:
                unified_data["labs"] = []
                
            for lab in parsed_data.get("labs", []):
                unified_data["labs"].append({
                    "test_name": lab.get("test_name", "Unknown Test"),
                    "value": lab.get("value", "N/A"),
                    "reference_range": lab.get("reference_range", "N/A"),
                    "date": parsed_data.get("date", now[:10])
                })

    return record


# ---------------------------------------------------------------------------
# Access token management
# ---------------------------------------------------------------------------

def create_access_token(patient_id: str, doctor_email: str,
                        duration_minutes: int = 30) -> dict:
    """
    Generate a short-lived access token for a doctor to view patient data.

    Returns:
        dict with access_token, expires_in_minutes, expires_at
    """
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=duration_minutes)

    # Simple lookup logic for doctor_id from email (simulated DB lookup)
    doctor_id = f"DR-{doctor_email.split('@')[0].replace('dr.', '').upper()}"

    ACCESS_TOKEN_STORE[token] = {
        "patient_id": patient_id,
        "doctor_email": doctor_email,
        "doctor_id": doctor_id,
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "duration_minutes": duration_minutes,
        "status": "active",
        "revoked": False,
    }

    _log_patient_audit(
        patient_id, "ACCESS_TOKEN_GRANTED", patient_id, "patient",
        f"Access granted to {doctor_email} for {duration_minutes} minutes"
    )

    return {
        "access_token": token,
        "expires_in_minutes": duration_minutes,
        "expires_at": expires_at.isoformat(),
        "doctor_id": doctor_id,
    }


def validate_access_token(token: str) -> dict | None:
    """
    Validate an access token. Returns the token data if valid, None if expired/invalid.
    """
    if token not in ACCESS_TOKEN_STORE:
        return None

    token_data = ACCESS_TOKEN_STORE[token]

    if token_data.get("revoked") or token_data.get("status") == "revoked":
        return None

    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return None

    return token_data

def get_active_authorizations(patient_id: str) -> list[dict]:
    """Return all non-expired, non-revoked active tokens for a patient."""
    active = []
    now = datetime.now(timezone.utc)
    for token, data in ACCESS_TOKEN_STORE.items():
        if data["patient_id"] == patient_id and not data.get("revoked") and data.get("status") != "revoked":
            expires_at = datetime.fromisoformat(data["expires_at"])
            if expires_at > now:
                # Include token in response for patient reference
                # Note: Returning raw token string to patient so they can copy it or revoke it.
                auth_data = data.copy()
                auth_data["access_token"] = token
                active.append(auth_data)
    return active

def revoke_token(patient_id: str, token: str) -> bool:
    """Revoke an active access token."""
    if token in ACCESS_TOKEN_STORE and ACCESS_TOKEN_STORE[token]["patient_id"] == patient_id:
        ACCESS_TOKEN_STORE[token]["revoked"] = True
        ACCESS_TOKEN_STORE[token]["status"] = "revoked"
        
        _log_patient_audit(
            patient_id, "ACCESS_TOKEN_REVOKED", patient_id, "patient",
            f"Patient revoked access token manually"
        )
        return True
    return False


# ---------------------------------------------------------------------------
# Patient audit log
# ---------------------------------------------------------------------------

def get_patient_audit_log(patient_id: str) -> list[dict]:
    """Return all audit entries for a patient, most recent first."""
    entries = PATIENT_AUDIT_LOG.get(patient_id, [])
    return list(reversed(entries))
