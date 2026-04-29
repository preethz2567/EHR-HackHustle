# Data API Reference

> **For:** Person B (Backend/Orchestration)  
> **From:** Person A (Lead + Data Systems)  
> **Version:** 1.0 | **Updated:** 2026-04-29

---

## Overview

This document describes how to use Person A's data layer. All patient data
flows through these functions. **Do not bypass them** — they enforce schema
validation, consent checks, and audit logging.

---

## Module: `data.synthetic_ehr_generator`

> Built by Person D. Generates synthetic but realistic patient records.

### `generate_patient(patient_id: str) -> dict`

Generate a single patient record conforming to the canonical schema.

```python
from data.synthetic_ehr_generator import generate_patient

patient = generate_patient("P001")
# Returns a dict with: patient_id, age, gender, diagnoses, medications,
#                       labs, episodes, allergies, consent_preferences
```

**Returns:** A fully populated patient dictionary. See `/docs/data_schema.md` for field details.

---

## Module: `tests.test_data`

> Built by Person A. Validation utilities.

### `validate_patient(patient_dict: dict) -> tuple[bool, list[str]]`

Validates the top-level patient structure (all required fields, correct types, consent keys).

```python
from tests.test_data import validate_patient

is_valid, errors = validate_patient(patient)
if not is_valid:
    print("Errors:", errors)
```

### `validate_diagnoses(diagnoses_list: list) -> tuple[bool, list[str]]`

Validates ICD-10 codes, required fields, and date formats in the diagnoses list.

```python
from tests.test_data import validate_diagnoses

is_valid, errors = validate_diagnoses(patient["diagnoses"])
```

### `validate_medications(medications_list: list) -> tuple[bool, list[str]]`

Validates medication fields: name, dosage (non-empty), indication, start_date, is_active (bool).

```python
from tests.test_data import validate_medications

is_valid, errors = validate_medications(patient["medications"])
```

### `validate_labs(labs_list: list) -> tuple[bool, list[str]]`

Validates lab results: numeric values, valid dates, string reference ranges.

```python
from tests.test_data import validate_labs

is_valid, errors = validate_labs(patient["labs"])
```

---

## How to Use in Your API Endpoints

Person B: when you receive patient data (from Person D's generator or from
a request), **always validate before processing**:

```python
from data.synthetic_ehr_generator import generate_patient
from tests.test_data import validate_patient, validate_diagnoses, validate_medications, validate_labs


def get_patient_data(patient_id: str) -> dict:
    """Fetch and validate a patient record."""
    patient = generate_patient(patient_id)

    # Validate structure
    valid, errors = validate_patient(patient)
    if not valid:
        raise ValueError(f"Invalid patient data: {errors}")

    # Validate sub-structures
    _, diag_errors = validate_diagnoses(patient["diagnoses"])
    _, med_errors = validate_medications(patient["medications"])
    _, lab_errors = validate_labs(patient["labs"])

    all_errors = diag_errors + med_errors + lab_errors
    if all_errors:
        raise ValueError(f"Sub-validation errors: {all_errors}")

    return patient
```

---

## Consent-Gated Access Pattern

**IMPORTANT:** Before sharing patient data across hospitals or with research,
check consent preferences:

```python
def can_share_across_hospitals(patient: dict) -> bool:
    return patient["consent_preferences"].get("share_across_hospitals", False)

def can_share_with_research(patient: dict) -> bool:
    return patient["consent_preferences"].get("share_with_research", False)

def can_share_mental_health(patient: dict) -> bool:
    return patient["consent_preferences"].get("share_mental_health", False)

def can_share_substance_abuse(patient: dict) -> bool:
    return patient["consent_preferences"].get("share_substance_abuse", False)
```

Person B: your orchestration agents **must** call these before including
sensitive data in any cross-hospital synthesis.

---

## Patient IDs

| ID Range     | Source Hospital          |
|-------------|--------------------------|
| `P001–P050` | City General Hospital    |
| `P051–P100` | Metro Health Center      |
| `P101–P150` | Regional Medical Center  |

---

## Running Validation Tests

```bash
# Run full validation suite
python tests/test_data.py

# Run with pytest (verbose)
python -m pytest tests/test_data.py -v
```

Expected output:
```
============================================================
  PATIENT DATA VALIDATION SUITE
============================================================

--- Validating P001 ---
  Patient P001: ✅ VALID

--- Validating P002 ---
  Patient P002: ✅ VALID

...

============================================================
  SUMMARY
============================================================
  Passed: 5/5
  Failed: 0/5
============================================================
```

---

## Questions?

Ping Person A in the team chat. Schema changes go through `/docs/data_schema.md` first.
