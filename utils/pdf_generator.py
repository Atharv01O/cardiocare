"""
Generates a polished clinical-style PDF report — header band, patient info card,
risk overview (3 cards), AI summary, recommended care, health indicators,
two-column parameter table, and disclaimer footer.
Uses reportlab only.
"""

import os
import random
import string
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── Colour palette ────────────────────────────────────────────────
NAVY        = colors.HexColor("#1c2541")
DARK_RED    = colors.HexColor("#c0392b")
ACCENT_RED  = colors.HexColor("#d62839")
ORANGE      = colors.HexColor("#d97a1f")
GREEN       = colors.HexColor("#1a9e5c")
BLUE        = colors.HexColor("#3d6b8c")
PURPLE      = colors.HexColor("#6d4fc7")
LIGHT_GRAY  = colors.HexColor("#f2f0eb")
MID_GRAY    = colors.HexColor("#e7e4dd")
TEXT_GRAY   = colors.HexColor("#3a3f4b")
MUTED_GRAY  = colors.HexColor("#767b8a")
WHITE       = colors.white

# Soft tinted card backgrounds
GREEN_BG  = colors.HexColor("#e9f8f0")
BLUE_BG   = colors.HexColor("#eaf2f8")
PURPLE_BG = colors.HexColor("#f0ecfb")
ORANGE_BG = colors.HexColor("#fdf1e3")

RISK_COLORS = {
    "Low Risk"      : GREEN,
    "Moderate Risk" : ORANGE,
    "High Risk"     : ACCENT_RED,
}
RISK_BG = {
    "Low Risk"      : GREEN_BG,
    "Moderate Risk" : ORANGE_BG,
    "High Risk"     : colors.HexColor("#fbe4e2"),
}


def _risk_color(level: str):
    return RISK_COLORS.get(level, NAVY)


def _gen_patient_id() -> str:
    today = datetime.now()
    rand  = "".join(random.choices(string.digits, k=4))
    return f"CC-{today.year}-{today.strftime('%m%d')}-{rand}"


def _gen_report_id() -> str:
    chars = string.ascii_uppercase + string.digits
    parts = ["".join(random.choices(chars, k=4)) for _ in range(3)]
    return f"RPT-{parts[0]}-{parts[1]}-{parts[2]}"


def _confidence_score(score: float) -> int:
    """
    score: 0-100 (probability * 100)
    Confidence = how far the prediction is from the 50% decision boundary,
    scaled to 0-100. A score of 2% or 98% both mean high model confidence;
    a score near 50% means the model is genuinely uncertain.
    """
    prob = score / 100
    return round(abs(prob - 0.5) * 2 * 100)


def create_pdf(report: dict, output_path: str, patient_name: str = "Patient") -> None:
    """
    report keys expected:
        score, risk, message, symptoms, care, values, date
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.6*cm, rightMargin=1.6*cm,
        topMargin=1.0*cm,  bottomMargin=1.0*cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    risk_level  = report.get("risk", "Unknown")
    rc          = _risk_color(risk_level)
    rc_bg       = RISK_BG.get(risk_level, LIGHT_GRAY)
    score       = report.get("score", 0)
    confidence  = _confidence_score(score)
    patient_id  = _gen_patient_id()
    report_id   = _gen_report_id()
    values      = report.get("values", [])
    age         = int(values[0]) if values else "—"
    sex         = "Male" if (values and values[1] == 1) else "Female" if values else "—"

    # ════════════════════════════════════════
    # HEADER BAND
    # ════════════════════════════════════════
    brand_style = ParagraphStyle(
        "brand", fontSize=20, fontName="Helvetica-Bold",
        textColor=NAVY, leading=24,
    )
    tag_style = ParagraphStyle(
        "tag", fontSize=8.5, textColor=MUTED_GRAY, leading=11,
    )

    header_left = [
        Paragraph('<font color="#d62839">&#9829; Cardio</font><font color="#1c2541">Care</font>', brand_style),
        Paragraph("AI Powered Heart Risk Assessment", tag_style),
    ]

    badge_style = ParagraphStyle(
        "badge", fontSize=8, fontName="Helvetica-Bold",
        textColor=WHITE, alignment=TA_CENTER, leading=10,
    )
    badge_inner = Table(
        [[Paragraph("AI GENERATED REPORT", badge_style)]],
        colWidths=[4.1*cm],
    )
    badge_inner.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), ACCENT_RED),
        ("ALIGN", (0,0), (0,0), "CENTER"),
        ("VALIGN", (0,0), (0,0), "MIDDLE"),
        ("ROUNDEDCORNERS", [14]),
        ("TOPPADDING", (0,0), (0,0), 6),
        ("BOTTOMPADDING", (0,0), (0,0), 6),
        ("LEFTPADDING", (0,0), (0,0), 6),
        ("RIGHTPADDING", (0,0), (0,0), 6),
    ]))

    header_table = Table(
        [[header_left, badge_inner]],
        colWidths=[12.7*cm, 4.3*cm],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3*cm))

    # ════════════════════════════════════════
    # PATIENT INFO CARD
    # ════════════════════════════════════════
    label_style = ParagraphStyle("lbl", fontSize=9, fontName="Helvetica-Bold", textColor=NAVY, leading=15)
    val_style   = ParagraphStyle("val", fontSize=9, textColor=TEXT_GRAY, leading=15)

    info_data = [
        [Paragraph("Patient ID", label_style), Paragraph(f": {patient_id}", val_style),
         Paragraph("Report Generated", label_style), Paragraph(f": {report.get('date', datetime.now().strftime('%d %B %Y, %H:%M'))}", val_style)],
        [Paragraph("Name", label_style), Paragraph(f": {patient_name}", val_style),
         Paragraph("Model Version", label_style), Paragraph(": CardioCare ML v1.0", val_style)],
        [Paragraph("Age / Sex", label_style), Paragraph(f": {age} Years / {sex}", val_style),
         Paragraph("Report ID", label_style), Paragraph(f": {report_id}", val_style)],
    ]

    info_table = Table(info_data, colWidths=[3.0*cm, 5.6*cm, 3.6*cm, 5.3*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_GRAY),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (0,-1), 14),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.35*cm))

    # ════════════════════════════════════════
    # RISK OVERVIEW — 3 CARDS
    # ════════════════════════════════════════
    section_h_style = ParagraphStyle(
        "sectionH", fontSize=11, fontName="Helvetica-Bold",
        textColor=NAVY, alignment=TA_CENTER, spaceAfter=10,
    )
    story.append(Paragraph("RISK OVERVIEW", section_h_style))

    card_label_style = ParagraphStyle("cardLbl", fontSize=8, fontName="Helvetica-Bold", textColor=MUTED_GRAY, alignment=TA_CENTER, leading=11)
    card_big_style   = ParagraphStyle("cardBig", fontSize=17, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=21)
    card_sub_style   = ParagraphStyle("cardSub", fontSize=8, textColor=TEXT_GRAY, alignment=TA_CENTER, leading=12)

    risk_card = [
        Paragraph("RISK LEVEL", card_label_style),
        Spacer(1, 4),
        Paragraph(risk_level.upper(), ParagraphStyle("rl", parent=card_big_style, textColor=rc)),
        Spacer(1, 4),
        Paragraph("Your heart health indicators<br/>are evaluated below.", card_sub_style),
    ]
    score_card = [
        Paragraph("AI RISK SCORE", card_label_style),
        Spacer(1, 4),
        Paragraph(f"{score:.1f}%", ParagraphStyle("sc", parent=card_big_style, textColor=BLUE)),
        Spacer(1, 4),
        Paragraph("Probability of heart disease", card_sub_style),
    ]
    conf_card = [
        Paragraph("MODEL CONFIDENCE", card_label_style),
        Spacer(1, 4),
        Paragraph(f"{confidence}%", ParagraphStyle("cf", parent=card_big_style, textColor=PURPLE)),
        Spacer(1, 4),
        Paragraph("Certainty in this prediction", card_sub_style),
    ]

    overview_table = Table([[risk_card, score_card, conf_card]], colWidths=[5.83*cm, 5.83*cm, 5.83*cm], spaceBefore=0, spaceAfter=0)
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), rc_bg),
        ("BACKGROUND", (1,0), (1,0), BLUE_BG),
        ("BACKGROUND", (2,0), (2,0), PURPLE_BG),
        ("LINEABOVE", (0,0), (0,0), 1.2, rc),
        ("LINEABOVE", (1,0), (1,0), 1.2, BLUE),
        ("LINEABOVE", (2,0), (2,0), 1.2, PURPLE),
        ("TOPPADDING", (0,0), (-1,-1), 11),
        ("BOTTOMPADDING", (0,0), (-1,-1), 11),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 0.35*cm))

    # ════════════════════════════════════════
    # AI SUMMARY + RECOMMENDED CARE (2 col)
    # ════════════════════════════════════════
    box_title_style = ParagraphStyle("boxTitle", fontSize=10.5, fontName="Helvetica-Bold", textColor=NAVY, leading=14)
    body_style      = ParagraphStyle("body", fontSize=9, textColor=TEXT_GRAY, leading=14)
    bullet_style    = ParagraphStyle("bul", fontSize=9, textColor=TEXT_GRAY, leading=14, leftIndent=4)

    summary_block = [
        Paragraph("AI HEALTH SUMMARY", box_title_style),
        Spacer(1, 8),
        Paragraph(report.get("message", ""), body_style),
    ]

    care_rows = [[Paragraph(f"•  {tip}", bullet_style)] for tip in report.get("care", [])[:5]]
    care_block = [
        Paragraph("RECOMMENDED CARE &amp; ACTIONS", box_title_style),
        Spacer(1, 8),
    ] + [Paragraph(f"•  {tip}", bullet_style) for tip in report.get("care", [])[:5]]

    two_col = Table([[summary_block, care_block]], colWidths=[8.2*cm, 8.2*cm])
    two_col.setStyle(TableStyle([
        ("BOX", (0,0), (0,0), 0.75, MID_GRAY),
        ("BOX", (1,0), (1,0), 0.75, MID_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(two_col)
    story.append(Spacer(1, 0.28*cm))

    # ════════════════════════════════════════
    # HEALTH INDICATORS (full width)
    # ════════════════════════════════════════
    sym_rows = [Paragraph(f"✓  {s}", bullet_style) for s in report.get("symptoms", [])[:5]]
    sym_block_content = [
        Paragraph("HEALTH INDICATORS", box_title_style),
        Spacer(1, 8),
    ] + sym_rows

    sym_table = Table([[sym_block_content]], colWidths=[16.6*cm])
    sym_table.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.75, MID_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(sym_table)
    story.append(Spacer(1, 0.3*cm))

    # ════════════════════════════════════════
    # PATIENT INPUT PARAMETERS — 2 col table
    # ════════════════════════════════════════
    story.append(Paragraph("PATIENT INPUT PARAMETERS", box_title_style))
    story.append(Spacer(1, 6))

    labels = [
        "Age", "Sex (1=M/0=F)", "Chest Pain Type", "Resting BP (mmHg)",
        "Cholesterol (mg/dl)", "Fasting BS > 120", "Resting ECG",
        "Max Heart Rate", "Exercise Angina", "ST Depression",
        "Slope of ST", "Major Vessels (0-3)", "Thalassemia",
    ]

    half = 7  # left=7 rows, right=6 rows, pad right to 7
    left_labels = labels[:half]
    left_vals   = [str(v) for v in values[:half]]
    right_labels = labels[half:] + [""]          # pad to 7
    right_vals   = [str(v) for v in values[half:]] + [""]  # pad to 7

    th  = ParagraphStyle("th",  fontSize=8.5, fontName="Helvetica-Bold", textColor=WHITE, leading=12)
    td  = ParagraphStyle("td",  fontSize=8.5, textColor=TEXT_GRAY, leading=12)
    tdg = ParagraphStyle("tdg", fontSize=8.5, textColor=TEXT_GRAY, leading=12)

    # 5 columns: LParam | LVal | gap | RParam | RVal — ALL 8 rows built uniformly
    # Header row and every data row have exactly 5 cells — no mismatch possible
    def P(text, style): return Paragraph(text, style) if text else ""

    tbl_rows = [
        [P("Parameter",th), P("Value",th), "", P("Parameter",th), P("Value",th)]
    ]
    for i in range(7):
        ll = left_labels[i]  if i < len(left_labels)  else ""
        lv = left_vals[i]    if i < len(left_vals)    else ""
        rl = right_labels[i] if i < len(right_labels) else ""
        rv = right_vals[i]   if i < len(right_vals)   else ""
        tbl_rows.append([P(ll,td), P(lv,tdg), "", P(rl,td), P(rv,tdg)])

    # colWidths: LParam=4.5 LVal=2.6 gap=0.5 RParam=4.5 RVal=2.6 = 14.7cm (fits in 16.6 page width - margins)
    param_table = Table(tbl_rows, colWidths=[4.5*cm, 2.6*cm, 0.5*cm, 4.5*cm, 2.6*cm])
    param_table.setStyle(TableStyle([
        # Header backgrounds
        ("BACKGROUND", (0,0), (1,0), NAVY),
        ("BACKGROUND", (3,0), (4,0), NAVY),
        # Row backgrounds - left half
        ("ROWBACKGROUNDS", (0,1), (1,-1), [WHITE, LIGHT_GRAY]),
        # Row backgrounds - right half (only first 6 data rows, last is padding)
        ("ROWBACKGROUNDS", (3,1), (4,7), [WHITE, LIGHT_GRAY]),
        # Grid - left half
        ("GRID", (0,0), (1,-1), 0.4, MID_GRAY),
        # Grid - right half (only first 6 data rows)
        ("GRID", (3,0), (4,7), 0.4, MID_GRAY),
        # hide padding row on right (row 7, index 7 = last)
        ("BACKGROUND", (3,7), (4,7), WHITE),
        ("GRID", (3,7), (4,7), 0, WHITE),
        # Consistent padding everywhere
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        # Gap column - no background, no grid
        ("BACKGROUND", (2,0), (2,-1), WHITE),
    ]))
    story.append(param_table)
    story.append(Spacer(1, 0.2*cm))

    # ════════════════════════════════════════
    # DISCLAIMER FOOTER
    # ════════════════════════════════════════
    disc_title_style = ParagraphStyle("discTitle", fontSize=9, fontName="Helvetica-Bold", textColor=NAVY, leading=13)
    disc_body_style  = ParagraphStyle("discBody", fontSize=8, textColor=TEXT_GRAY, leading=12)
    thanks_style     = ParagraphStyle("thanks", fontSize=9, textColor=ACCENT_RED, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=13)

    disclaimer_content = [
        Paragraph(
            '<b>Disclaimer:</b> This report is generated by an AI model for informational purposes only. '
            'It is NOT a substitute for professional medical advice, diagnosis, or treatment. '
            'Always consult a qualified healthcare provider.',
            disc_body_style
        )
    ]
    thanks_content = [
        Paragraph("Thank you for taking", ParagraphStyle("t1", fontSize=9, textColor=TEXT_GRAY, alignment=TA_CENTER)),
        Paragraph("care of your heart!", thanks_style),
    ]

    footer_table = Table([[disclaimer_content, thanks_content]], colWidths=[11.8*cm, 4.8*cm])
    footer_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GREEN_BG),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS", [8]),
        ("LINEAFTER", (0,0), (0,0), 0.5, MID_GRAY),
    ]))
    story.append(KeepTogether(footer_table))

    doc.build(story)