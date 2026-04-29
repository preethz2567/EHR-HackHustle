import sys
import json
from pathlib import Path

# Add parent directory to path so we can import from data/
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.synthetic_ehr_generator import generate_patient, generate_all_patients, PATIENT_TEMPLATES

def test_patient_has_all_fields():
    """Verify each patient has all required fields"""
    for patient_id in PATIENT_TEMPLATES.keys():
        patient = generate_patient(patient_id)
        
        required_fields = ["patient_id", "age", "diagnoses", "medications", "labs", "episodes", "allergies"]
        for field in required_fields:
            assert field in patient, f"Missing field: {field}"
            assert patient[field] is not None, f"Field {field} is None"
        
        print(f"✅ {patient_id} has all required fields")

def test_patient_data_types():
    """Verify data types are correct"""
    patient = generate_patient("P001")
    
    assert isinstance(patient["patient_id"], str), "patient_id should be string"
    assert isinstance(patient["age"], int), "age should be int"
    assert isinstance(patient["diagnoses"], list), "diagnoses should be list"
    assert isinstance(patient["medications"], list), "medications should be list"
    assert isinstance(patient["labs"], list), "labs should be list"
    assert isinstance(patient["episodes"], list), "episodes should be list"
    assert isinstance(patient["allergies"], list), "allergies should be list"
    
    print("✅ All data types are correct")

def test_diagnosis_fields():
    """Verify diagnosis objects have required fields"""
    patient = generate_patient("P001")
    
    for diagnosis in patient["diagnoses"]:
        assert "code" in diagnosis, "Diagnosis missing code"
        assert "name" in diagnosis, "Diagnosis missing name"
        assert "date_of_diagnosis" in diagnosis, "Diagnosis missing date"
        assert isinstance(diagnosis["code"], str), "Code should be string"
        assert "-" in diagnosis["date_of_diagnosis"], "Date should be YYYY-MM-DD format"
    
    print(f"✅ P001 has {len(patient['diagnoses'])} valid diagnoses")

def test_medication_fields():
    """Verify medication objects have required fields"""
    patient = generate_patient("P001")
    
    for medication in patient["medications"]:
        assert "name" in medication, "Medication missing name"
        assert "dosage" in medication, "Medication missing dosage"
        assert "indication" in medication, "Medication missing indication"
        assert "start_date" in medication, "Medication missing start_date"
    
    print(f"✅ P001 has {len(patient['medications'])} valid medications")

def test_lab_fields():
    """Verify lab objects have required fields"""
    patient = generate_patient("P001")
    
    for lab in patient["labs"]:
        assert "test_name" in lab, "Lab missing test_name"
        assert "value" in lab, "Lab missing value"
        assert "date" in lab, "Lab missing date"
        assert "reference_range" in lab, "Lab missing reference_range"
        assert isinstance(lab["value"], (int, float)), "Lab value should be numeric"
    
    print(f"✅ P001 has {len(patient['labs'])} valid labs")

def test_all_patients_generate():
    """Verify all 5 patients can be generated"""
    patients = generate_all_patients()
    assert len(patients) == 5, f"Expected 5 patients, got {len(patients)}"
    print(f"✅ Generated all 5 patients successfully")

def test_patient_realism():
    """Verify patients have realistic characteristics"""
    for patient_id in PATIENT_TEMPLATES.keys():
        patient = generate_patient(patient_id)
        
        # Age check
        assert 40 <= patient["age"] <= 80, f"Age should be 40-80, got {patient['age']}"
        
        # Should have at least one of each required category
        assert len(patient["diagnoses"]) > 0, "Should have at least one diagnosis"
        assert len(patient["medications"]) > 0, "Should have at least one medication"
        
        print(f"✅ {patient_id} (age {patient['age']}) has realistic characteristics")

if __name__ == "__main__":
    print("Running tests for synthetic patient generator...\n")
    
    try:
        test_patient_has_all_fields()
        test_patient_data_types()
        test_diagnosis_fields()
        test_medication_fields()
        test_lab_fields()
        test_all_patients_generate()
        test_patient_realism()
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
