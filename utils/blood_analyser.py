"""
Analyses uploaded blood report (PDF or image) using Gemini Vision.
Extracts heart-relevant values and flags abnormal ones.
"""

import json
import base64
import urllib.request
import re

from config import GEMINI_API_KEY, GEMINI_MODEL


ANALYSIS_PROMPT = """
You are a medical AI assistant.

Analyse this blood report image/pdf.

Return ONLY valid JSON.
No markdown.
No explanation outside JSON.

JSON format:

[
 {
  "test":"Total Cholesterol",
  "value":"240",
  "unit":"mg/dL",
  "normal_range":"<200 mg/dL",
  "status":"high",
  "heart_relevant":true,
  "explanation":"Short explanation"
 }
]

Rules:
- Escape all special characters.
- Do not use line breaks inside JSON strings.
- status values only:
normal, borderline, high, low, critical

Heart relevant true for:
cholesterol,
LDL,
HDL,
VLDL,
triglycerides,
glucose,
HbA1c,
blood pressure,
CRP,
homocysteine,
haemoglobin,
creatinine,
uric acid

Everything else false.
"""


def _encode_file(file_bytes, mime_type):

    encoded = base64.b64encode(
        file_bytes
    ).decode("utf-8")

    return {

        "inline_data": {

            "mime_type": mime_type,

            "data": encoded

        }

    }



def clean_gemini_json(raw):

    raw = raw.strip()


    # remove ```json wrappers

    raw = re.sub(
        r"```json",
        "",
        raw
    )


    raw = raw.replace(
        "```",
        ""
    )


    # find array

    match = re.search(
        r"\[.*\]",
        raw,
        re.DOTALL
    )


    if match:

        raw = match.group()


    return raw.strip()




def analyse_blood_report(file_bytes, mime_type):


    if not GEMINI_API_KEY:

        return {

            "error":"Gemini API key missing",

            "heart_relevant":[],

            "other":[]

        }



    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )



    payload = json.dumps({


        "contents":[

            {

                "role":"user",

                "parts":[

                    _encode_file(
                        file_bytes,
                        mime_type
                    ),

                    {
                        "text":ANALYSIS_PROMPT
                    }

                ]

            }

        ],


        "generationConfig":{

            "temperature":0,

            "maxOutputTokens":3000,

            "response_mime_type":
            "application/json"

        }


    }).encode("utf-8")



    try:


        request = urllib.request.Request(

            url,

            data=payload,

            headers={

                "Content-Type":
                "application/json"

            }

        )



        with urllib.request.urlopen(
            request,
            timeout=40
        ) as response:


            data=json.loads(

                response.read()
                .decode("utf-8")

            )



        raw = (

            data["candidates"][0]
            ["content"]
            ["parts"][0]
            ["text"]

        )


        print("====== GEMINI RAW ======")
        print(raw)



        try:

            items=json.loads(
                clean_gemini_json(raw)
            )


        except Exception:

            return {

                "error":
                "AI response formatting failed. Try again.",

                "heart_relevant":[],

                "other":[]

            }



        heart=[

            i for i in items

            if i.get(
                "heart_relevant"
            )

        ]


        other=[

            i for i in items

            if not i.get(
                "heart_relevant"
            )

        ]


        return {

            "heart_relevant":heart,

            "other":other,

            "error":None

        }



    except Exception as e:


        print(
            "[Blood Analyzer ERROR]",
            e
        )


        return {

            "error":
            f"Analysis failed: {e}",

            "heart_relevant":[],

            "other":[]

        }