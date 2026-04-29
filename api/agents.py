"""
agents.py — AI Agent Network
=============================
4 specialized clinical agents + 1 orchestrator.
All 4 agents run in parallel via ThreadPoolExecutor.
The orchestrator synthesizes their outputs into a unified narrative.

Agent 1: Risk Assessment Agent
Agent 2: Medication Reconciliation Agent
Agent 3: Episode Synthesis Agent
Agent 4: Labs Interpreter Agent
Orchestrator: Unified Clinical Synthesis
"""

import time
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Clinical Knowledge Base (rule-based reasoning)
# ─────────────────────────────────────────────────────────────────────────────

KNOWN_INTERACTIONS = {
    ("aspirin", "clopidogrel"): {
        "severity": "Moderate",
        "description": "Dual antiplatelet therapy increases bleeding risk. Monitor for GI bleeding and bruising. Check INR if warfarin is co-prescribed."
    },
    ("aspirin", "warfarin"): {
        "severity": "High",
        "description": "Significantly increased bleeding risk. Monitor INR closely and watch for signs of hemorrhage."
    },
    ("metformin", "lisinopril"): {
        "severity": "Low",
        "description": "ACE inhibitors may enhance hypoglycemic effect of metformin. Monitor blood glucose."
    },
    ("metoprolol", "lisinopril"): {
        "severity": "Moderate",
        "description": "Combined antihypertensive effect may cause excessive blood pressure lowering or bradycardia."
    },
}

HIGH_RISK_CONDITIONS = {
    "stroke", "ischemic stroke", "infarction", "myocardial infarction",
    "heart failure", "cardiac arrest", "pulmonary embolism"
}

MODERATE_RISK_CONDITIONS = {
    "diabetes", "hypertension", "copd", "asthma", "ckd",
    "chronic kidney", "atrial fibrillation"
}

RENAL_CAUTION_DRUGS = {"metformin", "lisinopril", "aspirin"}

STATIN_INDICATIONS = {"stroke", "ischemic stroke", "myocardial infarction", "infarction"}

LAB_REFERENCE = {
    "hba1c": {"normal_max": 5.7, "prediabetic_max": 6.4, "unit": "%"},
    "bp systolic": {"normal_max": 130, "stage1_max": 140, "unit": "mmHg"},
    "egfr": {"normal_min": 60, "moderate_min": 30, "unit": "mL/min/1.73m²"},
    "troponin": {"normal_max": 0.04, "unit": "ng/mL"},
}


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1: Risk Assessment Agent
# ─────────────────────────────────────────────────────────────────────────────

def agent_risk(patient_data: dict) -> dict:
    """
    Input: Diagnoses, medications, labs, prior episodes
    Task: Identify clinical risks, drug interactions, contraindications
    Output: JSON with immediate risks, trending concerns, drug interactions
    """
    time.sleep(0.5)  # Simulate processing

    diagnoses = patient_data.get("diagnoses", [])
    medications = patient_data.get("medications", [])
    labs = patient_data.get("labs", [])
    episodes = patient_data.get("episodes", [])

    immediate_risks = []
    high_risk_conditions = []
    moderate_risk_conditions = []
    contraindications = []

    # ── Analyze diagnoses ──
    has_stroke = False
    has_diabetes = False
    has_htn = False
    has_cardiac = False

    for d in diagnoses:
        name = str(d.get("name", "")).lower()
        diag_date = d.get("date_of_diagnosis", "")

        for keyword in HIGH_RISK_CONDITIONS:
            if keyword in name:
                high_risk_conditions.append({
                    "condition": d.get("name"),
                    "level": "High",
                    "since": diag_date
                })
                if "stroke" in name:
                    has_stroke = True
                    immediate_risks.append(
                        f"Prior stroke ({diag_date[:4]}) → requires dual antiplatelet therapy and secondary prevention"
                    )
                if "infarction" in name:
                    has_cardiac = True
                    immediate_risks.append(
                        f"Prior MI ({diag_date[:4]}) → ongoing cardiac monitoring required"
                    )
                break

        for keyword in MODERATE_RISK_CONDITIONS:
            if keyword in name:
                moderate_risk_conditions.append({
                    "condition": d.get("name"),
                    "level": "Moderate",
                    "since": diag_date
                })
                if "diabetes" in name:
                    has_diabetes = True
                if "hypertension" in name:
                    has_htn = True
                break

    # ── Analyze labs for risk signals ──
    latest_egfr = None
    latest_hba1c = None
    for lab in sorted(labs, key=lambda x: x.get("date", ""), reverse=True):
        test = str(lab.get("test_name", "")).lower()
        val = lab.get("value")
        if "egfr" in test and latest_egfr is None and isinstance(val, (int, float)):
            latest_egfr = val
        if "hba1c" in test and latest_hba1c is None and isinstance(val, (int, float)):
            latest_hba1c = val

    if latest_egfr is not None and latest_egfr < 60:
        immediate_risks.append(
            f"Declining eGFR ({latest_egfr} mL/min) → kidney function impaired, affects medication dosing"
        )
        # Check renal contraindications
        for med in medications:
            med_name = med.get("name", "").lower()
            if med_name in RENAL_CAUTION_DRUGS:
                contraindications.append(
                    f"{med.get('name')} requires dose adjustment with eGFR < 60 mL/min"
                )

    if latest_hba1c is not None and latest_hba1c > 7.0 and has_diabetes:
        immediate_risks.append(
            f"Suboptimal glycemic control (HbA1c {latest_hba1c}%) → diabetes management needs intensification"
        )

    # ── Drug interactions ──
    drug_interactions = []
    med_names_lower = [m.get("name", "").lower() for m in medications]
    for (drug_a, drug_b), info in KNOWN_INTERACTIONS.items():
        if drug_a in med_names_lower and drug_b in med_names_lower:
            drug_interactions.append({
                "drugs": [drug_a.title(), drug_b.title()],
                "severity": info["severity"],
                "description": info["description"]
            })

    # ── Comorbidity risk escalation ──
    comorbidity_count = len(high_risk_conditions) + len(moderate_risk_conditions)
    if comorbidity_count >= 3:
        immediate_risks.append(
            f"Multi-morbidity detected ({comorbidity_count} conditions) → complex care coordination required"
        )

    return {
        "status": "completed",
        "immediate_risks": immediate_risks,
        "high_risk_conditions": high_risk_conditions,
        "moderate_risk_conditions": moderate_risk_conditions,
        "drug_interactions": drug_interactions,
        "contraindications": contraindications,
        "summary": f"Detected {len(high_risk_conditions)} high-risk and {len(moderate_risk_conditions)} moderate-risk conditions with {len(drug_interactions)} drug interactions."
    }


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2: Medication Reconciliation Agent
# ─────────────────────────────────────────────────────────────────────────────

def agent_meds(patient_data: dict) -> dict:
    """
    Input: Current medications, diagnoses, allergies
    Task: Are current meds appropriate? Any gaps or duplicates?
    Output: Medication list with indications, therapy gaps, adherence risks
    """
    time.sleep(0.6)

    meds = patient_data.get("medications", [])
    diagnoses = patient_data.get("diagnoses", [])
    allergies = patient_data.get("allergies", [])
    labs = patient_data.get("labs", [])

    diag_names_lower = [str(d.get("name", "")).lower() for d in diagnoses]
    med_names_lower = [m.get("name", "").lower() for m in meds]

    # ── Build current regimen with adherence assessment ──
    current_regimen = []
    for med in meds:
        name = med.get("name", "")
        start = med.get("start_date", "")
        adherence_risk = "low"

        # Long-term meds without recent refill data → flag
        if start and start < "2020-01-01":
            adherence_risk = "monitor"

        current_regimen.append({
            "name": name,
            "dosage": med.get("dosage", ""),
            "indication": med.get("indication", "Unknown"),
            "start_date": start,
            "adherence_risk": adherence_risk
        })

    # ── Detect therapy gaps ──
    therapy_gaps = []

    # Check: stroke/MI patient missing statin?
    has_statin = any("statin" in m or "atorvastatin" in m or "rosuvastatin" in m
                     for m in med_names_lower)
    has_statin_indication = any(
        any(kw in d for kw in STATIN_INDICATIONS) for d in diag_names_lower
    )
    if has_statin_indication and not has_statin:
        therapy_gaps.append(
            "Consider statin therapy for post-stroke/MI secondary prevention (e.g., Atorvastatin 40mg)"
        )

    # Check: diabetes patient – consider GLP-1 if HbA1c rising?
    has_diabetes = any("diabetes" in d for d in diag_names_lower)
    has_glp1 = any("semaglutide" in m or "liraglutide" in m or "glp-1" in m
                    for m in med_names_lower)
    latest_hba1c = None
    for lab in sorted(labs, key=lambda x: x.get("date", ""), reverse=True):
        if "hba1c" in str(lab.get("test_name", "")).lower():
            latest_hba1c = lab.get("value")
            break
    if has_diabetes and latest_hba1c and latest_hba1c > 7.0 and not has_glp1:
        therapy_gaps.append(
            f"HbA1c {latest_hba1c}% despite Metformin → consider adding GLP-1 agonist for cardiometabolic protection"
        )

    # Check: hypertension patient – is BP controlled?
    has_htn = any("hypertension" in d for d in diag_names_lower)
    latest_bp = None
    for lab in sorted(labs, key=lambda x: x.get("date", ""), reverse=True):
        if "systolic" in str(lab.get("test_name", "")).lower():
            latest_bp = lab.get("value")
            break
    if has_htn and latest_bp and latest_bp > 140:
        therapy_gaps.append(
            f"BP Systolic {latest_bp} mmHg despite antihypertensive → consider dose escalation or adding second agent"
        )

    # ── Drug interactions (shared with risk agent but from meds perspective) ──
    interactions_found = []
    for (drug_a, drug_b), info in KNOWN_INTERACTIONS.items():
        if drug_a in med_names_lower and drug_b in med_names_lower:
            interactions_found.append({
                "drugs": [drug_a.title(), drug_b.title()],
                "severity": info["severity"],
                "description": info["description"]
            })

    # ── Allergy check ──
    allergy_conflicts = []
    allergies_lower = [a.lower() for a in allergies]
    for med in meds:
        if med.get("name", "").lower() in allergies_lower:
            allergy_conflicts.append(f"ALERT: {med['name']} is listed as a known allergy!")

    return {
        "status": "completed",
        "active_medications": len(meds),
        "current_regimen": current_regimen,
        "therapy_gaps": therapy_gaps,
        "interactions_found": interactions_found,
        "allergy_conflicts": allergy_conflicts,
        "adherence_flag": "Long-term medications present; verify refill compliance."
    }


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3: Episode Synthesis Agent
# ─────────────────────────────────────────────────────────────────────────────

def agent_episodes(patient_data: dict) -> dict:
    """
    Input: Prior hospitalizations, ED visits, procedures
    Task: What patterns emerged? How has disease trajectory changed?
    Output: Treatment response patterns, disease trajectory, recurrence risk
    """
    time.sleep(0.4)

    episodes = patient_data.get("episodes", [])
    diagnoses = patient_data.get("diagnoses", [])

    # ── Categorize episodes ──
    hospitalizations = [e for e in episodes if e.get("type") == "hospitalization"]
    procedures = [e for e in episodes if e.get("type") == "procedure"]
    ed_visits = [e for e in episodes if e.get("type") == "ed_visit"]

    # ── Build patterns ──
    patterns = []
    for ep in episodes:
        reason = ep.get("reason", "Unknown")
        outcome = ep.get("outcome", "Unknown")
        duration = ep.get("duration_days", "?")
        date = ep.get("date", "Unknown")
        ep_type = ep.get("type", "event")

        if ep_type == "hospitalization":
            patterns.append(
                f"Hospitalization ({date}): {reason} — {duration}-day stay, outcome: {outcome}"
            )
        elif ep_type == "procedure":
            patterns.append(
                f"Procedure ({date}): {reason} — outcome: {outcome}"
            )
        elif ep_type == "ed_visit":
            patterns.append(
                f"ED visit ({date}): {reason} — outcome: {outcome}"
            )

    # ── Disease trajectory assessment ──
    diag_dates = []
    for d in diagnoses:
        ddate = d.get("date_of_diagnosis", "")
        if ddate:
            diag_dates.append(ddate)
    diag_dates.sort()

    trajectory = "Stable"
    if len(diagnoses) >= 3:
        trajectory = "Declining — comorbidities accumulating over time"
    elif len(hospitalizations) >= 2:
        trajectory = "Declining — recurrent hospitalizations indicate disease progression"
    elif len(diagnoses) >= 2 and len(hospitalizations) >= 1:
        trajectory = "Declining after acute event; comorbidities accumulating"

    # ── Recurrence risk score ──
    risk_score = 0.2  # baseline
    risk_score += len(hospitalizations) * 0.15
    risk_score += len(procedures) * 0.05
    risk_score += len(ed_visits) * 0.10
    if len(diagnoses) >= 3:
        risk_score += 0.15
    risk_score = min(round(risk_score, 2), 0.95)

    readmission_risk = "Low"
    if risk_score >= 0.6:
        readmission_risk = "High"
    elif risk_score >= 0.35:
        readmission_risk = "Medium"

    return {
        "status": "completed",
        "total_episodes": len(episodes),
        "recent_hospitalizations": len(hospitalizations),
        "patterns": patterns if patterns else ["No prior episodes on record."],
        "disease_trajectory": trajectory,
        "recurrence_risk": risk_score,
        "readmission_risk_score": readmission_risk
    }


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4: Labs Interpreter Agent
# ─────────────────────────────────────────────────────────────────────────────

def agent_labs(patient_data: dict) -> dict:
    """
    Input: Time-series lab values (HbA1c, BP, eGFR, troponin, etc.)
    Task: What abnormalities, trends, and clinical significance?
    Output: Abnormal values, trending direction, recommended actions
    """
    time.sleep(0.5)

    labs = patient_data.get("labs", [])

    # ── Group labs by test name ──
    grouped = {}
    for lab in labs:
        test = str(lab.get("test_name", "")).strip()
        test_key = test.lower()
        if test_key not in grouped:
            grouped[test_key] = {"name": test, "values": []}
        val = lab.get("value")
        if isinstance(val, (int, float)):
            grouped[test_key]["values"].append({
                "date": lab.get("date", ""),
                "value": val,
                "reference_range": lab.get("reference_range", "")
            })

    # Sort each group by date
    for key in grouped:
        grouped[key]["values"].sort(key=lambda x: x["date"])

    # ── Detect abnormalities ──
    abnormalities = []
    trends = []

    for test_key, data in grouped.items():
        values = data["values"]
        test_display = data["name"]
        if not values:
            continue

        latest = values[-1]
        ref_info = None
        for ref_key in LAB_REFERENCE:
            if ref_key in test_key:
                ref_info = LAB_REFERENCE[ref_key]
                break

        if ref_info is None:
            continue

        # Check latest value against reference
        severity = "normal"
        if "normal_max" in ref_info:
            if latest["value"] > ref_info["normal_max"]:
                severity = "moderate" if latest["value"] <= ref_info.get("stage1_max", ref_info.get("prediabetic_max", float("inf"))) else "high"
                abnormalities.append({
                    "test": test_display,
                    "latest": latest["value"],
                    "reference": latest["reference_range"],
                    "severity": severity,
                    "date": latest["date"]
                })
        elif "normal_min" in ref_info:
            if latest["value"] < ref_info["normal_min"]:
                severity = "moderate" if latest["value"] >= ref_info.get("moderate_min", 0) else "high"
                abnormalities.append({
                    "test": test_display,
                    "latest": latest["value"],
                    "reference": latest["reference_range"],
                    "severity": severity,
                    "date": latest["date"]
                })

        # ── Trend detection (need ≥ 2 values) ──
        if len(values) >= 2:
            first_val = values[0]["value"]
            last_val = values[-1]["value"]
            diff = last_val - first_val
            n_points = len(values)

            if "normal_min" in ref_info:
                # For eGFR: declining is bad
                if diff < -3:
                    rate = abs(diff) / max(n_points - 1, 1)
                    concern = ""
                    if last_val < 60:
                        concern = "CKD stage 3 — affects medication dosing"
                    elif last_val < 30:
                        concern = "CKD stage 4 — nephrology referral needed"
                    trends.append({
                        "test": test_display,
                        "direction": "declining",
                        "from": first_val,
                        "to": last_val,
                        "rate": f"~{rate:.1f} {ref_info['unit']}/reading",
                        "concern": concern or "Monitor closely"
                    })
            else:
                # For HbA1c, BP: rising is bad
                if diff > 2:
                    rate = diff / max(n_points - 1, 1)
                    concern = ""
                    if "hba1c" in test_key:
                        concern = "Worsening glycemic control — therapy intensification needed"
                    elif "systolic" in test_key or "bp" in test_key:
                        concern = "Uncontrolled hypertension — cardiovascular risk increasing"
                    trends.append({
                        "test": test_display,
                        "direction": "rising",
                        "from": first_val,
                        "to": last_val,
                        "rate": f"~{rate:.1f} {ref_info['unit']}/reading",
                        "concern": concern or "Monitor closely"
                    })

    return {
        "status": "completed",
        "total_labs_analyzed": len(labs),
        "abnormalities": abnormalities,
        "abnormal_results": abnormalities,  # backward compat
        "trends": trends,
        "summary": f"Analyzed {len(labs)} lab values across {len(grouped)} tests. Found {len(abnormalities)} abnormalities and {len(trends)} concerning trends."
    }


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator Agent
# ─────────────────────────────────────────────────────────────────────────────

def orchestrator(risk_output: dict, meds_output: dict,
                 episodes_output: dict, labs_output: dict) -> dict:
    """
    Synthesize all 4 agent outputs into a unified, clinically coherent narrative.
    Real synthesis — not just concatenation.
    """
    time.sleep(0.3)

    # ── Gather key signals from each agent ──
    immediate_risks = risk_output.get("immediate_risks", [])
    high_risk = risk_output.get("high_risk_conditions", [])
    drug_interactions = risk_output.get("drug_interactions", [])
    therapy_gaps = meds_output.get("therapy_gaps", [])
    trajectory = episodes_output.get("disease_trajectory", "Stable")
    recurrence = episodes_output.get("recurrence_risk", 0.2)
    readmission = episodes_output.get("readmission_risk_score", "Low")
    abnormal_labs = labs_output.get("abnormalities", [])
    lab_trends = labs_output.get("trends", [])

    # ── Build clinical summary (2-3 sentences, synthesized) ──
    summary_parts = []

    if high_risk:
        conditions = ", ".join(c["condition"] for c in high_risk[:3])
        summary_parts.append(f"Patient has significant history including {conditions}")

    if "declining" in trajectory.lower():
        summary_parts.append("Disease trajectory is declining with accumulating comorbidities")
    elif "stable" in trajectory.lower():
        summary_parts.append("Disease course is currently stable")

    # Cross-domain synthesis: labs → diagnoses → medications
    declining_labs = [t["test"] for t in lab_trends if t["direction"] in ("rising", "declining")]
    if declining_labs:
        summary_parts.append(
            f"Key lab markers ({', '.join(declining_labs)}) are trending unfavorably"
        )

    if therapy_gaps:
        summary_parts.append(f"Medication review identified {len(therapy_gaps)} therapy gap(s)")

    clinical_summary = ". ".join(summary_parts) + "." if summary_parts else "Routine assessment — no critical findings."

    # ── Immediate priorities (ranked by clinical urgency) ──
    priorities = []

    # Priority 1: Life-threatening risks
    if any("stroke" in r.lower() or "mi" in r.lower() or "infarction" in r.lower() for r in immediate_risks):
        priorities.append("Continue and optimize secondary prevention for cardiovascular events")

    # Priority 2: Declining organ function
    egfr_declining = any("egfr" in t.get("test", "").lower() and t["direction"] == "declining" for t in lab_trends)
    if egfr_declining:
        priorities.append("Monitor kidney function closely — adjust renal-eliminated medications if eGFR continues to decline")

    # Priority 3: Uncontrolled chronic conditions
    bp_rising = any("bp" in t.get("test", "").lower() or "systolic" in t.get("test", "").lower() for t in lab_trends if t["direction"] == "rising")
    if bp_rising:
        priorities.append("Adjust antihypertensive regimen — blood pressure is trending upward despite current therapy")

    hba1c_rising = any("hba1c" in t.get("test", "").lower() for t in lab_trends if t["direction"] == "rising")
    if hba1c_rising:
        priorities.append("Intensify diabetes management — HbA1c is rising, consider adding GLP-1 agonist with renal-sparing properties")

    # Priority 4: Therapy gaps
    for gap in therapy_gaps[:2]:
        priorities.append(gap)

    if not priorities:
        priorities.append("Routine follow-up in 3 months")

    # ── Recommended actions with timelines ──
    actions = []
    if bp_rising:
        actions.append("Titrate antihypertensive (within 2 weeks)")
    if hba1c_rising:
        actions.append("Add GLP-1 agonist or adjust insulin regimen (within 1 month)")
    if egfr_declining:
        actions.append("Recheck eGFR and creatinine in 4 weeks; nephrology referral if eGFR < 45")
    if drug_interactions:
        for inter in drug_interactions:
            if inter["severity"] in ("Moderate", "High"):
                actions.append(f"Review {' + '.join(inter['drugs'])} interaction — consider dosage adjustment")
    if readmission in ("Medium", "High"):
        actions.append("Schedule 7-day post-discharge follow-up to prevent readmission")
    if any("statin" in gap.lower() for gap in therapy_gaps):
        actions.append("Initiate statin therapy for secondary prevention (within 1 week)")

    if not actions:
        actions.append("Continue current care plan with routine monitoring")

    # ── Key risk signals ──
    key_risk_signals = {
        "readmission_risk": readmission,
        "disease_trajectory": trajectory.split("—")[0].strip() if "—" in trajectory else trajectory,
        "med_interactions": len(drug_interactions),
        "abnormal_labs": len(abnormal_labs),
        "therapy_gaps": len(therapy_gaps),
        "recurrence_probability": recurrence
    }

    return {
        "clinical_summary": clinical_summary,
        "immediate_priorities": priorities[:5],
        "key_risk_signals": key_risk_signals,
        "recommended_actions": actions[:6]
    }
