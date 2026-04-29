"""
consent_gateway.py
Enforces patient consent preferences on every data access request.
Every access (allowed or denied) is recorded in the audit log.
"""

from typing import Any, Dict, Optional
from core.privacy_model import ConsentPreferences, ConsentLevel, PATIENT_CONSENT_PROFILES
from core.audit_log import log_access


# ── Main gateway function ──────────────────────────────────────────────────────

def apply_consent(
    patient_data: Dict[str, Any],
    consent_preferences: ConsentPreferences,
    requester_agent: str,
) -> Dict[str, Any]:
    """
    Filter patient_data according to the patient's consent preferences.

    Args:
        patient_data:         Full merged patient dict from federated_query().
        consent_preferences:  ConsentPreferences object for this patient.
        requester_agent:      Name of the agent making the request (e.g. "Risk", "Medication").

    Returns:
        A copy of patient_data with denied categories set to None,
        and a populated 'audit_trail' key listing every access decision.
    """
    patient_id = patient_data.get("patient_id", "UNKNOWN")

    # Categories we actively gate — non-category top-level fields pass through freely
    GATED_CATEGORIES = {
        "diagnoses",
        "medications",
        "labs",
        "episodes",
        "genomic",
        "mental_health",
    }

    filtered: Dict[str, Any] = {}
    audit_entries = []

    for key, value in patient_data.items():
        if key not in GATED_CATEGORIES:
            # Pass-through: demographic/metadata fields
            filtered[key] = value
            continue

        level = consent_preferences.get(key)

        if level == ConsentLevel.REVOKED:
            filtered[key] = None
            result = "DENIED"
        elif level == ConsentLevel.CLINICAL_ONLY:
            # Return data but strip any research/identifiable sub-fields if present
            filtered[key] = _apply_clinical_only_filter(key, value)
            result = "ALLOWED (CLINICAL_ONLY)"
        else:  # FULL_ACCESS
            filtered[key] = value
            result = "ALLOWED"

        entry = log_access(
            agent_name=requester_agent,
            patient_id=patient_id,
            category=key,
            result=result,
        )
        audit_entries.append(entry)

    filtered["audit_trail"] = audit_entries
    return filtered


def apply_consent_by_id(
    patient_data: Dict[str, Any],
    patient_id: str,
    requester_agent: str,
) -> Dict[str, Any]:
    """
    Convenience wrapper: looks up the consent profile automatically by patient_id.
    Raises KeyError if patient_id is not in PATIENT_CONSENT_PROFILES.
    """
    if patient_id not in PATIENT_CONSENT_PROFILES:
        raise KeyError(
            f"No consent profile found for patient '{patient_id}'. "
            "Register consent preferences in privacy_model.py first."
        )
    prefs = PATIENT_CONSENT_PROFILES[patient_id]
    return apply_consent(patient_data, prefs, requester_agent)


# ── CLINICAL_ONLY filter helpers ───────────────────────────────────────────────

def _apply_clinical_only_filter(category: str, value: Any) -> Any:
    """
    Strip research-identifiable sub-fields for CLINICAL_ONLY access.
    For most categories this is a no-op; extend as needed.
    """
    if value is None:
        return None

    if category == "labs" and isinstance(value, list):
        # Remove any 'research_flag' or 'genomic_marker' sub-fields
        return [
            {k: v for k, v in lab.items() if k not in ("research_flag", "genomic_marker")}
            for lab in value
        ]

    if category == "mental_health" and isinstance(value, list):
        # Return only the condition name + date; strip therapy notes
        return [
            {k: v for k, v in entry.items() if k not in ("therapy_notes", "provider_notes")}
            for entry in value
        ]

    # Default: return as-is
    return value
