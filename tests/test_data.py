"""
test_data.py — Data Validation Test Suite
==========================================
Person A: Lead + Data Systems

Validates that patient data structures conform to the canonical schema
defined in /docs/data_schema.md. Tests ICD-10 codes, date formats,
medication fields, lab values, and consent model.

Run:  python -m pytest tests/test_data.py -v
  or: python tests/test_data.py
"""

import os
import re
import sys
from datetime import datetime

# Ensure parent directory is on the path so 'data' package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Regex: ICD-10 code — starts with a letter, followed by 2-6 alphanumeric/dot chars
ICD10_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9.]{2,6}$")

# Regex: ISO date — YYYY-MM-DD
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_PATIENT_FIELDS = {
    "patient_id": str,
    "age": int,
    "diagnoses": list,
    "medications": list,
    "labs": list,
    "episodes": list,
    "allergies": list,
    "consent_preferences": dict,
}

REQUIRED_CONSENT_KEYS = [
    "share_with_research",
    "share_across_hospitals",
    "share_mental_health",
    "share_substance_abuse",
    "last_updated",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_valid_date(date_string: str) -> bool:
    """Return True if *date_string* is a valid YYYY-MM-DD date."""
    if not DATE_PATTERN.match(date_string):
        return False
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _is_valid_icd10(code: str) -> bool:
    """Return True if *code* matches ICD-10 format rules."""
    return bool(ICD10_PATTERN.match(code))


# ---------------------------------------------------------------------------
# Validation Functions
# ---------------------------------------------------------------------------

def validate_patient(patient_dict: dict) -> tuple[bool, list[str]]:
    """
    Validate top-level patient structure.

    Checks
    ------
    - All required fields exist
    - Each field has the correct type
    - consent_preferences contains all required keys

    Returns
    -------
    (is_valid, errors)  where *errors* is a list of human-readable messages.
    """
    errors: list[str] = []

    if not isinstance(patient_dict, dict):
        return False, ["Patient data is not a dictionary"]

    # --- Required fields & types ---
    for field, expected_type in REQUIRED_PATIENT_FIELDS.items():
        if field not in patient_dict:
            errors.append(f"Missing required field: '{field}'")
        elif not isinstance(patient_dict[field], expected_type):
            errors.append(
                f"Field '{field}' should be {expected_type.__name__}, "
                f"got {type(patient_dict[field]).__name__}"
            )

    # --- Consent preferences deep check ---
    consent = patient_dict.get("consent_preferences")
    if isinstance(consent, dict):
        for key in REQUIRED_CONSENT_KEYS:
            if key not in consent:
                errors.append(f"Missing consent key: '{key}'")
            elif key == "last_updated":
                if not isinstance(consent[key], str) or not _is_valid_date(consent[key]):
                    errors.append(f"consent_preferences.last_updated is not a valid date")
            else:
                if not isinstance(consent[key], bool):
                    errors.append(
                        f"consent_preferences.{key} should be bool, "
                        f"got {type(consent[key]).__name__}"
                    )

    return (len(errors) == 0, errors)


def validate_diagnoses(diagnoses_list: list) -> tuple[bool, list[str]]:
    """
    Validate every diagnosis in the list.

    Checks
    ------
    - Each diagnosis has code, name, date_of_diagnosis
    - code matches ICD-10 format (3-7 chars, starts with letter)
    - date_of_diagnosis is valid YYYY-MM-DD

    Returns
    -------
    (is_valid, errors)
    """
    errors: list[str] = []

    if not isinstance(diagnoses_list, list):
        return False, ["diagnoses is not a list"]

    for i, diag in enumerate(diagnoses_list):
        prefix = f"diagnoses[{i}]"

        if not isinstance(diag, dict):
            errors.append(f"{prefix}: not a dictionary")
            continue

        # Required fields
        for field in ("code", "name", "date_of_diagnosis"):
            if field not in diag:
                errors.append(f"{prefix}: missing '{field}'")

        # ICD-10 format
        code = diag.get("code", "")
        if code and not _is_valid_icd10(code):
            errors.append(
                f"{prefix}: code '{code}' does not match ICD-10 format "
                f"(3-7 chars, starts with letter)"
            )

        # Date format
        date_val = diag.get("date_of_diagnosis", "")
        if date_val and not _is_valid_date(date_val):
            errors.append(f"{prefix}: date_of_diagnosis '{date_val}' is not valid YYYY-MM-DD")

    return (len(errors) == 0, errors)


def validate_medications(medications_list: list) -> tuple[bool, list[str]]:
    """
    Validate every medication in the list.

    Checks
    ------
    - Each med has name, dosage, indication, start_date, is_active
    - dosage is a non-empty string
    - start_date is valid YYYY-MM-DD
    - is_active is boolean

    Returns
    -------
    (is_valid, errors)
    """
    errors: list[str] = []

    if not isinstance(medications_list, list):
        return False, ["medications is not a list"]

    for i, med in enumerate(medications_list):
        prefix = f"medications[{i}]"

        if not isinstance(med, dict):
            errors.append(f"{prefix}: not a dictionary")
            continue

        # Required fields
        for field in ("name", "dosage", "indication", "start_date", "is_active"):
            if field not in med:
                errors.append(f"{prefix}: missing '{field}'")

        # Dosage non-empty
        dosage = med.get("dosage")
        if isinstance(dosage, str) and len(dosage.strip()) == 0:
            errors.append(f"{prefix}: dosage is empty")
        elif dosage is not None and not isinstance(dosage, str):
            errors.append(f"{prefix}: dosage should be str, got {type(dosage).__name__}")

        # start_date format
        start_date = med.get("start_date", "")
        if start_date and not _is_valid_date(start_date):
            errors.append(f"{prefix}: start_date '{start_date}' is not valid YYYY-MM-DD")

        # is_active boolean
        is_active = med.get("is_active")
        if is_active is not None and not isinstance(is_active, bool):
            errors.append(f"{prefix}: is_active should be bool, got {type(is_active).__name__}")

    return (len(errors) == 0, errors)


def validate_labs(labs_list: list) -> tuple[bool, list[str]]:
    """
    Validate every lab result in the list.

    Checks
    ------
    - Each lab has test_name, value, unit, reference_range, date
    - value is numeric (int or float)
    - date is valid YYYY-MM-DD
    - reference_range is a string (e.g., "<5.7" or "80-120")

    Returns
    -------
    (is_valid, errors)
    """
    errors: list[str] = []

    if not isinstance(labs_list, list):
        return False, ["labs is not a list"]

    for i, lab in enumerate(labs_list):
        prefix = f"labs[{i}]"

        if not isinstance(lab, dict):
            errors.append(f"{prefix}: not a dictionary")
            continue

        # Required fields
        for field in ("test_name", "value", "unit", "reference_range", "date"):
            if field not in lab:
                errors.append(f"{prefix}: missing '{field}'")

        # value is numeric
        value = lab.get("value")
        if value is not None and not isinstance(value, (int, float)):
            errors.append(f"{prefix}: value should be numeric, got {type(value).__name__}")

        # date format
        date_val = lab.get("date", "")
        if date_val and not _is_valid_date(date_val):
            errors.append(f"{prefix}: date '{date_val}' is not valid YYYY-MM-DD")

        # reference_range is string
        ref = lab.get("reference_range")
        if ref is not None and not isinstance(ref, str):
            errors.append(
                f"{prefix}: reference_range should be str, got {type(ref).__name__}"
            )

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# Main Test — test_patient_generation()
# ---------------------------------------------------------------------------

def test_patient_generation():
    """
    Integration test: generate 5 patients using Person D's synthetic EHR
    generator and validate each one against the full schema.

    Imports Person D's function:
        from data.synthetic_ehr_generator import generate_patient

    Generates patients P001–P005 and runs all 4 validators.
    Prints per-patient results and asserts all pass.
    """
    # Import Person D's generator
    try:
        from data.synthetic_ehr_generator import generate_patient
    except ImportError:
        print("[!] WARNING: data.synthetic_ehr_generator not available yet.")
        print("    Person D needs to create /data/synthetic_ehr_generator.py")
        print("    with a generate_patient(patient_id: str) -> dict function.")
        print()
        print("    Running with built-in sample data instead...\n")
        generate_patient = _generate_sample_patient

    patient_ids = ["P001", "P002", "P003", "P004", "P005"]
    all_passed = True
    results_summary = []

    print("=" * 60)
    print("  PATIENT DATA VALIDATION SUITE")
    print("=" * 60)
    print()

    for pid in patient_ids:
        print(f"--- Validating {pid} ---")
        patient = generate_patient(pid)

        # Collect all errors across validators
        patient_errors: list[str] = []

        # 1. Top-level structure
        valid, errs = validate_patient(patient)
        patient_errors.extend(errs)

        # 2. Diagnoses
        if "diagnoses" in patient and isinstance(patient["diagnoses"], list):
            valid_d, errs_d = validate_diagnoses(patient["diagnoses"])
            patient_errors.extend(errs_d)

        # 3. Medications
        if "medications" in patient and isinstance(patient["medications"], list):
            valid_m, errs_m = validate_medications(patient["medications"])
            patient_errors.extend(errs_m)

        # 4. Labs
        if "labs" in patient and isinstance(patient["labs"], list):
            valid_l, errs_l = validate_labs(patient["labs"])
            patient_errors.extend(errs_l)

        # Report
        if not patient_errors:
            print(f"  Patient {pid}: [PASS] VALID")
            results_summary.append((pid, "VALID", []))
        else:
            print(f"  Patient {pid}: [FAIL] INVALID")
            for err in patient_errors:
                print(f"    - {err}")
            results_summary.append((pid, "INVALID", patient_errors))
            all_passed = False

        print()

    # Summary
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, status, _ in results_summary if status == "VALID")
    failed = len(results_summary) - passed
    print(f"  Passed: {passed}/{len(results_summary)}")
    print(f"  Failed: {failed}/{len(results_summary)}")
    print("=" * 60)

    # Assertion for pytest
    assert all_passed, (
        f"{failed} patient(s) failed validation: "
        + ", ".join(pid for pid, status, _ in results_summary if status == "INVALID")
    )

    return results_summary


# ---------------------------------------------------------------------------
# Built-in Sample Patient Generator (fallback until Person D delivers)
# ---------------------------------------------------------------------------

def _generate_sample_patient(patient_id: str) -> dict:
    """
    Generate a minimal but schema-compliant sample patient.
    Used as fallback when Person D's generator is not yet available.
    """
    import random

    age = random.randint(25, 80)
    gender = random.choice(["Male", "Female"])

    sample_diagnoses = [
        {"code": "E11.9", "name": "Type 2 Diabetes Mellitus",
         "date_of_diagnosis": "2023-03-15", "status": "active"},
        {"code": "I10", "name": "Essential Hypertension",
         "date_of_diagnosis": "2022-06-20", "status": "active"},
        {"code": "J45.20", "name": "Mild Intermittent Asthma",
         "date_of_diagnosis": "2021-11-05", "status": "resolved"},
        {"code": "E78.5", "name": "Hyperlipidemia",
         "date_of_diagnosis": "2023-01-10", "status": "active"},
        {"code": "K21.0", "name": "GERD with esophagitis",
         "date_of_diagnosis": "2024-02-28", "status": "active"},
    ]

    sample_medications = [
        {"name": "Metformin", "dosage": "500mg twice daily",
         "indication": "Type 2 Diabetes", "start_date": "2023-03-20",
         "is_active": True},
        {"name": "Lisinopril", "dosage": "10mg once daily",
         "indication": "Hypertension", "start_date": "2022-06-25",
         "is_active": True},
        {"name": "Atorvastatin", "dosage": "20mg at bedtime",
         "indication": "Hyperlipidemia", "start_date": "2023-01-15",
         "is_active": True},
        {"name": "Albuterol", "dosage": "2 puffs as needed",
         "indication": "Asthma", "start_date": "2021-11-10",
         "is_active": False},
        {"name": "Omeprazole", "dosage": "20mg before breakfast",
         "indication": "GERD", "start_date": "2024-03-01",
         "is_active": True},
    ]

    sample_labs = [
        {"test_name": "HbA1c", "value": round(random.uniform(5.0, 9.5), 1),
         "unit": "%", "reference_range": "<5.7", "date": "2024-01-10"},
        {"test_name": "Fasting Glucose", "value": round(random.uniform(70, 200), 0),
         "unit": "mg/dL", "reference_range": "70-100", "date": "2024-01-10"},
        {"test_name": "LDL Cholesterol", "value": round(random.uniform(60, 190), 0),
         "unit": "mg/dL", "reference_range": "<100", "date": "2024-01-10"},
        {"test_name": "Creatinine", "value": round(random.uniform(0.6, 1.8), 2),
         "unit": "mg/dL", "reference_range": "0.7-1.3", "date": "2024-01-10"},
        {"test_name": "Blood Pressure Systolic", "value": round(random.uniform(110, 160), 0),
         "unit": "mmHg", "reference_range": "<120", "date": "2024-01-10"},
    ]

    sample_episodes = [
        {"episode_id": f"EP-{patient_id}-001", "hospital": "City General Hospital",
         "date": "2023-03-15", "type": "outpatient",
         "summary": "Initial diabetes diagnosis and treatment plan"},
        {"episode_id": f"EP-{patient_id}-002", "hospital": "Metro Health Center",
         "date": "2024-01-10", "type": "outpatient",
         "summary": "Routine follow-up and lab work"},
    ]

    sample_allergies = [
        {"allergen": "Penicillin", "reaction": "Rash", "severity": "moderate"},
        {"allergen": "Sulfa Drugs", "reaction": "Hives", "severity": "mild"},
    ]

    # Pick a random subset for variety
    num_diag = random.randint(1, len(sample_diagnoses))
    num_meds = random.randint(1, len(sample_medications))
    num_labs = random.randint(2, len(sample_labs))

    return {
        "patient_id": patient_id,
        "age": age,
        "gender": gender,
        "diagnoses": random.sample(sample_diagnoses, num_diag),
        "medications": random.sample(sample_medications, num_meds),
        "labs": random.sample(sample_labs, num_labs),
        "episodes": sample_episodes,
        "allergies": sample_allergies,
        "consent_preferences": {
            "share_with_research": random.choice([True, False]),
            "share_across_hospitals": True,
            "share_mental_health": random.choice([True, False]),
            "share_substance_abuse": False,
            "last_updated": "2024-01-15",
        },
    }


# ---------------------------------------------------------------------------
# Run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        results = test_patient_generation()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
