"""
IronCrate - Firebase Core Helper
Wraps pyrebase4 for DB and Storage access.
"""

import os
import pyrebase

_CONFIG = {
    "apiKey":        os.getenv("FIREBASE_API_KEY"),
    "authDomain":    os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL":   os.getenv("FIREBASE_DB_URL"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "serviceAccount": os.getenv("FIREBASE_SERVICE_ACCOUNT", ""),
}

_firebase = pyrebase.initialize_app(_CONFIG)

db      = _firebase.database()
_store  = _firebase.storage()


class _Storage:
    """Thin wrapper that uploads bytes and returns a public URL."""

    def upload(self, data: bytes, path: str, content_type: str = "video/webm") -> str:
        import tempfile, os as _os
        # pyrebase needs a file path, so write to a temp file first
        suffix = "." + content_type.split("/")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name

        try:
            _store.child(path).put(tmp_path)
            url = _store.child(path).get_url(None)
        finally:
            _os.unlink(tmp_path)

        return url


storage = _Storage()
