def fetch_patient_data(patient_id):
    # Simulate federated fetch
    from data.synthetic_ehr_generator import generate_synthetic_patients
    patients = generate_synthetic_patients()
    for p in patients:
        if p['id'] == patient_id:
            return p
    return {}

def get_patient_records(patient_id):
    return fetch_patient_data(patient_id)

def upload_manual_report(patient_id, file):
    pass

def get_patient_by_id(patient_id):
    return fetch_patient_data(patient_id)
