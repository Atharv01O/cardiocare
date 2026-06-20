"""
CardioCare Professional PDF Report Generator
Uses only ReportLab
pip install reportlab
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import cm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)

from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ===============================
# COLORS
# ===============================

PRIMARY_RED = colors.HexColor("#C0392B")
DARK_TEXT   = colors.HexColor("#2C3E50")
LIGHT_BG    = colors.HexColor("#F4F6F7")

GREEN       = colors.HexColor("#27AE60")
ORANGE      = colors.HexColor("#E67E22")
RED         = colors.HexColor("#E74C3C")

WHITE       = colors.white


RISK_COLORS = {
    "Low Risk": GREEN,
    "Moderate Risk": ORANGE,
    "High Risk": RED
}


def risk_color(level):
    return RISK_COLORS.get(level, DARK_TEXT)



# ===============================
# PDF GENERATOR
# ===============================

def create_pdf(report: dict, output_path: str):

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )


    doc = SimpleDocTemplate(

        output_path,

        pagesize=A4,

        leftMargin=1.8*cm,
        rightMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm

    )


    styles = getSampleStyleSheet()

    story = []



    # ===============================
    # HEADER
    # ===============================


    title_style = ParagraphStyle(

        "title",

        parent=styles["Normal"],

        alignment=TA_CENTER,

        fontSize=24,

        textColor=PRIMARY_RED,

        spaceAfter=8

    )


    story.append(
        Paragraph(
            """
            <b>CardioCare</b><br/>
            <font size='11' color='#566573'>
            AI Powered Heart Risk Assessment Report
            </font>
            """,
            title_style
        )
    )


    story.append(
        Paragraph(
            f"""
            <para align='center'>
            Generated: 
            {report.get(
                "date",
                datetime.now().strftime("%d-%m-%Y %H:%M")
            )}
            </para>
            """,
            styles["Normal"]
        )
    )


    story.append(Spacer(1,0.4*cm))



    # ===============================
    # AI BADGE
    # ===============================


    badge = Table(
        [["AI GENERATED REPORT"]],
        colWidths=[5*cm]
    )


    badge.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,-1),PRIMARY_RED),

        ("TEXTCOLOR",(0,0),(-1,-1),WHITE),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),

        ("PADDING",(0,0),(-1,-1),8),

    ]))


    story.append(badge)

    story.append(Spacer(1,0.5*cm))





    # ===============================
    # RISK SUMMARY CARDS
    # ===============================


    risk = report.get(
        "risk",
        "Unknown"
    )


    score = report.get(
        "score",
        0
    )


    rc = risk_color(risk)



    risk_cards = Table(

        [

            [

                Paragraph(
                    f"""
                    <b>Risk Category</b>
                    <br/><br/>

                    <font size='18'
                    color='{rc.hexval()}'>
                    {risk}
                    </font>
                    """,

                    styles["Normal"]

                ),



                Paragraph(

                    f"""
                    <b>AI Risk Probability</b>
                    <br/><br/>

                    <font size='18'>
                    {score:.1f} %
                    </font>

                    """,

                    styles["Normal"]

                )

            ]

        ],


        colWidths=[8*cm,8*cm]

    )



    risk_cards.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,-1),LIGHT_BG),

        ("BOX",(0,0),(-1,-1),1,colors.lightgrey),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("PADDING",(0,0),(-1,-1),18),

    ]))



    story.append(risk_cards)

    story.append(Spacer(1,0.5*cm))





    # ===============================
    # AI SUMMARY
    # ===============================


    section_style = ParagraphStyle(

        "section",

        parent=styles["Heading2"],

        fontSize=13,

        textColor=PRIMARY_RED,

        spaceBefore=10

    )



    normal = ParagraphStyle(

        "normal",

        parent=styles["Normal"],

        fontSize=10,

        textColor=DARK_TEXT,

        leading=15

    )



    def section(name):

        story.append(
            Paragraph(
                name,
                section_style
            )
        )

        story.append(

            HRFlowable(
                width="100%",
                thickness=0.5,
                color=colors.lightgrey
            )

        )

        story.append(
            Spacer(1,0.15*cm)
        )



    section("AI Health Summary")


    story.append(

        Paragraph(

            report.get(
                "message",
                "No summary available"
            ),

            normal

        )

    )






    # ===============================
    # SYMPTOMS
    # ===============================


    section("Health Indicators")


    for item in report.get(
        "symptoms",
        []
    ):

        story.append(

            Paragraph(
                f"✓ {item}",
                normal
            )

        )




    # ===============================
    # CARE
    # ===============================


    section(
        "Recommended Care Plan"
    )


    for item in report.get(
        "care",
        []
    ):


        story.append(

            Paragraph(

                f"✓ {item}",

                normal

            )

        )





    # ===============================
    # PATIENT DATA
    # ===============================


    section(
        "Patient Input Parameters"
    )



    labels = [

        "Age",
        "Sex (1=M / 0=F)",
        "Chest Pain Type",
        "Resting BP",
        "Cholesterol",
        "Fasting Blood Sugar",
        "Resting ECG",
        "Max Heart Rate",
        "Exercise Angina",
        "ST Depression",
        "Slope",
        "Major Vessels",
        "Thalassemia"

    ]



    values = report.get(
        "values",
        []
    )



    data = [

        [
            "Parameter",
            "Value"
        ]

    ]



    for a,b in zip(labels,values):

        data.append(

            [
                a,
                str(b)
            ]

        )




    table = Table(

        data,

        colWidths=[10*cm,6*cm]

    )



    table.setStyle(TableStyle([


        ("BACKGROUND",(0,0),(-1,0),PRIMARY_RED),

        ("TEXTCOLOR",(0,0),(-1,0),WHITE),

        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),


        ("BACKGROUND",(0,1),(-1,-1),WHITE),


        ("LINEBELOW",(0,0),(-1,-1),
         0.4,
         colors.lightgrey),


        ("ALIGN",(1,0),(1,-1),"CENTER"),


        ("PADDING",(0,0),(-1,-1),8),

        ("FONTSIZE",(0,0),(-1,-1),9)


    ]))



    story.append(table)



    story.append(
        Spacer(1,0.6*cm)
    )





    # ===============================
    # DISCLAIMER
    # ===============================


    story.append(

        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.lightgrey
        )

    )



    disclaimer = ParagraphStyle(

        "disc",

        parent=styles["Normal"],

        fontSize=8,

        textColor=colors.grey,

        alignment=TA_CENTER,

        leading=12

    )



    story.append(

        Paragraph(

            """
            This report was generated using an AI prediction model.
            It is for informational purposes only and should not replace
            professional medical diagnosis or treatment.
            """,

            disclaimer

        )

    )



    doc.build(story)