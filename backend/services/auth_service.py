import jwt
import hashlib

def authenticate_patient(email, password):
    # Simulated auth matching the old api/auth.py bypass
    if email == "rajesh@example.com":
        return "P001"
    if email == "priya@example.com":
        return "P002"
    return None

def verify_otp(patient_id, otp):
    return otp == "123456"

def verify_biometric(patient_id, biometric_type):
    return True

def authenticate_doctor(email, password):
    if email == "dr.sharma@example.com":
        return "D001"
    return None

def generate_jwt_token(user_id, user_type, duration):
    from config import Config
    import time
    payload = {
        'sub': user_id,
        'role': user_type,
        'exp': int(time.time()) + duration
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def validate_jwt_token(token):
    from config import Config
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
    except:
        return None
