"""
Generates a PDF report for a prediction result.
Uses reportlab only — no external dependencies beyond pip install reportlab.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── Colour palette ────────────────────────────────────────────────
DARK_RED   = colors.HexColor("#C0392B")
SOFT_RED   = colors.HexColor("#E74C3C")
ORANGE     = colors.HexColor("#E67E22")
GREEN      = colors.HexColor("#27AE60")
DARK_GRAY  = colors.HexColor("#2C3E50")
LIGHT_GRAY = colors.HexColor("#ECF0F1")
WHITE      = colors.white

RISK_COLORS = {
    "Low Risk"      : GREEN,
    "Moderate Risk" : ORANGE,
    "High Risk"     : SOFT_RED,
}


def _risk_color(level: str):
    return RISK_COLORS.get(level, DARK_GRAY)


def create_pdf(report: dict, output_path: str) -> None:
    """
    report keys expected:
        score, risk, message, symptoms, care, values, date
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Title ─────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "title",
        parent    = styles["Title"],
        fontSize  = 22,
        textColor = DARK_RED,
        spaceAfter= 4,
        alignment = TA_CENTER,
    )
    story.append(Paragraph("CardioCare — Heart Risk Report", title_style))

    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.gray,
        alignment=TA_CENTER, spaceAfter=12,
    )
    story.append(Paragraph(f"Generated on {report.get('date', datetime.now().strftime('%d-%m-%Y %H:%M'))}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    story.append(Spacer(1, 0.4*cm))

    # ── Risk Badge ────────────────────────────────────────────────
    risk_level = report.get("risk", "Unknown")
    rc = _risk_color(risk_level)

    risk_table = Table(
        [[f"{report.get('icon','⚠️')}  {risk_level}  —  Score: {report.get('score', 0):.1f} / 100"]],
        colWidths=[16*cm]
    )
    risk_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), rc),
        ("TEXTCOLOR",   (0,0), (-1,-1), WHITE),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 14),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWHEIGHT",   (0,0), (-1,-1), 36),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(risk_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Message ───────────────────────────────────────────────────
    msg_style = ParagraphStyle(
        "msg", parent=styles["Normal"],
        fontSize=11, textColor=DARK_GRAY,
        leading=16, spaceAfter=14,
    )
    story.append(Paragraph(report.get("message", ""), msg_style))

    # ── Section helper ────────────────────────────────────────────
    def section_title(text):
        s = ParagraphStyle(
            "sec", parent=styles["Heading2"],
            fontSize=13, textColor=DARK_RED,
            spaceBefore=12, spaceAfter=6,
        )
        story.append(Paragraph(text, s))
        story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY))

    bullet_style = ParagraphStyle(
        "bullet", parent=styles["Normal"],
        fontSize=10, textColor=DARK_GRAY,
        leading=16, leftIndent=14, spaceAfter=3,
    )

    # ── Symptoms ──────────────────────────────────────────────────
    section_title("Observed / Possible Symptoms")
    for sym in report.get("symptoms", []):
        story.append(Paragraph(f"• {sym}", bullet_style))

    # ── Care Tips ─────────────────────────────────────────────────
    section_title("Recommended Care & Actions")
    for tip in report.get("care", []):
        story.append(Paragraph(f"• {tip}", bullet_style))

    # ── Input Parameters ─────────────────────────────────────────
    section_title("Patient Input Parameters")

    labels = [
        "Age", "Sex (1=M/0=F)", "Chest Pain Type", "Resting BP (mmHg)",
        "Cholesterol (mg/dl)", "Fasting BS > 120", "Resting ECG",
        "Max Heart Rate", "Exercise Angina", "ST Depression",
        "Slope of ST", "Major Vessels (0-3)", "Thalassemia",
    ]
    values = report.get("values", [])

    table_data = [["Parameter", "Value"]]
    for label, val in zip(labels, values):
        table_data.append([label, str(val)])

    param_table = Table(table_data, colWidths=[10*cm, 6*cm])
    param_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  DARK_RED),
        ("TEXTCOLOR",   (0,0), (-1,0),  WHITE),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 10),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, LIGHT_GRAY]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.lightgrey),
        ("ALIGN",       (1,0), (1,-1),  "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWHEIGHT",   (0,0), (-1,-1), 22),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Disclaimer ────────────────────────────────────────────────
    disc_style = ParagraphStyle(
        "disc", parent=styles["Normal"],
        fontSize=8, textColor=colors.gray,
        alignment=TA_CENTER, leading=12,
    )
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "This report is generated by an AI model for informational purposes only. "
        "It is NOT a substitute for professional medical advice, diagnosis, or treatment. "
        "Always consult a qualified healthcare provider.",
        disc_style
    ))

    doc.build(story)
