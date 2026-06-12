"""
Gemini chat endpoint for the CardioCare floating assistant.
Maintains conversation context within a session.
"""

import json
import urllib.request
from config import GEMINI_API_KEY, GEMINI_MODEL

SYSTEM_CONTEXT = """You are CardioCare Assistant, a friendly cardiology helper inside a heart disease risk prediction app.
Rules:
- Keep responses SHORT (2-4 sentences max unless asked for more)
- Be warm and friendly, not clinical
- Always remind users to consult a real doctor for medical decisions
- Never diagnose — only educate and guide
- If report context is provided, use it to give specific answers about that patient\'s results"""


def build_system_message(report_context: dict = None) -> str:
    base = SYSTEM_CONTEXT
    if not report_context:
        return base
    ctx = f"""

The user just received their heart disease risk assessment. Here are their results:
- Risk Level: {report_context.get("risk", "Unknown")}
- Risk Score: {report_context.get("score", 0):.1f} / 100
- Age: {report_context.get("age", "?")} | Sex: {report_context.get("sex", "?")}
- Cholesterol: {report_context.get("chol", "?")} mg/dl | Blood Pressure: {report_context.get("trestbps", "?")} mmHg
- Max Heart Rate: {report_context.get("thalach", "?")} bpm | ST Depression: {report_context.get("oldpeak", "?")}
- Exercise Angina: {"Yes" if report_context.get("exang") else "No"} | Major Vessels: {report_context.get("ca", "?")}
- Chest Pain Type: {report_context.get("cp_label", "?")} | Thalassemia: {report_context.get("thal_label", "?")}

When the user asks about their report, results, risk, or any of these values — answer specifically about THIS patient\'s data.
If asked "is my report bad" or "should I be worried", give an honest, caring assessment based on the score and risk level above."""
    return base + ctx


def chat_with_gemini(messages: list, report_context: dict = None) -> str:
    """
    messages: list of {role: 'user'|'model', text: str}
    report_context: optional dict with latest prediction data
    Returns assistant reply string.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "Please add your Gemini API key in config.py to enable the chat assistant."

    system_msg = build_system_message(report_context)

    # Build contents array with system context prepended to first user message
    contents = []
    for i, msg in enumerate(messages):
        role = "user" if msg["role"] == "user" else "model"
        text = msg["text"]
        if i == 0 and role == "user":
            text = f"{system_msg}\n\nUser question: {text}"
        contents.append({"role": role, "parts": [{"text": text}]})

    url     = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = json.dumps({
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 400,
        }
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"[Gemini Chat] Error: {e}")
        return "Sorry, I couldn't reach the AI assistant right now. Please try again."
