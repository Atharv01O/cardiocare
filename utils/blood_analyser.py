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

Extract EVERY test value visible.

Return ONLY valid JSON.
No markdown.
No text outside JSON.

Return format:
[
{
"test":"Total Cholesterol",
"value":"245",
"unit":"mg dL",
"normal_range":"below 200 mg dL",
"status":"high",
"heart_relevant":true,
"explanation":"Cholesterol value is higher than normal"
}
]

Rules:
- JSON must start with [ and end with ]
- Use double quotes only
- No trailing commas
- No newline characters inside values
- Use proper medical units like mg/dL, %, g/dL
- Escape JSON special characters correctly
- Use plain text units like mg dL
- Explanation maximum 15 words
- Explain the health meaning, not just whether value is high or low

Status options:
normal
borderline
high
low
critical

heart_relevant true ONLY:
cholesterol
LDL
HDL
VLDL
triglycerides
glucose
blood sugar
HbA1c
blood pressure
CRP
homocysteine
haemoglobin
creatinine
uric acid
ferritin
troponin

Medical interpretation:
- High LDL is bad
- High triglycerides are bad
- High HDL is usually protective
- Low HDL increases heart risk
- High glucose and HbA1c indicate diabetes risk

Everything else heart_relevant false.
"""

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
# Resize large images to reduce payload size
    if mime_type in ("image/jpeg", "image/png", "image/jpg"):
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(file_bytes))
            img.thumbnail((1200, 1600))  # max dimensions
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            file_bytes = buf.getvalue()
            mime_type = "image/jpeg"
        except Exception:
            pass  # use original if PIL fails
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
            "maxOutputTokens": 4096,
        },
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        print("🚀 CALLING GEMINI ONCE", flush=True)

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                 print("✅ GEMINI RESPONDED", flush=True)
                 data = json.loads(resp.read().decode("utf-8"))

        except Exception as e:
            print("🔥 GEMINI REQUEST FAILED:", repr(e), flush=True)
            raise e
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        print("====== GEMINI RAW ======", flush=True)
        print(raw, flush=True)
        # Extract and parse the JSON array
        json_str = _extract_json_array(raw)

        try:
            items = json.loads(json_str)

        except json.JSONDecodeError:
            print("❌ BAD GEMINI JSON:", json_str[:1000], flush=True)

            cleaned = re.sub(r"[\x00-\x1F]+", " ", json_str)
            cleaned = re.sub(r",\s*]", "]", cleaned)
            cleaned = re.sub(r",\s*}", "}", cleaned)

            items = json.loads(cleaned)

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
        error_body = e.read().decode("utf-8")
        print("🔥 GEMINI HTTP ERROR:", e.code, error_body, flush=True)

        if e.code == 429:
            return {
                "error": "Gemini busy. Try again in a minute.",
                "heart_relevant": [],
                "other": [],
            }

        return {
            "error": f"Gemini failed with code {e.code}",
            "heart_relevant": [],
            "other": [],
        }


    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "error": f"Analysis failed: {str(e)}",
            "heart_relevant": [],
            "other": [],
        }