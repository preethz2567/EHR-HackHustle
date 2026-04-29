"""
privacy_model.py
Defines consent categories and access levels for patient data.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict


class ConsentLevel(str, Enum):
    FULL_ACCESS   = "FULL_ACCESS"
    CLINICAL_ONLY = "CLINICAL_ONLY"
    REVOKED       = "REVOKED"


# All data categories that can be consent-controlled
DATA_CATEGORIES = [
    "diagnoses",
    "medications",
    "labs",
    "episodes",
    "genomic",
    "mental_health",
]


@dataclass
class ConsentPreferences:
    """
    Represents a patient's consent settings per data category.
    Defaults to FULL_ACCESS for all clinical categories; REVOKED for genomic/mental_health.
    """
    patient_id: str
    preferences: Dict[str, ConsentLevel] = field(default_factory=dict)

    def __post_init__(self):
        defaults = {
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        }
        # Apply defaults only for missing keys
        for cat, default_level in defaults.items():
            self.preferences.setdefault(cat, default_level)

    def get(self, category: str) -> ConsentLevel:
        return self.preferences.get(category, ConsentLevel.REVOKED)

    def set(self, category: str, level: ConsentLevel):
        if category not in DATA_CATEGORIES:
            raise ValueError(f"Unknown data category: {category}")
        self.preferences[category] = level


# ── Pre-built consent profiles for the 5 demo patients ────────────────────────

PATIENT_CONSENT_PROFILES: Dict[str, ConsentPreferences] = {

    # P001: Stroke / diabetic patient — shares everything except genomic
    "P001": ConsentPreferences(
        patient_id="P001",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        },
    ),

    # P002: Asthma patient — clinical-only for labs, revokes mental_health & genomic
    "P002": ConsentPreferences(
        patient_id="P002",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.CLINICAL_ONLY,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        },
    ),

    # P003: Post-MI patient — full access to everything except genomic
    "P003": ConsentPreferences(
        patient_id="P003",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.CLINICAL_ONLY,
        },
    ),

    # P004: COPD patient — revokes episodes and genomic
    "P004": ConsentPreferences(
        patient_id="P004",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.REVOKED,
            "genomic":      ConsentLevel.REVOKED,
            "mental_health": ConsentLevel.REVOKED,
        },
    ),

    # P005: Type 1 diabetic — shares everything, including genomic (research participant)
    "P005": ConsentPreferences(
        patient_id="P005",
        preferences={
            "diagnoses":    ConsentLevel.FULL_ACCESS,
            "medications":  ConsentLevel.FULL_ACCESS,
            "labs":         ConsentLevel.FULL_ACCESS,
            "episodes":     ConsentLevel.FULL_ACCESS,
            "genomic":      ConsentLevel.FULL_ACCESS,
            "mental_health": ConsentLevel.REVOKED,
        },
    ),
}
