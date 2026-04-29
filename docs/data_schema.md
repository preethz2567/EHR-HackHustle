# Patient Data Schema — Contract Document

> **Version:** 1.0  
> **Owner:** Person A (Lead + Data Systems)  
> **Last Updated:** 2026-04-29  
> **Status:** Active — All team members must conform to this schema.

---

## Overview

This document defines the canonical patient data structure used across the entire PS-1 system.
All synthetic data (Person D), orchestration agents (Person B), and frontend rendering (Person C)
**must** conform to this schema exactly.

---

## Top-Level Patient Object

| Field                | Type     | Required | Description                                      |
|----------------------|----------|----------|--------------------------------------------------|
| `patient_id`         | `string` | ✅ Yes   | Unique identifier (e.g., `"P001"`)               |
| `age`                | `int`    | ✅ Yes   | Patient age in years                              |
| `gender`             | `string` | ✅ Yes   | `"Male"`, `"Female"`, or `"Other"`                |
| `diagnoses`          | `list`   | ✅ Yes   | List of Diagnosis objects (see below)             |
| `medications`        | `list`   | ✅ Yes   | List of Medication objects (see below)            |
| `labs`               | `list`   | ✅ Yes   | List of Lab Result objects (see below)            |
| `episodes`           | `list`   | ✅ Yes   | List of Episode objects (see below)               |
| `allergies`          | `list`   | ✅ Yes   | List of Allergy objects (see below)               |
| `consent_preferences`| `dict`   | ✅ Yes   | Consent control object (see below)                |

---

## Diagnosis Object

Each item in the `diagnoses` list:

| Field                | Type     | Required | Description                                      |
|----------------------|----------|----------|--------------------------------------------------|
| `code`               | `string` | ✅ Yes   | ICD-10 code (3–7 chars, starts with letter, e.g., `"E11.9"`) |
| `name`               | `string` | ✅ Yes   | Human-readable diagnosis name                    |
| `date_of_diagnosis`  | `string` | ✅ Yes   | ISO date format `YYYY-MM-DD`                     |
| `status`             | `string` | ❌ No    | `"active"`, `"resolved"`, `"chronic"`            |

### ICD-10 Code Format Rules
- Length: 3 to 7 characters
- First character: uppercase letter (A–Z)
- Remaining: digits and optional decimal point
- Examples: `"E11.9"`, `"I10"`, `"J45.20"`

---

## Medication Object

Each item in the `medications` list:

| Field          | Type      | Required | Description                                      |
|----------------|-----------|----------|--------------------------------------------------|
| `name`         | `string`  | ✅ Yes   | Drug name (e.g., `"Metformin"`)                  |
| `dosage`       | `string`  | ✅ Yes   | Dosage string, non-empty (e.g., `"500mg twice daily"`) |
| `indication`   | `string`  | ✅ Yes   | Reason for prescription                          |
| `start_date`   | `string`  | ✅ Yes   | ISO date format `YYYY-MM-DD`                     |
| `is_active`    | `boolean` | ✅ Yes   | Whether the medication is currently active        |
| `end_date`     | `string`  | ❌ No    | ISO date format `YYYY-MM-DD` (if discontinued)   |

---

## Lab Result Object

Each item in the `labs` list:

| Field             | Type           | Required | Description                                      |
|-------------------|----------------|----------|--------------------------------------------------|
| `test_name`       | `string`       | ✅ Yes   | Name of the lab test (e.g., `"HbA1c"`)           |
| `value`           | `float`/`int`  | ✅ Yes   | Numeric result value                             |
| `unit`            | `string`       | ✅ Yes   | Measurement unit (e.g., `"%"`, `"mg/dL"`)        |
| `reference_range` | `string`       | ✅ Yes   | Reference range string (e.g., `"<5.7"`, `"80-120"`) |
| `date`            | `string`       | ✅ Yes   | ISO date format `YYYY-MM-DD`                     |
| `is_abnormal`     | `boolean`      | ❌ No    | Whether value is outside normal range            |

---

## Episode Object

Each item in the `episodes` list:

| Field          | Type     | Required | Description                                      |
|----------------|----------|----------|--------------------------------------------------|
| `episode_id`   | `string` | ✅ Yes   | Unique episode identifier                        |
| `hospital`     | `string` | ✅ Yes   | Source hospital name                             |
| `date`         | `string` | ✅ Yes   | ISO date format `YYYY-MM-DD`                     |
| `type`         | `string` | ✅ Yes   | `"inpatient"`, `"outpatient"`, `"emergency"`     |
| `summary`      | `string` | ❌ No    | Brief description of the episode                 |

---

## Allergy Object

Each item in the `allergies` list:

| Field          | Type     | Required | Description                                      |
|----------------|----------|----------|--------------------------------------------------|
| `allergen`     | `string` | ✅ Yes   | Name of allergen (e.g., `"Penicillin"`)          |
| `reaction`     | `string` | ✅ Yes   | Reaction description (e.g., `"Anaphylaxis"`)     |
| `severity`     | `string` | ✅ Yes   | `"mild"`, `"moderate"`, `"severe"`               |

---

## Consent Preferences Object

The `consent_preferences` field is a dictionary:

| Field                  | Type      | Required | Description                                      |
|------------------------|-----------|----------|--------------------------------------------------|
| `share_with_research`  | `boolean` | ✅ Yes   | Patient consents to research data sharing         |
| `share_across_hospitals`| `boolean`| ✅ Yes   | Patient consents to cross-hospital data sharing   |
| `share_mental_health`  | `boolean` | ✅ Yes   | Patient consents to mental health data sharing    |
| `share_substance_abuse`| `boolean` | ✅ Yes   | Patient consents to substance abuse data sharing  |
| `last_updated`         | `string`  | ✅ Yes   | ISO date format `YYYY-MM-DD`                     |

---

## Example Patient Object

```json
{
  "patient_id": "P001",
  "age": 45,
  "gender": "Male",
  "diagnoses": [
    {
      "code": "E11.9",
      "name": "Type 2 Diabetes Mellitus",
      "date_of_diagnosis": "2023-03-15",
      "status": "active"
    }
  ],
  "medications": [
    {
      "name": "Metformin",
      "dosage": "500mg twice daily",
      "indication": "Type 2 Diabetes",
      "start_date": "2023-03-20",
      "is_active": true
    }
  ],
  "labs": [
    {
      "test_name": "HbA1c",
      "value": 7.2,
      "unit": "%",
      "reference_range": "<5.7",
      "date": "2024-01-10",
      "is_abnormal": true
    }
  ],
  "episodes": [
    {
      "episode_id": "EP001",
      "hospital": "City General Hospital",
      "date": "2023-03-15",
      "type": "outpatient",
      "summary": "Initial diabetes diagnosis and treatment plan"
    }
  ],
  "allergies": [
    {
      "allergen": "Penicillin",
      "reaction": "Rash",
      "severity": "moderate"
    }
  ],
  "consent_preferences": {
    "share_with_research": true,
    "share_across_hospitals": true,
    "share_mental_health": false,
    "share_substance_abuse": false,
    "last_updated": "2024-01-15"
  }
}
```

---

## Validation Rules Summary

| Rule                         | Details                                          |
|------------------------------|--------------------------------------------------|
| ICD-10 codes                 | 3–7 chars, starts with letter, alphanumeric + `.` |
| All dates                    | `YYYY-MM-DD` format, must be parseable           |
| `value` in labs              | Must be numeric (`int` or `float`)               |
| `is_active` in medications   | Must be `boolean`                                |
| `dosage` in medications      | Must be non-empty string                         |
| `consent_preferences`        | Must be a `dict` with all 5 required keys        |
| Lists can be empty           | `[]` is acceptable for optional conditions       |

---

## Change Log

| Date       | Version | Author   | Changes               |
|------------|---------|----------|-----------------------|
| 2026-04-29 | 1.0     | Person A | Initial schema release |
