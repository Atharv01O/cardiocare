"""
Auth helpers — password hashing and user management via MongoDB.
Uses werkzeug (bundled with Flask) for secure password hashing.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson import ObjectId
from config import MONGO_URI, MONGO_DB


_client     = MongoClient(MONGO_URI)
_db         = _client[MONGO_DB]
users_col   = _db["users"]

# Unique index on email
users_col.create_index("email", unique=True)


class User:
    """Minimal Flask-Login compatible user object."""

    def __init__(self, data: dict):
        self.id       = str(data["_id"])
        self.email    = data["email"]
        self.name     = data.get("name", data["email"].split("@")[0])
        self._data    = data

    # ── Flask-Login interface ──────────────────────────────────
    @property
    def is_authenticated(self): return True
    @property
    def is_active(self):        return True
    @property
    def is_anonymous(self):     return False
    def get_id(self):           return self.id


def create_user(email: str, password: str, name: str = "") -> tuple[bool, str]:
    """Returns (success, message)."""
    if users_col.find_one({"email": email.lower()}):
        return False, "An account with this email already exists."
    users_col.insert_one({
        "email":    email.lower().strip(),
        "name":     name.strip() or email.split("@")[0],
        "password": generate_password_hash(password),
    })
    return True, "Account created successfully."


def get_user_by_email(email: str, password: str):
    """Returns User object if credentials valid, else None."""
    data = users_col.find_one({"email": email.lower().strip()})
    if data and check_password_hash(data["password"], password):
        return User(data)
    return None


def get_user_by_id(user_id: str):
    """Used by Flask-Login user_loader."""
    try:
        data = users_col.find_one({"_id": ObjectId(user_id)})
        return User(data) if data else None
    except Exception:
        return None
