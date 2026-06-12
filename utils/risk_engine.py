"""
Maps a prediction probability (0-100 score) to:
  - risk level
  - message
  - symptoms list
  - care tips list
  - color class for UI
"""


def analyze_risk(score: float) -> dict:
    """
    score: 0 – 100  (probability × 100)
    """

    if score < 30:
        return {
            "level"   : "Low Risk",
            "color"   : "green",
            "icon"    : "✅",
            "message" : (
                "Your indicators suggest a low likelihood of heart disease. "
                "Maintain your healthy habits."
            ),
            "symptoms": [
                "No significant warning signs detected",
                "Heart rate within normal range",
                "Blood pressure appears controlled",
            ],
            "care"    : [
                "Continue regular aerobic exercise (30 min/day)",
                "Maintain a balanced, low-sodium diet",
                "Schedule annual heart check-ups",
                "Avoid smoking and limit alcohol",
                "Manage stress through sleep and relaxation",
            ],
        }

    elif score < 60:
        return {
            "level"   : "Moderate Risk",
            "color"   : "orange",
            "icon"    : "⚠️",
            "message" : (
                "Some indicators suggest moderate cardiovascular risk. "
                "Consult a cardiologist and review your lifestyle."
            ),
            "symptoms": [
                "Possible occasional chest discomfort or tightness",
                "Mild shortness of breath on exertion",
                "Elevated cholesterol or blood pressure levels",
                "Fatigue more than usual",
            ],
            "care"    : [
                "See a doctor for a full cardiac evaluation",
                "Reduce saturated fats and processed foods",
                "Start a supervised exercise routine",
                "Monitor blood pressure and cholesterol regularly",
                "Reduce BMI if overweight",
                "Limit caffeine and alcohol intake",
            ],
        }

    else:
        return {
            "level"   : "High Risk",
            "color"   : "red",
            "icon"    : "🚨",
            "message" : (
                "Your indicators suggest a high risk of heart disease. "
                "Please seek immediate medical consultation."
            ),
            "symptoms": [
                "Chest pain, pressure, or squeezing sensation",
                "Severe shortness of breath",
                "Pain radiating to arm, neck, or jaw",
                "Dizziness or sudden cold sweats",
                "Irregular heartbeat (palpitations)",
                "Swelling in legs or ankles",
            ],
            "care"    : [
                "Consult a cardiologist IMMEDIATELY",
                "Do not ignore chest pain — go to emergency if needed",
                "Take prescribed medications without skipping",
                "Follow a strict heart-healthy diet (DASH diet)",
                "Complete bed rest and avoid strenuous activity",
                "Daily monitoring of blood pressure and pulse",
                "Stop smoking completely",
            ],
        }
