"""
config.py — Application Configuration
======================================
Centralized config for Flask app, JWT secrets, and session timeouts.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "ps1-ehr-dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "ps1-jwt-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"

    # Token validity (seconds)
    PATIENT_TOKEN_EXPIRY = 24 * 60 * 60    # 24 hours
    DOCTOR_TOKEN_EXPIRY = 60 * 60           # 1 hour
    SESSION_TOKEN_EXPIRY = 30 * 60          # 30 minutes (doctor session)

    # Biometric simulation
    BIOMETRIC_MATCH_RATE = 1.0  # 100% match rate for demo (set < 1.0 to simulate failures)

    # OTP simulation
    SIMULATED_OTP = "123456"  # Fixed OTP for demo/testing
