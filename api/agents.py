"""
agents.py — AI Agent Definitions
================================
Mock implementations of Person B's multi-agent architecture.
Includes 4 parallel agents (Risk, Meds, Episodes, Labs) and an Orchestrator.
"""

import time

def agent_risk(patient_data: dict) -> dict:
    """Analyze diagnoses and demographic data for risks."""
    time.sleep(0.5)  # Simulate processing
    diagnoses = patient_data.get("diagnoses", [])
    
    high_risk = []
    moderate_risk = []
    
    for d in diagnoses:
        name = str(d.get("name", "")).lower()
        if "stroke" in name or "infarction" in name:
            high_risk.append({"condition": d.get("name"), "level": "High"})
        elif "diabetes" in name or "hypertension" in name:
            moderate_risk.append({"condition": d.get("name"), "level": "Moderate"})
            
    return {
        "status": "completed",
        "high_risk_conditions": high_risk,
        "moderate_risk_conditions": moderate_risk,
        "summary": f"Detected {len(high_risk)} high risk and {len(moderate_risk)} moderate risk conditions."
    }

def agent_meds(patient_data: dict) -> dict:
    """Analyze medications for interactions and compliance."""
    time.sleep(0.6)
    meds = patient_data.get("medications", [])
    
    interactions = []
    # Mock some interaction detection
    med_names = [m.get("name", "").lower() for m in meds]
    if "aspirin" in med_names and "clopidogrel" in med_names:
        interactions.append({
            "drugs": ["Aspirin", "Clopidogrel"],
            "severity": "Moderate",
            "description": "Increased bleeding risk when used together."
        })
        
    return {
        "status": "completed",
        "active_medications": len(meds),
        "interactions_found": interactions,
        "adherence_flag": "No recent refills missed."
    }

def agent_episodes(patient_data: dict) -> dict:
    """Analyze episode history for readmission risk or patterns."""
    time.sleep(0.4)
    episodes = patient_data.get("episodes", [])
    
    recent_hospitalizations = sum(1 for e in episodes if e.get("type") == "hospitalization")
    
    readmission_risk = "Low"
    if recent_hospitalizations > 0:
        readmission_risk = "Medium"
    if recent_hospitalizations > 2:
        readmission_risk = "High"
        
    return {
        "status": "completed",
        "total_episodes": len(episodes),
        "recent_hospitalizations": recent_hospitalizations,
        "readmission_risk_score": readmission_risk
    }

def agent_labs(patient_data: dict) -> dict:
    """Analyze lab results for critical values or abnormal trends."""
    time.sleep(0.5)
    labs = patient_data.get("labs", [])
    
    abnormal = []
    for lab in labs:
        val = lab.get("value")
        ref = lab.get("reference_range", "")
        # Very simple mock check
        if "HbA1c" in str(lab.get("test_name")) and isinstance(val, (int, float)):
            if val > 6.5:
                abnormal.append({"test": lab.get("test_name"), "value": val, "flag": "High"})
        elif "Systolic" in str(lab.get("test_name")) and isinstance(val, (int, float)):
            if val > 130:
                abnormal.append({"test": lab.get("test_name"), "value": val, "flag": "High"})
                
    return {
        "status": "completed",
        "total_labs_analyzed": len(labs),
        "abnormal_results": abnormal
    }

def orchestrator(risk_output: dict, meds_output: dict, episodes_output: dict, labs_output: dict) -> dict:
    """
    Synthesize the outputs of the 4 agents into a unified clinical summary.
    """
    time.sleep(0.3)
    
    # Generate immediate priorities
    priorities = []
    if risk_output.get("high_risk_conditions"):
        priorities.append("Monitor high-risk cardiovascular conditions.")
    if meds_output.get("interactions_found"):
        priorities.append("Review medication interactions (Aspirin/Clopidogrel).")
    if labs_output.get("abnormal_results"):
        priorities.append("Address out-of-range lab values.")
        
    # Generate recommended actions
    actions = []
    if episodes_output.get("readmission_risk_score") in ["Medium", "High"]:
        actions.append("Schedule 7-day post-discharge follow-up to prevent readmission.")
    if any(m.get("severity") == "Moderate" for m in meds_output.get("interactions_found", [])):
        actions.append("Consider dosage adjustment for dual antiplatelet therapy.")
        
    return {
        "clinical_summary": "Patient has a complex medical history with active management required for cardiovascular and metabolic conditions.",
        "immediate_priorities": priorities if priorities else ["Routine follow-up in 3 months."],
        "key_risk_signals": {
            "readmission_risk": episodes_output.get("readmission_risk_score"),
            "med_interactions": len(meds_output.get("interactions_found", [])),
            "abnormal_labs": len(labs_output.get("abnormal_results", []))
        },
        "recommended_actions": actions if actions else ["Continue current care plan."]
    }
