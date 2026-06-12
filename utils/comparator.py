"""
Compares two reports parameter-by-parameter.
Returns a list of dicts with delta info for the UI.
"""

FIELD_LABELS = {
    "age":      "Age",
    "sex":      "Sex",
    "cp":       "Chest Pain Type",
    "trestbps": "Resting Blood Pressure",
    "chol":     "Cholesterol",
    "fbs":      "Fasting Blood Sugar",
    "restecg":  "Resting ECG",
    "thalach":  "Max Heart Rate",
    "exang":    "Exercise Angina",
    "oldpeak":  "ST Depression",
    "slope":    "ST Slope",
    "ca":       "Major Vessels",
    "thal":     "Thalassemia",
}

# True = higher is BETTER for heart health, False = lower is better
HIGHER_IS_BETTER = {
    "thalach": True,   # Higher max HR is generally better
    "age":     False,  # Older = higher risk
    "trestbps":False,
    "chol":    False,
    "fbs":     False,
    "oldpeak": False,
    "ca":      False,
    "exang":   False,
    # categorical — no direction
    "sex":     None,
    "cp":      None,
    "restecg": None,
    "slope":   None,
    "thal":    None,
}


def compare_reports(new_report: dict, old_report: dict) -> dict:
    """
    new_report / old_report: MongoDB documents with a 'values' list
    Returns:
      {
        score_delta: float,
        rows: [ { label, old_val, new_val, delta, direction, good } ]
        new_score: float,
        old_score: float,
        new_risk: str,
        old_risk: str,
        new_date: str,
        old_date: str,
      }
    """

    fields     = list(FIELD_LABELS.keys())
    new_values = new_report.get("values", [])
    old_values = old_report.get("values", [])

    rows = []
    for i, key in enumerate(fields):
        label   = FIELD_LABELS[key]
        new_val = new_values[i] if i < len(new_values) else None
        old_val = old_values[i] if i < len(old_values) else None

        # Delta only for numeric fields
        try:
            delta = round(float(new_val) - float(old_val), 2)
        except (TypeError, ValueError):
            delta = None

        # Determine if change is good / bad / neutral
        hib = HIGHER_IS_BETTER.get(key)
        if delta is None or hib is None or delta == 0:
            good = "neutral"
        elif (delta > 0 and hib) or (delta < 0 and not hib):
            good = "good"
        else:
            good = "bad"

        direction = "up" if (delta or 0) > 0 else ("down" if (delta or 0) < 0 else "same")

        rows.append({
            "label":    label,
            "old_val":  old_val,
            "new_val":  new_val,
            "delta":    delta,
            "direction":direction,
            "good":     good,
        })

    new_score = float(new_report.get("score", 0))
    old_score = float(old_report.get("score", 0))

    return {
        "rows":      rows,
        "new_score": new_score,
        "old_score": old_score,
        "score_delta": round(new_score - old_score, 2),
        "new_risk":  new_report.get("risk", ""),
        "old_risk":  old_report.get("risk", ""),
        "new_date":  new_report.get("date", ""),
        "old_date":  old_report.get("date", ""),
    }
