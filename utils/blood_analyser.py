"""
Analyses uploaded blood report (PDF or image) using Gemini Vision.
Extracts heart-relevant values and flags abnormal ones.
"""

import json
import base64
import urllib.request
from config import GEMINI_API_KEY, GEMINI_MODEL

ANALYSIS_PROMPT = """You are a medical AI assistant. Analyse this blood test report and extract ALL test values present.

For each value found, return a JSON array like this (respond ONLY with valid JSON, no markdown):
[
  {
    "test": "Total Cholesterol",
    "value": "240",
    "unit": "mg/dL",
    "normal_range": "< 200 mg/dL",
    "status": "high",
    "heart_relevant": true,
    "explanation": "Your cholesterol is above the healthy limit. High cholesterol increases risk of arterial plaque and heart disease."
  }
]

Status must be one of: "normal", "borderline", "high", "low", "critical"
heart_relevant must be true for: cholesterol, triglycerides, blood sugar/glucose, HbA1c, blood pressure, CRP, homocysteine, LDL, HDL, VLDL, haemoglobin, creatinine, uric acid
heart_relevant = false for everything else (thyroid, liver enzymes, vitamins, etc.)

Be specific with the explanation for heart_relevant=true items. Keep explanations to 1-2 sentences."""


def _encode_file(file_bytes: bytes, mime_type: str) -> dict:
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return {"inline_data": {"mime_type": mime_type, "data": b64}}


def analyse_blood_report(file_bytes: bytes, mime_type: str) -> dict:
    """
    Sends file to Gemini Vision and returns structured analysis.
    Returns: { heart_relevant: [...], other: [...], error: str|None }
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return {"error": "Gemini API key not configured.", "heart_relevant": [], "other": []}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    payload = json.dumps({
        "contents": [{
            "role": "user",
            "parts": [
                _encode_file(file_bytes, mime_type),
                {"text": ANALYSIS_PROMPT}
            ]
        }],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2000}
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        items = json.loads(raw.strip())

        heart  = [i for i in items if i.get("heart_relevant")]
        other  = [i for i in items if not i.get("heart_relevant")]
        return {"heart_relevant": heart, "other": other, "error": None}

    except Exception as e:
        print(f"[Blood Analyser] Error: {e}")
        return {"error": f"Analysis failed: {str(e)}", "heart_relevant": [], "other": []}
