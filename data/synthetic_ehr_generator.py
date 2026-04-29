import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ICD-10 diagnosis codes (real codes)
ICD10_DIAGNOSES = {
    "I63.9": "Ischemic stroke, unspecified",
    "E11.9": "Type 2 diabetes mellitus without complications",
    "I10": "Essential (primary) hypertension",
    "J44.9": "Chronic obstructive pulmonary disease, unspecified",
    "I21.9": "ST elevation (STEMI) and non-ST elevation (NSTEMI) of unspecified site",
    "I25.10": "Atherosclerotic heart disease of native coronary artery with angina pectoris",
    "E10.9": "Type 1 diabetes mellitus without complications",
    "J45.9": "Asthma, unspecified",
}

# Real medication names
MEDICATIONS = {
    "Aspirin": "100mg daily",
    "Clopidogrel": "75mg daily",
    "Metformin": "500mg BID",
    "Lisinopril": "10mg daily",


    
    "Atorvastatin": "20mg daily",
    "Metoprolol": "50mg BID",
    "Albuterol": "2 puffs as needed",
    "Fluticasone": "2 puffs daily",
    "Insulin Glargine": "20 units daily",
}

# Lab tests
LAB_TESTS = {
    "HbA1c": {"range": (5.0, 9.0), "normal_max": 5.7, "unit": "%"},
    "Creatinine": {"range": (0.6, 2.0), "normal_max": 1.0, "unit": "mg/dL"},
    "eGFR": {"range": (20, 120), "normal_min": 60, "unit": "mL/min"},
    "Troponin": {"range": (0.01, 2.0), "normal_max": 0.04, "unit": "ng/mL"},
    "BP Systolic": {"range": (90, 180), "normal_max": 130, "unit": "mmHg"},
}

# Allergy list
ALLERGIES = ["Penicillin", "Sulfa", "NSAIDs", "ACE inhibitors", "Statins", "None"]

# Patient templates - realistic disease profiles
PATIENT_TEMPLATES = {
    "P001": {
        "age": 68,
        "diagnoses": ["I63.9", "E11.9", "I10"],  # Stroke, diabetes, hypertension
        "medications": ["Aspirin", "Clopidogrel", "Metformin", "Lisinopril"],
        "labs": ["HbA1c", "Creatinine", "eGFR"],
        "allergies": ["Penicillin"],
    },
    "P002": {
        "age": 45,
        "diagnoses": ["J45.9", "I10"],  # Asthma, hypertension
        "medications": ["Albuterol", "Fluticasone", "Lisinopril"],
        "labs": ["BP Systolic"],
        "allergies": ["NSAIDs"],
    },
    "P003": {
        "age": 72,
        "diagnoses": ["I21.9", "I10"],  # MI, hypertension
        "medications": ["Aspirin", "Atorvastatin", "Metoprolol", "Lisinopril"],
        "labs": ["Troponin", "Creatinine", "eGFR"],
        "allergies": ["None"],
    },
    "P004": {
        "age": 55,
        "diagnoses": ["J44.9"],  # COPD
        "medications": ["Albuterol", "Fluticasone"],
        "labs": ["eGFR"],
        "allergies": ["Sulfa"],
    },
    "P005": {
        "age": 40,
        "diagnoses": ["E10.9"],  # Type 1 diabetes
        "medications": ["Insulin Glargine"],
        "labs": ["HbA1c"],
        "allergies": ["None"],
    },
}

def random_date(start_year: int, end_year: int) -> str:
    """Generate random date between start and end year (YYYY-MM-DD format)"""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    return random_date.strftime("%Y-%m-%d")

def generate_diagnoses(diagnosis_codes: List[str]) -> List[Dict[str, Any]]:
    """Generate diagnosis objects with realistic dates"""
    diagnoses = []
    current_year = datetime.now().year
    for code in diagnosis_codes:
        diagnosis = {
            "code": code,
            "name": ICD10_DIAGNOSES.get(code, "Unknown diagnosis"),
            "date_of_diagnosis": random_date(current_year - 15, current_year - 1)  # 1-15 years ago
        }
        diagnoses.append(diagnosis)
    return diagnoses

def generate_medications(med_names: List[str], diagnosis_dates: List[str]) -> List[Dict[str, Any]]:
    """Generate medication objects. Start date should be after or with diagnosis"""
    medications = []
    earliest_diagnosis = min(diagnosis_dates) if diagnosis_dates else "2015-01-01"
    for med_name in med_names:
        medication = {
            "name": med_name,
            "dosage": MEDICATIONS.get(med_name, "unknown dosage"),
            "indication": "Chronic disease management",  # Simplified for demo
            "start_date": random_date(int(earliest_diagnosis[:4]), datetime.now().year)
        }
        medications.append(medication)
    return medications

def generate_labs(lab_names: List[str]) -> List[Dict[str, Any]]:
    """Generate realistic lab results"""
    labs = []
    for lab_name in lab_names:
        lab_info = LAB_TESTS.get(lab_name, {})
        value_range = lab_info.get("range", (0, 100))
        value = round(random.uniform(value_range[0], value_range[1]), 2)
        
        lab = {
            "test_name": lab_name,
            "value": value,
            "date": random_date(datetime.now().year - 1, datetime.now().year),
            "reference_range": f"{value_range[0]} - {value_range[1]} {lab_info.get('unit', '')}"
        }
        labs.append(lab)
    return labs

def generate_episodes(diagnosis_dates: List[str]) -> List[Dict[str, Any]]:
    """Generate clinical episodes (hospitalizations, ED visits)"""
    episodes = []
    for diagnosis_date in diagnosis_dates:
        # Random chance of having an episode for each diagnosis
        if random.random() > 0.5:  # 50% chance
            episode_year = int(diagnosis_date[:4])
            episode = {
                "type": random.choice(["hospitalization", "ED visit"]),
                "date": random_date(episode_year, episode_year + 1),
                "reason": "Related to primary diagnosis",
                "outcome": random.choice(["discharged to home", "discharged to facility", "admitted"]),
                "duration_days": random.randint(1, 10)
            }
            episodes.append(episode)
    return episodes

def generate_allergies() -> List[str]:
    """Generate random allergies"""
    return [random.choice(ALLERGIES)]

def generate_patient(patient_id: str) -> Dict[str, Any]:
    """
    Main function: Generate realistic synthetic patient data
    
    Args:
        patient_id: Patient identifier (e.g., "P001")
    
    Returns:
        Dictionary with complete patient data matching schema
    """
    if patient_id not in PATIENT_TEMPLATES:
        raise ValueError(f"Unknown patient template: {patient_id}")
    
    template = PATIENT_TEMPLATES[patient_id]
    
    # Generate each component
    diagnoses = generate_diagnoses(template["diagnoses"])
    diagnosis_dates = [d["date_of_diagnosis"] for d in diagnoses]
    medications = generate_medications(template["medications"], diagnosis_dates)
    labs = generate_labs(template["labs"])
    episodes = generate_episodes(diagnosis_dates)
    allergies = generate_allergies()
    
    # Assemble patient object
    patient = {
        "patient_id": patient_id,
        "age": template["age"],
        "diagnoses": diagnoses,
        "medications": medications,
        "labs": labs,
        "episodes": episodes,
        "allergies": allergies
    }
    
    return patient

def generate_all_patients() -> Dict[str, Dict[str, Any]]:
    """Generate all 5 test patients"""
    patients = {}
    for patient_id in PATIENT_TEMPLATES.keys():
        patients[patient_id] = generate_patient(patient_id)
    return patients

# For testing
if __name__ == "__main__":
    # Generate one patient to verify format
    patient_p001 = generate_patient("P001")
    print(f"Generated Patient P001:")
    print(f"  Age: {patient_p001['age']}")
    print(f"  Diagnoses: {[d['name'] for d in patient_p001['diagnoses']]}")
    print(f"  Medications: {[m['name'] for m in patient_p001['medications']]}")
    print(f"  Labs: {[l['test_name'] for l in patient_p001['labs']]}")
    print(f"  Episodes: {len(patient_p001['episodes'])} episode(s)")
    print(f"  Allergies: {patient_p001['allergies']}")
    print("\n✅ Synthetic patient generator working!")
    
    # Generate all patients
    print("\nGenerating all 5 patients...")
    all_patients = generate_all_patients()
    print(f"✅ Generated {len(all_patients)} patients successfully")