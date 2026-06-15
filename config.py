import os

# =========================
# BASE PATHS
# =========================

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH  = os.path.join(BASE_DIR, "model", "heart_model.h5")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")
DATASET_PATH= os.path.join(BASE_DIR, "dataset", "heart.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# =========================
# MONGODB
# =========================

from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB  = "cardiocare"
MONGO_COL = "reports"

# =========================
# APP
# =========================

DEBUG      = True
SECRET_KEY = "cardiocare-secret-2024"

# =========================
# GEMINI API
# =========================

GEMINI_API_KEY = ""
GEMINI_MODEL = "gemini-2.5-flash"