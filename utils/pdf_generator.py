"""
CardioCare Modern AI Report Generator
pip install reportlab
"""

import os
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# =====================
# COLORS
# =====================

RED = colors.HexColor("#C0392B")
GREEN = colors.HexColor("#27AE60")
BLUE = colors.HexColor("#1F3A68")
PURPLE = colors.HexColor("#6C3483")
ORANGE = colors.HexColor("#E67E22")

DARK = colors.HexColor("#1F2933")
GREY = colors.HexColor("#6B7280")
LIGHT = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#E5E7EB")


# =====================
# HELPERS
# =====================

def card(c, x, y, w, h):
    c.setFillColor(colors.white)
    c.setStrokeColor(BORDER)

    c.roundRect(
        x,
        y,
        w,
        h,
        radius=12,
        stroke=1,
        fill=1
    )


def text(c, value, x, y, size=10, color=DARK, bold=False):

    c.setFillColor(color)

    if bold:
        c.setFont(
            "Helvetica-Bold",
            size
        )
    else:
        c.setFont(
            "Helvetica",
            size
        )

    c.drawString(
        x,
        y,
        str(value)
    )


def center(c,value,x,y,size,color=DARK):

    c.setFont(
        "Helvetica-Bold",
        size
    )

    c.setFillColor(color)

    c.drawCentredString(
        x,
        y,
        value
    )



# =====================
# MAIN PDF
# =====================


def create_pdf(report, output_path):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )


    c = canvas.Canvas(
        output_path,
        pagesize=A4
    )


    width,height = A4


    # =====================
    # HEADER
    # =====================


    text(
        c,
        "♥ CardioCare",
        45,
        height-60,
        24,
        RED,
        True
    )


    text(
        c,
        "AI Powered Heart Risk Assessment",
        48,
        height-82,
        11,
        GREY
    )


    # badge

    c.setFillColor(RED)

    c.roundRect(
        330,
        height-70,
        160,
        25,
        6,
        fill=1,
        stroke=0
    )

    center(
        c,
        "AI GENERATED REPORT",
        410,
        height-62,
        9,
        colors.white
    )



    # =====================
    # PATIENT CARD
    # =====================

    card(
        c,
        40,
        height-165,
        515,
        65
    )


    text(
        c,
        "Patient ID:",
        70,
        height-125,
        9,
        DARK,
        True
    )


    text(
        c,
        "CC-2026-001",
        150,
        height-125
    )


    text(
        c,
        "Report Generated:",
        330,
        height-125,
        9,
        DARK,
        True
    )


    text(
        c,
        report.get(
            "date",
            datetime.now().strftime("%d-%m-%Y")
        ),
        440,
        height-125
    )


    text(
        c,
        "Model:",
        70,
        height-148,
        9,
        DARK,
        True
    )


    text(
        c,
        "CardioCare ML v1.0",
        150,
        height-148
    )



    # =====================
    # RISK OVERVIEW
    # =====================


    center(
        c,
        "RISK OVERVIEW",
        width/2,
        height-200,
        13
    )



    risk = report.get(
        "risk",
        "Unknown"
    )

    score = report.get(
        "score",
        0
    )


    # CARD 1

    card(
        c,
        40,
        height-310,
        155,
        85
    )

    center(
        c,
        "RISK LEVEL",
        117,
        height-250,
        9,
        GREEN
    )

    center(
        c,
        risk.upper(),
        117,
        height-285,
        18,
        GREEN
    )


    # CARD 2

    card(
        c,
        220,
        height-310,
        155,
        85
    )

    center(
        c,
        "AI RISK SCORE",
        297,
        height-250,
        9,
        BLUE
    )


    center(
        c,
        f"{score:.1f}%",
        297,
        height-285,
        22,
        BLUE
    )


    # CARD 3

    card(
        c,
        400,
        height-310,
        155,
        85
    )

    center(
        c,
        "CONFIDENCE",
        477,
        height-250,
        9,
        PURPLE
    )


    center(
        c,
        "92%",
        477,
        height-285,
        22,
        PURPLE
    )



    # =====================
    # SUMMARY
    # =====================


    card(
        c,
        40,
        height-430,
        230,
        90
    )


    text(
        c,
        "AI HEALTH SUMMARY",
        60,
        height-365,
        12,
        BLUE,
        True
    )


    text(
        c,
        report.get(
            "message",
            ""
        )[:70],
        60,
        height-390
    )



    # CARE CARD


    card(
        c,
        290,
        height-430,
        265,
        90
    )


    text(
        c,
        "RECOMMENDED CARE",
        310,
        height-365,
        12,
        BLUE,
        True
    )


    y = height-390

    for item in report.get("care",[])[:4]:

        text(
            c,
            "✓ "+item,
            310,
            y
        )

        y-=15



    # =====================
    # PARAMETERS
    # =====================


    card(
        c,
        40,
        95,
        515,
        260
    )


    text(
        c,
        "PATIENT INPUT PARAMETERS",
        60,
        330,
        12,
        BLUE,
        True
    )



    labels=[

        "Age",
        "Sex",
        "Chest Pain",
        "BP",
        "Cholesterol",
        "Max Heart Rate",
        "ST Depression",
        "Thalassemia"

    ]


    values = report.get(
        "values",
        []
    )


    y=300

    for a,b in zip(labels,values):

        text(
            c,
            a,
            70,
            y,
            9
        )

        text(
            c,
            b,
            250,
            y,
            9,
            DARK,
            True
        )

        y-=22



    # =====================
    # FOOTER
    # =====================


    c.setFillColor(LIGHT)

    c.roundRect(
        40,
        35,
        515,
        35,
        10,
        fill=1,
        stroke=0
    )


    text(
        c,
        "Disclaimer: AI generated report. Not a substitute for professional medical advice.",
        60,
        50,
        8,
        GREY
    )


    c.save()