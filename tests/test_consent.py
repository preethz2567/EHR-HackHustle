"""
test_consent.py
Tests for consent_gateway.py, privacy_model.py, and audit_log.py
Run: python tests/test_consent.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.privacy_model import ConsentPreferences, ConsentLevel, PATIENT_CONSENT_PROFILES
from core.consent_gateway import apply_consent, apply_consent_by_id
from core.audit_log import log_access, get_audit_log, get_audit_summary, clear_audit_log, get_stats

PASS = "[PASS]"
FAIL = "[FAIL]"


def make_sample_patient(patient_id="TEST001"):
    """Minimal patient dict for testing."""
    return {
        "patient_id":  patient_id,
        "name":        "Test Patient",
        "age":         55,
        "diagnoses":   [{"code": "I63.9", "name": "Stroke", "date_of_diagnosis": "2022-03-15"}],
        "medications": [{"name": "Aspirin", "dosage": "81mg", "indication": "Stroke prevention"}],
        "labs":        [{"test_name": "HbA1c", "value": "7.2%", "date": "2024-01-10",
                         "reference_range": "<7.0%", "research_flag": True}],
        "episodes":    [{"type": "hospitalization", "date": "2022-03-14", "reason": "Stroke",
                         "outcome": "Stable", "duration": 5}],
        "genomic":     [{"marker": "BRCA1", "status": "negative"}],
        "mental_health": [{"condition": "Anxiety", "date": "2023-06-01",
                           "therapy_notes": "CBT ongoing"}],
    }


# ── Test 1: FULL_ACCESS category is returned ──────────────────────────────────
def test_full_access_returned():
    clear_audit_log()
    patient = make_sample_patient("T001")
    prefs = ConsentPreferences(
        patient_id="T001",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.FULL_ACCESS,
            "mental_health": ConsentLevel.FULL_ACCESS,
        },
    )
    result = apply_consent(patient, prefs, "Risk")
    ok = result["diagnoses"] is not None and result["genomic"] is not None
    print(f"{PASS if ok else FAIL}  test_full_access_returned")
    return ok


# ── Test 2: REVOKED category returns None ─────────────────────────────────────
def test_revoked_blocked():
    clear_audit_log()
    patient = make_sample_patient("T002")
    prefs = ConsentPreferences(
        patient_id="T002",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        },
    )
    result = apply_consent(patient, prefs, "Risk")
    ok = result["genomic"] is None and result["mental_health"] is None
    print(f"{PASS if ok else FAIL}  test_revoked_blocked")
    return ok


# ── Test 3: CLINICAL_ONLY strips research fields from labs ────────────────────
def test_clinical_only_strips_research_flag():
    clear_audit_log()
    patient = make_sample_patient("T003")
    prefs = ConsentPreferences(
        patient_id="T003",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.CLINICAL_ONLY,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        },
    )
    result = apply_consent(patient, prefs, "Medication")
    labs = result.get("labs", [])
    ok = labs is not None and all("research_flag" not in lab for lab in labs)
    print(f"{PASS if ok else FAIL}  test_clinical_only_strips_research_flag")
    return ok


# ── Test 4: Audit log records correct allow/deny ──────────────────────────────
def test_audit_log_records_correctly():
    clear_audit_log()
    patient = make_sample_patient("T004")
    prefs = ConsentPreferences(
        patient_id="T004",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.REVOKED,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        },
    )
    apply_consent(patient, prefs, "Summary")
    log = get_audit_log("T004")

    allowed_entries = [e for e in log if "ALLOWED" in e["result"]]
    denied_entries  = [e for e in log if "DENIED"  in e["result"]]

    # diagnoses, labs, episodes → ALLOWED; medications, genomic, mental_health → DENIED
    ok = len(allowed_entries) == 3 and len(denied_entries) == 3
    print(f"{PASS if ok else FAIL}  test_audit_log_records_correctly  "
          f"(allowed={len(allowed_entries)}, denied={len(denied_entries)})")
    return ok


# ── Test 5: apply_consent_by_id uses pre-built profiles ──────────────────────
def test_apply_consent_by_id_p001():
    clear_audit_log()
    patient = make_sample_patient("P001")
    result = apply_consent_by_id(patient, "P001", "Risk")
    # P001 revokes genomic and mental_health
    ok = result["diagnoses"] is not None and result["genomic"] is None
    print(f"{PASS if ok else FAIL}  test_apply_consent_by_id_p001")
    return ok


# ── Test 6: Audit log is patient-scoped ───────────────────────────────────────
def test_audit_log_patient_scoped():
    clear_audit_log()

    p1 = make_sample_patient("SCOPE001")
    p2 = make_sample_patient("SCOPE002")
    prefs_full = ConsentPreferences("SCOPE001")
    prefs_full2 = ConsentPreferences("SCOPE002")

    apply_consent(p1, prefs_full,  "Risk")
    apply_consent(p2, prefs_full2, "Medication")

    log1 = get_audit_log("SCOPE001")
    log2 = get_audit_log("SCOPE002")

    ok = all(e["patient_id"] == "SCOPE001" for e in log1) and \
         all(e["patient_id"] == "SCOPE002" for e in log2)
    print(f"{PASS if ok else FAIL}  test_audit_log_patient_scoped")
    return ok


# ── Test 7: Audit summary is human-readable ───────────────────────────────────
def test_audit_summary():
    clear_audit_log()
    patient = make_sample_patient("SUM001")
    prefs = ConsentPreferences("SUM001")
    apply_consent(patient, prefs, "Risk")
    summary = get_audit_summary("SUM001")
    ok = "SUM001" in summary and "ALLOWED" in summary
    print(f"{PASS if ok else FAIL}  test_audit_summary")
    if ok:
        print(summary)
    return ok


# ── Run all tests ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  CONSENT GATEWAY & AUDIT LOG TEST SUITE")
    print("="*60 + "\n")

    results = [
        test_full_access_returned(),
        test_revoked_blocked(),
        test_clinical_only_strips_research_flag(),
        test_audit_log_records_correctly(),
        test_apply_consent_by_id_p001(),
        test_audit_log_patient_scoped(),
        test_audit_summary(),
    ]

    print("\n" + "="*60)
    passed = sum(results)
    total  = len(results)
    print(f"  Results: {passed}/{total} tests passed")
    if passed == total:
        print("  [PASS] All tests passed! Consent gateway ready for Person B.")
    else:
        print("  [FAIL]  Some tests failed. Check output above.")
    print("="*60 + "\n")
    sys.exit(0 if passed == total else 1)
