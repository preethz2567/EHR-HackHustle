from data.synthetic_ehr_generator import generate_patient
from typing import Dict, Any

# Hospital data fragments
HOSPITAL_DATA = {
    "A": {
        # Hospital A: Neurology specialists
        # Knows: diagnoses, episodes, imaging
        "P001": {
            "diagnoses": [
                {
                    "code": "I63.9",
                    "name": "Ischemic stroke, unspecified",
                    "date_of_diagnosis": "2022-03-15"
                },
                {
                    "code": "E11.9",
                    "name": "Type 2 diabetes mellitus without complications",
                    "date_of_diagnosis": "2010-05-12"
                }
            ],
            "episodes": [
                {
                    "type": "hospitalization",
                    "date": "2022-03-15",
                    "reason": "Acute ischemic stroke",
                    "outcome": "discharged to home",
                    "duration_days": 5
                }
            ]
        },
        "P002": {
            "diagnoses": [],
            "episodes": []
        },
        "P003": {
            "diagnoses": [
                {
                    "code": "I21.9",
                    "name": "Myocardial infarction",
                    "date_of_diagnosis": "2020-06-10"
                }
            ],
            "episodes": [
                {
                    "type": "hospitalization",
                    "date": "2020-06-10",
                    "reason": "Acute MI",
                    "outcome": "discharged to home",
                    "duration_days": 4
                }
            ]
        },
        "P004": {"diagnoses": [], "episodes": []},
        "P005": {"diagnoses": [], "episodes": []}
    },
    "B": {
        # Hospital B: Cardiology specialists
        # Knows: cardiac history, imaging, procedures
        "P001": {
            "diagnoses": [
                {
                    "code": "I10",
                    "name": "Essential hypertension",
                    "date_of_diagnosis": "2005-06-20"
                }
            ],
            "episodes": []
        },
        "P002": {
            "diagnoses": [
                {
                    "code": "I10",
                    "name": "Essential hypertension",
                    "date_of_diagnosis": "2015-01-15"
                }
            ],
            "episodes": []
        },
        "P003": {
            "diagnoses": [
                {
                    "code": "I10",
                    "name": "Essential hypertension",
                    "date_of_diagnosis": "2008-03-20"
                }
            ],
            "episodes": [
                {
                    "type": "procedure",
                    "date": "2020-06-15",
                    "reason": "Cardiac intervention",
                    "outcome": "stent placed",
                    "duration_days": 1
                }
            ]
        },
        "P004": {"diagnoses": [], "episodes": []},
        "P005": {"diagnoses": [], "episodes": []}
    },
    "C": {
        # Hospital C (Clinic): Primary care
        # Knows: current medications, recent labs, vitals
        "P001": {
            "medications": [
                {
                    "name": "Aspirin",
                    "dosage": "100mg daily",
                    "indication": "Post-stroke prevention",
                    "start_date": "2022-03-16"
                },
                {
                    "name": "Clopidogrel",
                    "dosage": "75mg daily",
                    "indication": "Post-stroke prevention",
                    "start_date": "2022-03-16"
                },
                {
                    "name": "Metformin",
                    "dosage": "500mg BID",
                    "indication": "Type 2 diabetes",
                    "start_date": "2010-05-12"
                },
                {
                    "name": "Lisinopril",
                    "dosage": "10mg daily",
                    "indication": "Hypertension",
                    "start_date": "2005-06-20"
                }
            ],
            "labs": [
                {
                    "test_name": "HbA1c",
                    "value": 7.2,
                    "date": "2024-01-10",
                    "reference_range": "< 5.7 (normal)"
                }
            ]
        },
        "P002": {
            "medications": [
                {
                    "name": "Albuterol",
                    "dosage": "2 puffs as needed",
                    "indication": "Asthma",
                    "start_date": "2015-01-15"
                },
                {
                    "name": "Lisinopril",
                    "dosage": "10mg daily",
                    "indication": "Hypertension",
                    "start_date": "2015-01-15"
                }
            ],
            "labs": [
                {
                    "test_name": "BP Systolic",
                    "value": 135,
                    "date": "2024-01-12",
                    "reference_range": "< 130 (normal)"
                }
            ]
        },
        "P003": {
            "medications": [
                {
                    "name": "Atorvastatin",
                    "dosage": "20mg daily",
                    "indication": "Cholesterol",
                    "start_date": "2020-06-20"
                },
                {
                    "name": "Metoprolol",
                    "dosage": "50mg BID",
                    "indication": "Heart disease",
                    "start_date": "2020-06-20"
                }
            ],
            "labs": [
                {
                    "test_name": "Troponin",
                    "value": 0.02,
                    "date": "2024-01-08",
                    "reference_range": "< 0.04 (normal)"
                }
            ]
        },
        "P004": {
            "medications": [
                {
                    "name": "Albuterol",
                    "dosage": "2 puffs as needed",
                    "indication": "COPD",
                    "start_date": "2018-06-10"
                }
            ],
            "labs": []
        },
        "P005": {
            "medications": [
                {
                    "name": "Insulin Glargine",
                    "dosage": "20 units daily",
                    "indication": "Type 1 diabetes",
                    "start_date": "2015-01-01"
                }
            ],
            "labs": [
                {
                    "test_name": "HbA1c",
                    "value": 6.8,
                    "date": "2024-01-05",
                    "reference_range": "< 5.7 (normal)"
                }
            ]
        }
    }
}

def query_hospital(hospital_id: str, patient_id: str) -> Dict[str, Any]:
    """
    Query a specific hospital for their fragment of patient data
    
    Args:
        hospital_id: "A", "B", or "C"
        patient_id: "P001", "P002", etc.
    
    Returns:
        Fragment of patient data from that hospital
    """
    if hospital_id not in HOSPITAL_DATA:
        raise ValueError(f"Unknown hospital: {hospital_id}")
    
    if patient_id not in HOSPITAL_DATA[hospital_id]:
        raise ValueError(f"Unknown patient: {patient_id}")
    
    return HOSPITAL_DATA[hospital_id][patient_id]

def federated_query(patient_id: str) -> Dict[str, Any]:
    """
    Query all 3 hospitals and merge their data fragments
    
    Simulates real federated healthcare system:
    - Hospital A: Neurology records (diagnoses, episodes)
    - Hospital B: Cardiology records (cardiac procedures)
    - Hospital C: Primary care records (medications, labs)
    
    Args:
        patient_id: Patient identifier (e.g., "P001")
    
    Returns:
        Merged patient data from all 3 hospitals
    """
    # Get fragments from each hospital
    fragment_a = query_hospital("A", patient_id)
    fragment_b = query_hospital("B", patient_id)
    fragment_c = query_hospital("C", patient_id)
    
    # Initialize merged patient object with patient ID
    merged_patient = {
        "patient_id": patient_id,
        "diagnoses": [],
        "medications": [],
        "labs": [],
        "episodes": [],
        "allergies": []  # Not stored in federated system
    }
    
    # Merge diagnoses from A and B
    if "diagnoses" in fragment_a:
        merged_patient["diagnoses"].extend(fragment_a["diagnoses"])
    if "diagnoses" in fragment_b:
        merged_patient["diagnoses"].extend(fragment_b["diagnoses"])
    
    # Merge medications from C
    if "medications" in fragment_c:
        merged_patient["medications"] = fragment_c["medications"]
    
    # Merge labs from C
    if "labs" in fragment_c:
        merged_patient["labs"] = fragment_c["labs"]
    
    # Merge episodes from A and B
    if "episodes" in fragment_a:
        merged_patient["episodes"].extend(fragment_a["episodes"])
    if "episodes" in fragment_b:
        merged_patient["episodes"].extend(fragment_b["episodes"])
    
    # Remove duplicates from diagnoses (by code)
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
    print("Testing Federated Gateway...\n")
    
    # Test federated query for P001
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