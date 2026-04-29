from data.synthetic_ehr_generator import generate_patient
from typing import Dict, Any

# Hospital data fragments with disparate formats
HOSPITAL_DATA = {
    "A": {
        # Hospital A: Neurology specialists (Simulates FHIR format)
        "P001": {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Condition",
                        "code": {"coding": [{"code": "I63.9", "display": "Ischemic stroke, unspecified"}]},
                        "onsetDateTime": "2022-03-15"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Condition",
                        "code": {"coding": [{"code": "E11.9", "display": "Type 2 diabetes mellitus without complications"}]},
                        "onsetDateTime": "2010-05-12"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "class": "hospitalization",
                        "period": {"start": "2022-03-15"},
                        "reasonCode": [{"text": "Acute ischemic stroke"}],
                        "hospitalization": {"dischargeDisposition": {"text": "discharged to home"}},
                        "length": {"value": 5}
                    }
                }
            ]
        },
        "P002": {"resourceType": "Bundle", "entry": []},
        "P003": {
            "resourceType": "Bundle",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Condition",
                        "code": {"coding": [{"code": "I21.9", "display": "Myocardial infarction"}]},
                        "onsetDateTime": "2020-06-10"
                    }
                },
                {
                    "resource": {
                        "resourceType": "Encounter",
                        "class": "hospitalization",
                        "period": {"start": "2020-06-10"},
                        "reasonCode": [{"text": "Acute MI"}],
                        "hospitalization": {"dischargeDisposition": {"text": "discharged to home"}},
                        "length": {"value": 4}
                    }
                }
            ]
        },
        "P004": {"resourceType": "Bundle", "entry": []},
        "P005": {"resourceType": "Bundle", "entry": []}
    },
    "B": {
        # Hospital B: Cardiology specialists (Simulates Legacy EHR format)
        "P001": {
            "DX_LIST": [
                {"ICD10": "I10", "DESC": "Essential hypertension", "DX_DATE": "2005-06-20"}
            ],
            "PROCEDURES": []
        },
        "P002": {
            "DX_LIST": [
                {"ICD10": "I10", "DESC": "Essential hypertension", "DX_DATE": "2015-01-15"}
            ],
            "PROCEDURES": []
        },
        "P003": {
            "DX_LIST": [
                {"ICD10": "I10", "DESC": "Essential hypertension", "DX_DATE": "2008-03-20"}
            ],
            "PROCEDURES": [
                {
                    "TYPE": "procedure",
                    "DATE": "2020-06-15",
                    "REASON": "Cardiac intervention",
                    "OUTCOME": "stent placed",
                    "DAYS": 1
                }
            ]
        },
        "P004": {"DX_LIST": [], "PROCEDURES": []},
        "P005": {"DX_LIST": [], "PROCEDURES": []}
    },
    "C": {
        # Hospital C (Clinic): Primary care (Simulates Custom API format)
        "P001": {
            "meds": [
                {"med_name": "Aspirin", "dose": "100mg daily", "reason": "Post-stroke prevention", "started": "2022-03-16"},
                {"med_name": "Clopidogrel", "dose": "75mg daily", "reason": "Post-stroke prevention", "started": "2022-03-16"},
                {"med_name": "Metformin", "dose": "500mg BID", "reason": "Type 2 diabetes", "started": "2010-05-12"},
                {"med_name": "Lisinopril", "dose": "10mg daily", "reason": "Hypertension", "started": "2005-06-20"}
            ],
            "lab_results": [
                {"name": "HbA1c", "val": 6.8, "date": "2023-07-15", "ref": "< 5.7 (normal)"},
                {"name": "HbA1c", "val": 6.9, "date": "2023-09-10", "ref": "< 5.7 (normal)"},
                {"name": "HbA1c", "val": 7.0, "date": "2023-11-12", "ref": "< 5.7 (normal)"},
                {"name": "HbA1c", "val": 7.2, "date": "2024-01-10", "ref": "< 5.7 (normal)"},
                {"name": "HbA1c", "val": 7.5, "date": "2024-03-08", "ref": "< 5.7 (normal)"},
                {"name": "BP Systolic", "val": 128, "date": "2023-07-15", "ref": "< 130 (normal)"},
                {"name": "BP Systolic", "val": 132, "date": "2023-09-10", "ref": "< 130 (normal)"},
                {"name": "BP Systolic", "val": 138, "date": "2023-11-12", "ref": "< 130 (normal)"},
                {"name": "BP Systolic", "val": 142, "date": "2024-01-10", "ref": "< 130 (normal)"},
                {"name": "BP Systolic", "val": 148, "date": "2024-03-08", "ref": "< 130 (normal)"},
                {"name": "eGFR", "val": 72, "date": "2023-07-15", "ref": "> 60 (normal)"},
                {"name": "eGFR", "val": 68, "date": "2023-09-10", "ref": "> 60 (normal)"},
                {"name": "eGFR", "val": 64, "date": "2023-11-12", "ref": "> 60 (normal)"},
                {"name": "eGFR", "val": 58, "date": "2024-01-10", "ref": "> 60 (normal)"},
                {"name": "eGFR", "val": 52, "date": "2024-03-08", "ref": "> 60 (normal)"}
            ]
        },
        "P002": {
            "meds": [
                {"med_name": "Albuterol", "dose": "2 puffs as needed", "reason": "Asthma", "started": "2015-01-15"},
                {"med_name": "Lisinopril", "dose": "10mg daily", "reason": "Hypertension", "started": "2015-01-15"}
            ],
            "lab_results": [
                {"name": "BP Systolic", "val": 135, "date": "2024-01-12", "ref": "< 130 (normal)"}
            ]
        },
        "P003": {
            "meds": [
                {"med_name": "Atorvastatin", "dose": "20mg daily", "reason": "Cholesterol", "started": "2020-06-20"},
                {"med_name": "Metoprolol", "dose": "50mg BID", "reason": "Heart disease", "started": "2020-06-20"}
            ],
            "lab_results": [
                {"name": "Troponin", "val": 0.02, "date": "2024-01-08", "ref": "< 0.04 (normal)"}
            ]
        },
        "P004": {
            "meds": [
                {"med_name": "Albuterol", "dose": "2 puffs as needed", "reason": "COPD", "started": "2018-06-10"}
            ],
            "lab_results": []
        },
        "P005": {
            "meds": [
                {"med_name": "Insulin Glargine", "dose": "20 units daily", "reason": "Type 1 diabetes", "started": "2015-01-01"}
            ],
            "lab_results": [
                {"name": "HbA1c", "val": 6.8, "date": "2024-01-05", "ref": "< 5.7 (normal)"}
            ]
        }
    }
}

def query_hospital(hospital_id: str, patient_id: str) -> Dict[str, Any]:
    """
    Query a specific hospital for their fragment of patient data.
    The returned fragment is in the hospital's native format.
    """
    if hospital_id not in HOSPITAL_DATA:
        raise ValueError(f"Unknown hospital: {hospital_id}")
    
    if patient_id not in HOSPITAL_DATA[hospital_id]:
        raise ValueError(f"Unknown patient: {patient_id}")
    
    return HOSPITAL_DATA[hospital_id][patient_id]

# --- Normalization Adapters ---

def normalize_hospital_a(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize FHIR-like format to Canonical Format"""
    normalized = {"diagnoses": [], "episodes": []}
    for entry in raw_data.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") == "Condition":
            coding = resource.get("code", {}).get("coding", [{}])[0]
            normalized["diagnoses"].append({
                "code": coding.get("code", "UNKNOWN"),
                "name": coding.get("display", "Unknown"),
                "date_of_diagnosis": resource.get("onsetDateTime", "")
            })
        elif resource.get("resourceType") == "Encounter":
            reason = resource.get("reasonCode", [{}])[0].get("text", "Unknown")
            outcome = resource.get("hospitalization", {}).get("dischargeDisposition", {}).get("text", "Unknown")
            normalized["episodes"].append({
                "type": resource.get("class", "unknown"),
                "date": resource.get("period", {}).get("start", ""),
                "reason": reason,
                "outcome": outcome,
                "duration_days": resource.get("length", {}).get("value", 0)
            })
    return normalized

def normalize_hospital_b(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Legacy EHR format to Canonical Format"""
    normalized = {"diagnoses": [], "episodes": []}
    for dx in raw_data.get("DX_LIST", []):
        normalized["diagnoses"].append({
            "code": dx.get("ICD10", "UNKNOWN"),
            "name": dx.get("DESC", "Unknown"),
            "date_of_diagnosis": dx.get("DX_DATE", "")
        })
    for proc in raw_data.get("PROCEDURES", []):
        normalized["episodes"].append({
            "type": proc.get("TYPE", "unknown"),
            "date": proc.get("DATE", ""),
            "reason": proc.get("REASON", "Unknown"),
            "outcome": proc.get("OUTCOME", "Unknown"),
            "duration_days": proc.get("DAYS", 0)
        })
    return normalized

def normalize_hospital_c(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Custom API format to Canonical Format"""
    normalized = {"medications": [], "labs": []}
    for med in raw_data.get("meds", []):
        normalized["medications"].append({
            "name": med.get("med_name", "Unknown"),
            "dosage": med.get("dose", "Unknown"),
            "indication": med.get("reason", "Unknown"),
            "start_date": med.get("started", "")
        })
    for lab in raw_data.get("lab_results", []):
        normalized["labs"].append({
            "test_name": lab.get("name", "Unknown"),
            "value": lab.get("val", 0),
            "date": lab.get("date", ""),
            "reference_range": lab.get("ref", "Unknown")
        })
    return normalized

# --- Core Federated Query Engine ---

def federated_query(patient_id: str) -> Dict[str, Any]:
    """
    Query all 3 hospitals, normalize their disparate data formats, 
    and merge into a canonical patient record.
    """
    # 1. Fetch raw fragments
    raw_a = query_hospital("A", patient_id)
    raw_b = query_hospital("B", patient_id)
    raw_c = query_hospital("C", patient_id)
    
    # 2. Normalize fragments (Data Harmonization)
    norm_a = normalize_hospital_a(raw_a)
    norm_b = normalize_hospital_b(raw_b)
    norm_c = normalize_hospital_c(raw_c)
    
    # 3. Initialize merged canonical patient object
    merged_patient = {
        "patient_id": patient_id,
        "diagnoses": [],
        "medications": [],
        "labs": [],
        "episodes": [],
        "allergies": []  # Not stored in federated system
    }
    
    # 4. Merge normalized data
    merged_patient["diagnoses"].extend(norm_a.get("diagnoses", []))
    merged_patient["diagnoses"].extend(norm_b.get("diagnoses", []))
    
    merged_patient["medications"] = norm_c.get("medications", [])
    merged_patient["labs"] = norm_c.get("labs", [])
    
    merged_patient["episodes"].extend(norm_a.get("episodes", []))
    merged_patient["episodes"].extend(norm_b.get("episodes", []))
    
    # 5. Remove duplicates from diagnoses (by code)
    seen_codes = set()
    unique_diagnoses = []
    for diag in merged_patient["diagnoses"]:
        if diag["code"] not in seen_codes:
            unique_diagnoses.append(diag)
            seen_codes.add(diag["code"])
    merged_patient["diagnoses"] = unique_diagnoses
    
    return merged_patient

# For testing
if __name__ == "__main__":
    print("Testing Federated Gateway with Normalization...\n")
    
    patient_data = federated_query("P001")
    
    print(f"Patient {patient_data['patient_id']}:")
    print(f"  Diagnoses: {len(patient_data['diagnoses'])} found")
    for diag in patient_data['diagnoses']:
        print(f"    - {diag['name']} ({diag['code']})")
    
    print(f"  Medications: {len(patient_data['medications'])} found")
    for med in patient_data['medications']:
        print(f"    - {med['name']} {med['dosage']}")
    
    print(f"  Labs: {len(patient_data['labs'])} found")
    for lab in patient_data['labs']:
        print(f"    - {lab['test_name']}: {lab['value']}")
    
    print(f"  Episodes: {len(patient_data['episodes'])} found")
    for episode in patient_data['episodes']:
        print(f"    - {episode['type']}: {episode['reason']}")
    
    print("\n✅ Federated gateway working!")