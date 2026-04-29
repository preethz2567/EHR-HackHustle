"""
audit_log.py
Append-only in-memory audit log for all data access events.
Tracks every allowed/denied consent decision for HIPAA compliance demonstration.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# ── In-memory store ────────────────────────────────────────────────────────────
# List of dicts; each entry is one access event.
_AUDIT_LOG: List[Dict[str, Any]] = []


# ── Core functions ─────────────────────────────────────────────────────────────

def log_access(
    agent_name: str,
    patient_id: str,
    category: str,
    result: str,
) -> Dict[str, Any]:
    """
    Record one data access event.

    Args:
        agent_name:  Name of the requesting agent (e.g. "Risk", "Medication").
        patient_id:  Patient identifier (e.g. "P001").
        category:    Data category requested (e.g. "diagnoses", "genomic").
        result:      Outcome string: "ALLOWED", "ALLOWED (CLINICAL_ONLY)", or "DENIED".

    Returns:
        The newly created audit entry dict.
    """
    entry: Dict[str, Any] = {
        "timestamp":  datetime.now(tz=timezone.utc).isoformat(),
        "agent_name": agent_name,
        "patient_id": patient_id,
        "category":   category,
        "result":     result,
    }
    _AUDIT_LOG.append(entry)
    return entry


def get_audit_log(patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve audit log entries.

    Args:
        patient_id: If provided, return only entries for this patient.
                    If None, return the full log.

    Returns:
        List of audit entries, newest first, each with keys:
        timestamp | agent_name | patient_id | category | result
    """
    if patient_id:
        entries = [e for e in _AUDIT_LOG if e["patient_id"] == patient_id]
    else:
        entries = list(_AUDIT_LOG)

    # Newest first
    return sorted(entries, key=lambda e: e["timestamp"], reverse=True)


def get_audit_summary(patient_id: str) -> str:
    """
    Human-readable summary of all access events for a patient.
    Useful for displaying in a UI or printing to console.
    """
    entries = get_audit_log(patient_id)
    if not entries:
        return f"No audit entries found for patient {patient_id}."

    lines = [f"Audit Log for Patient {patient_id} ({len(entries)} events):\n"]
    for e in entries:
        ts   = e["timestamp"]
        line = f"  [{ts}]  {e['agent_name']:20s}  {e['category']:15s}  →  {e['result']}"
        lines.append(line)
    return "\n".join(lines)


def clear_audit_log():
    """
    Clear the in-memory log. Use only in tests — never in production.
    """
    global _AUDIT_LOG
    _AUDIT_LOG = []


def get_stats(patient_id: Optional[str] = None) -> Dict[str, int]:
    """
    Quick stats: total accesses, allowed count, denied count.
    """
    entries = get_audit_log(patient_id)
    allowed = sum(1 for e in entries if "ALLOWED" in e["result"])
    denied  = sum(1 for e in entries if "DENIED"  in e["result"])
    return {"total": len(entries), "allowed": allowed, "denied": denied}
