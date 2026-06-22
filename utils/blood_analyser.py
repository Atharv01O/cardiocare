"""
Analyses uploaded blood report (PDF or image) using Gemini Vision.
Extracts heart-relevant values and flags abnormal ones.
"""

import os
import json
import base64
import urllib.request
import re

from config import GEMINI_API_KEY, GEMINI_MODEL


ANALYSIS_PROMPT = """You are a medical AI assistant analysing a blood test report.

Extract EVERY test value visible in this report.

Return ONLY a valid JSON array. No text before or after. No markdown. Start with [ end with ].

Each item must follow this exact format:
[
  {
    "test": "Total Cholesterol",
    "value": "245",
    "unit": "mg/dL",
    "normal_range": "< 200 mg/dL",
    "status": "high",
    "heart_relevant": true,
    "explanation": "Your cholesterol of 245 mg/dL is above the healthy limit of 200. This increases risk of arterial plaque."
  }
]

Status must be exactly one of: normal, borderline, high, low, critical

Set heart_relevant to true ONLY for:
cholesterol, LDL, HDL, VLDL, triglycerides, glucose, blood sugar, HbA1c,
blood pressure, systolic, diastolic, CRP, homocysteine, haemoglobin,
creatinine, uric acid, fibrinogen, ferritin, troponin

Set heart_relevant to false for everything else (thyroid, vitamins, liver enzymes, WBC, platelets etc.)

Rules:
- Extract ALL tests visible, not just heart-related ones
- Keep explanation to 1-2 sentences, specific to the actual value
- Do not use newlines inside string values
- Escape any special characters in strings"""


def _encode_file(file_bytes: bytes, mime_type: str) -> dict:
    return {
        "inline_data": {
            "mime_type": mime_type,
            "data": base64.b64encode(file_bytes).decode("utf-8"),
        }
    }


def _extract_json_array(raw: str) -> str:
    """Robustly extract a JSON array from Gemini's response."""

    raw = raw.strip()

    # Strip markdown fences if present
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()

    # If it already starts with [ we're good
    if raw.startswith("["):
        return raw

    # Find the outermost [ ... ] array
    start = raw.find("[")
    if start == -1:
        raise ValueError("No JSON array found in response")

    # Walk forward to find the matching closing bracket
    depth   = 0
    in_str  = False
    escape  = False
    end_idx = -1

    for i, ch in enumerate(raw[start:], start):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_str:
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end_idx = i
                break

    if end_idx == -1:
        raise ValueError("Unmatched brackets in JSON response")

    return raw[start : end_idx + 1]


def analyse_blood_report(file_bytes: bytes, mime_type: str) -> dict:

    if not GEMINI_API_KEY:
        return {
            "error": "Gemini API key not configured.",
            "heart_relevant": [],
            "other": [],
        }

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    # NOTE: do NOT include response_mime_type for vision/multimodal requests —
    # it conflicts with image input and causes Gemini 2.5 to return malformed output
    payload = json.dumps({
        "contents": [{
            "role": "user",
            "parts": [
                _encode_file(file_bytes, mime_type),
                {"text": ANALYSIS_PROMPT},
            ],
        }],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 3000,
        },
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        print("====== GEMINI RAW ======")
        print(raw[:500])

        # Extract and parse the JSON array
        json_str = _extract_json_array(raw)
        items    = json.loads(json_str)

        if not isinstance(items, list):
            raise ValueError("Response is not a JSON array")

        heart = [i for i in items if i.get("heart_relevant")]
        other = [i for i in items if not i.get("heart_relevant")]

        return {"heart_relevant": heart, "other": other, "error": None}

    except json.JSONDecodeError as e:
        print(f"[Blood Analyser] JSON parse error: {e}")
        return {
            "error": "AI response formatting failed. Try again.",
            "heart_relevant": [],
            "other": [],
        }
  
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {
                "error": "Too many requests — please wait 30 seconds and try again.",
                "heart_relevant": [],
                "other": [],
            }
        print(f"[Blood Analyser ERROR] {e}")
        return {
            "error": f"Analysis failed: {e}",
            "heart_relevant": [],
            "other": [],
        }
    except Exception as e:
        print(f"[Blood Analyser ERROR] {e}")
        return {
            "error": f"Analysis failed: {e}",
            "heart_relevant": [],
            "other": [],
        }