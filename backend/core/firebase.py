"""
IronCrate — core/firebase.py
Centralised Firebase initialisation. Import `db` and `storage` from here.
"""
import os
import pyrebase

_config = {
    "apiKey":            os.getenv("FIREBASE_API_KEY"),
    "authDomain":        os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL":       os.getenv("FIREBASE_DATABASE_URL"),   # single authoritative key
    "projectId":         os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket":     os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId":             os.getenv("FIREBASE_APP_ID"),
}

# Validate the most critical key at startup
if not _config["databaseURL"]:
    raise ValueError(
        "CRITICAL: FIREBASE_DATABASE_URL is not set. "
        "Check your backend/.env file."
    )

_firebase = pyrebase.initialize_app(_config)
db      = _firebase.database()
storage = _firebase.storage()
