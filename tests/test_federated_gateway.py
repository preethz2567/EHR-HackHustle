import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.federated_sources import query_hospital, federated_query

def test_hospital_query():
    """Test that individual hospital queries work"""
    # Hospital A has neurology data
    frag_a = query_hospital("A", "P001")
    assert "diagnoses" in frag_a
    assert len(frag_a["diagnoses"]) > 0
    
    # Hospital B has cardiology data
    frag_b = query_hospital("B", "P001")
    assert "diagnoses" in frag_b
    
    # Hospital C has primary care data
    frag_c = query_hospital("C", "P001")
    assert "medications" in frag_c
    assert "labs" in frag_c
    
    print("✅ Individual hospital queries work")

def test_federated_merge():
    """Test that federated query merges all fragments correctly"""
    patient = federated_query("P001")
    
    # Should have all required fields
    assert "patient_id" in patient
    assert "diagnoses" in patient
    assert "medications" in patient
    assert "labs" in patient
    assert "episodes" in patient
    
    print("✅ Federated merge includes all fields")

def test_diagnoses_merged():
    """Test that diagnoses from multiple hospitals are combined"""
    patient = federated_query("P001")
    
    # Should have diagnoses from both Hospital A and B
    diagnoses = patient["diagnoses"]
    assert len(diagnoses) > 0
    
    # Check for stroke (from A) and hypertension (from B)
    codes = [d["code"] for d in diagnoses]
    assert "I63.9" in codes, "Should have stroke from Hospital A"
    assert "I10" in codes, "Should have hypertension from Hospital B"
    
    print(f"✅ Diagnoses merged correctly ({len(diagnoses)} total)")

def test_medications_from_clinic():
    """Test that medications come from Clinic C"""
    patient = federated_query("P001")
    
    # Should have medications
    meds = patient["medications"]
    assert len(meds) > 0
    
    # Check for specific medications
    med_names = [m["name"] for m in meds]
    assert "Aspirin" in med_names
    assert "Metformin" in med_names
    
    print(f"✅ Medications correct ({len(meds)} medications)")

def test_labs_from_clinic():
    """Test that labs come from Clinic C"""
    patient = federated_query("P001")
    
    # Should have labs
    labs = patient["labs"]
    assert len(labs) > 0
    
    # Check for specific labs
    lab_names = [l["test_name"] for l in labs]
    assert "HbA1c" in lab_names
    
    print(f"✅ Labs correct ({len(labs)} labs)")

def test_episodes_merged():
    """Test that episodes from multiple hospitals are combined"""
    patient = federated_query("P001")
    
    # Should have episodes
    episodes = patient["episodes"]
    assert len(episodes) > 0
    
    print(f"✅ Episodes merged correctly ({len(episodes)} episodes)")

def test_no_duplicate_diagnoses():
    """Test that duplicate diagnoses are removed"""
    patient = federated_query("P001")
    
    diagnoses = patient["diagnoses"]
    codes = [d["code"] for d in diagnoses]
    
    # No duplicates
    assert len(codes) == len(set(codes)), "Should not have duplicate diagnosis codes"
    
    print("✅ No duplicate diagnoses")

def test_all_patients():
    """Test that all 5 patients can be queried"""
    for patient_id in ["P001", "P002", "P003", "P004", "P005"]:
        patient = federated_query(patient_id)
        assert patient["patient_id"] == patient_id
        assert "diagnoses" in patient
        assert "medications" in patient
        assert "labs" in patient
    
    print("✅ All 5 patients can be queried")

if __name__ == "__main__":
    print("Running Federated Gateway Tests...\n")
    
    try:
        test_hospital_query()
        test_federated_merge()
        test_diagnoses_merged()
        test_medications_from_clinic()
        test_labs_from_clinic()
        test_episodes_merged()
        test_no_duplicate_diagnoses()
        test_all_patients()
        
        print("\n" + "="*50)
        print("✅ ALL FEDERATED GATEWAY TESTS PASSED!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)