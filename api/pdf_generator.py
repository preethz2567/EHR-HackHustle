"""
pdf_generator.py — Medical Report PDF Generator
================================================
Generates professional healthcare-formatted PDF reports
from dashboard data using ReportLab.
"""

import io
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)


# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
PRIMARY = HexColor("#1a365d")       # Dark navy
SECONDARY = HexColor("#2b6cb0")     # Medium blue
ACCENT = HexColor("#e53e3e")        # Red for high risk
WARN = HexColor("#dd6b20")          # Orange for moderate
SUCCESS = HexColor("#38a169")       # Green for normal
LIGHT_BG = HexColor("#f7fafc")      # Light gray background
BORDER = HexColor("#cbd5e0")        # Gray border
WHITE = HexColor("#ffffff")
BLACK = HexColor("#1a202c")


# ---------------------------------------------------------------------------
# Custom styles
# ---------------------------------------------------------------------------

def _build_styles():
    """Build a set of custom ParagraphStyles for the medical report."""
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"],
            fontSize=22, textColor=PRIMARY, spaceAfter=4 * mm,
            alignment=TA_CENTER, fontName="Helvetica-Bold",
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle", parent=base["Normal"],
            fontSize=10, textColor=SECONDARY, spaceAfter=6 * mm,
            alignment=TA_CENTER, fontName="Helvetica",
        ),
        "section": ParagraphStyle(
            "SectionHeader", parent=base["Heading2"],
            fontSize=14, textColor=WHITE, spaceAfter=3 * mm,
            spaceBefore=6 * mm, fontName="Helvetica-Bold",
            backColor=PRIMARY, borderPadding=(4, 8, 4, 8),
        ),
        "body": ParagraphStyle(
            "BodyText", parent=base["Normal"],
            fontSize=10, textColor=BLACK, leading=14,
            fontName="Helvetica",
        ),
        "bold": ParagraphStyle(
            "BoldText", parent=base["Normal"],
            fontSize=10, textColor=BLACK, leading=14,
            fontName="Helvetica-Bold",
        ),
        "risk_high": ParagraphStyle(
            "RiskHigh", parent=base["Normal"],
            fontSize=10, textColor=ACCENT, fontName="Helvetica-Bold",
        ),
        "risk_moderate": ParagraphStyle(
            "RiskModerate", parent=base["Normal"],
            fontSize=10, textColor=WARN, fontName="Helvetica-Bold",
        ),
        "footer": ParagraphStyle(
            "Footer", parent=base["Normal"],
            fontSize=8, textColor=SECONDARY, alignment=TA_CENTER,
            fontName="Helvetica-Oblique",
        ),
        "disclaimer": ParagraphStyle(
            "Disclaimer", parent=base["Normal"],
            fontSize=7, textColor=HexColor("#718096"), alignment=TA_CENTER,
            fontName="Helvetica-Oblique", spaceBefore=4 * mm,
        ),
    }
    return styles


# ---------------------------------------------------------------------------
# Table helper
# ---------------------------------------------------------------------------

def _styled_table(data, col_widths=None):
    """Create a consistently styled table."""
    t = Table(data, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 1), (-1, -1), BLACK),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BG]),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_medical_report_pdf(dashboard_data: dict, doctor_name: str = "Doctor") -> io.BytesIO:
    """
    Generate a professional medical report PDF from dashboard data.

    Args:
        dashboard_data: The response dict from _build_dashboard_dict()
        doctor_name: Name of the doctor generating the report

    Returns:
        io.BytesIO buffer containing the PDF bytes.
    """
    buf = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2.5 * cm,
        title="Patient Medical Report",
        author=doctor_name,
    )

    story = []
    now = datetime.now(timezone.utc)

    ps = dashboard_data.get("patient_summary", {})
    risk = dashboard_data.get("risk_assessment", {})
    trends = dashboard_data.get("health_trends", {})
    recs = dashboard_data.get("recommendations", {})

    # ── HEADER ────────────────────────────────────────────────────────
    story.append(Paragraph("Patient Medical Report", styles["title"]))
    story.append(Paragraph(
        f"Generated on {now.strftime('%B %d, %Y at %H:%M UTC')}  •  Prepared by {doctor_name}",
        styles["subtitle"]
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceAfter=4 * mm))

    # ── SECTION 1: PATIENT INFO ───────────────────────────────────────
    story.append(Paragraph("1. Patient Information", styles["section"]))
    story.append(Spacer(1, 2 * mm))

    info_data = [
        ["Field", "Value"],
        ["Patient ID", str(ps.get("patient_id", "N/A"))],
        ["Age", str(ps.get("age", "Unknown"))],
        ["Gender", str(ps.get("gender", "Unknown"))],
        ["Allergies", ", ".join(ps.get("allergies", [])) or "None reported"],
        ["Total Diagnoses", str(ps.get("diagnoses_count", 0))],
        ["Active Medications", str(ps.get("medications_count", 0))],
        ["Lab Tests on Record", str(ps.get("lab_tests_count", 0))],
    ]
    story.append(_styled_table(info_data, col_widths=[5 * cm, 12 * cm]))
    story.append(Spacer(1, 4 * mm))

    # ── SECTION 2: RISK ASSESSMENT ────────────────────────────────────
    story.append(Paragraph("2. Risk Assessment", styles["section"]))
    story.append(Spacer(1, 2 * mm))

    immediate_risks = risk.get("immediate_risks", [])
    if immediate_risks:
        risk_data = [["Condition", "Risk Level"]]
        for r in immediate_risks:
            risk_data.append([
                str(r.get("condition", "Unknown")),
                str(r.get("level", "Unknown"))
            ])
        story.append(Paragraph("Immediate Risks:", styles["bold"]))
        story.append(Spacer(1, 1 * mm))
        story.append(_styled_table(risk_data, col_widths=[12 * cm, 5 * cm]))
        story.append(Spacer(1, 3 * mm))
    else:
        story.append(Paragraph("No immediate risks identified.", styles["body"]))
        story.append(Spacer(1, 2 * mm))

    interactions = risk.get("drug_interactions", [])
    if interactions:
        story.append(Paragraph("Drug Interactions:", styles["bold"]))
        story.append(Spacer(1, 1 * mm))
        int_data = [["Drugs", "Description", "Severity"]]
        for inter in interactions:
            drugs = ", ".join(inter.get("drugs", []))
            int_data.append([
                drugs,
                str(inter.get("description", "")),
                str(inter.get("severity", ""))
            ])
        story.append(_styled_table(int_data, col_widths=[5 * cm, 8 * cm, 4 * cm]))
        story.append(Spacer(1, 4 * mm))

    # ── SECTION 3: HEALTH TRENDS ──────────────────────────────────────
    story.append(Paragraph("3. Health Trends", styles["section"]))
    story.append(Spacer(1, 2 * mm))

    for label, key, unit in [
        ("HbA1c", "hba1c", "%"),
        ("Blood Pressure (Systolic)", "bp", "mmHg"),
        ("eGFR", "egfr", "mL/min"),
    ]:
        values = trends.get(key, [])
        if values:
            story.append(Paragraph(f"{label} ({unit}):", styles["bold"]))
            story.append(Spacer(1, 1 * mm))
            t_data = [["Date", "Value"]]
            for v in values:
                t_data.append([str(v.get("date", "")), str(v.get("value", ""))])
            story.append(_styled_table(t_data, col_widths=[8 * cm, 9 * cm]))
            story.append(Spacer(1, 3 * mm))
        else:
            story.append(Paragraph(f"{label}: No data available.", styles["body"]))
            story.append(Spacer(1, 2 * mm))

    # ── SECTION 4: CLINICAL RECOMMENDATIONS ───────────────────────────
    story.append(Paragraph("4. Clinical Recommendations", styles["section"]))
    story.append(Spacer(1, 2 * mm))

    summary = recs.get("clinical_summary", "No clinical summary available.")
    story.append(Paragraph(f"<b>Clinical Summary:</b> {summary}", styles["body"]))
    story.append(Spacer(1, 3 * mm))

    priorities = recs.get("immediate_priorities", [])
    if priorities:
        story.append(Paragraph("<b>Immediate Priorities:</b>", styles["body"]))
        for i, p in enumerate(priorities, 1):
            story.append(Paragraph(f"  {i}. {p}", styles["body"]))
        story.append(Spacer(1, 3 * mm))

    actions = recs.get("recommended_actions", [])
    if actions:
        story.append(Paragraph("<b>Recommended Actions:</b>", styles["body"]))
        for i, a in enumerate(actions, 1):
            story.append(Paragraph(f"  {i}. {a}", styles["body"]))
        story.append(Spacer(1, 3 * mm))

    risk_signals = recs.get("key_risk_signals", {})
    if risk_signals:
        story.append(Paragraph("<b>Key Risk Signals:</b>", styles["body"]))
        for k, v in risk_signals.items():
            story.append(Paragraph(f"  • {k}: {v}", styles["body"]))
        story.append(Spacer(1, 4 * mm))

    # ── FOOTER / DISCLAIMER ───────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=6 * mm))
    story.append(Paragraph(
        f"CONFIDENTIAL — Generated on {now.strftime('%Y-%m-%d %H:%M UTC')} for {doctor_name}. "
        "This report is for clinical reference only.",
        styles["footer"]
    ))
    story.append(Paragraph(
        "This document contains protected health information (PHI) and is intended solely for the "
        "authorized healthcare provider. Unauthorized use, disclosure, or distribution is strictly "
        "prohibited. Data sourced from federated EHR providers via PS-1 Privacy Layer.",
        styles["disclaimer"]
    ))

    doc.build(story)
    buf.seek(0)
    return buf
