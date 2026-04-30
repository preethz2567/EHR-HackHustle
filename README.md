# HealthBridge EHR - Unified Patient Records System

![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Development-yellow)

## Overview

HealthBridge is a privacy-first, federated Electronic Health Record (EHR) system that unifies patient data across multiple healthcare providers while maintaining explicit patient consent and preventing centralized data breaches.

### Key Features
- **Federated Architecture**: Query hospitals A, B, C simultaneously without centralizing data
- **Patient Consent Control**: Granular control over data access by category (diagnoses, medications, labs, etc.)
- **Rule Based Clinical Engine Powered Synthesis**: 4 specialized agents analyze patient data, orchestrator creates unified narrative
- **Real-Time Audit Logging**: Every access logged for transparency and compliance
- **Session-Based Access**: Doctors get 30-min sessions with automatic logout
- **Manual Report Upload**: Patients can upload vaccine cards, lab reports, discharge summaries

## Architecture

```text
Patient Portal (React)
    ↓
Backend API (Flask)
    ├─ Auth Service (JWT)
    ├─ Data Service (Federated Query)
    ├─ Agent Service (AI Analysis)
    ├─ Export Service (PDF Generation)
    └─ Audit Service (Logging)
    ↓
Doctor Portal (React)
```
