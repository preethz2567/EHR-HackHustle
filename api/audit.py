"""
audit.py — Centralized Structured Audit Logging
==============================================
Maintains the unified global audit log and provides helper functions
for tracking patient and doctor actions securely.
"""

from datetime import datetime, timezone

# Central in-memory audit log store
GLOBAL_AUDIT_LOG = []

def log_patient_action(patient_id: str, action: str, details: dict, status: str = "success") -> dict:
    """
    Log an action initiated by a patient.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": patient_id,
        "user_type": "patient",
        "action": action,
        "patient_id": patient_id,
        "doctor_id": None,
        "details": details,
        "status": status
    }
    GLOBAL_AUDIT_LOG.append(entry)
    return entry

def log_doctor_action(doctor_id: str, action: str, patient_id: str = None, details: dict = None, status: str = "success") -> dict:
    """
    Log an action initiated by a doctor.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": doctor_id,
        "user_type": "doctor",
        "action": action,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "details": details or {},
        "status": status
    }
    GLOBAL_AUDIT_LOG.append(entry)
    return entry

def get_patient_audit_log(patient_id: str) -> list[dict]:
    """Return all audit entries involving this patient_id, newest first."""
    entries = [entry for entry in GLOBAL_AUDIT_LOG if entry.get("patient_id") == patient_id]
    # Sort newest first
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    return entries

def get_doctor_audit_log(doctor_id: str) -> list[dict]:
    """Return all audit entries involving this doctor_id, newest first."""
    entries = [entry for entry in GLOBAL_AUDIT_LOG if entry.get("doctor_id") == doctor_id]
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    return entries

def get_admin_audit_log(filters: dict = None) -> list[dict]:
    """Return all audit logs for the admin, optionally filtered."""
    entries = GLOBAL_AUDIT_LOG.copy()
    if filters:
        if "user_id" in filters:
            entries = [e for e in entries if e.get("user_id") == filters["user_id"]]
        if "action" in filters:
            entries = [e for e in entries if e.get("action") == filters["action"]]
    
    entries.sort(key=lambda x: x["timestamp"], reverse=True)
    return entries
