"""
IronCrate - Flask Backend
Run: python app.py
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

from routes.auth import auth_bp
from routes.session import session_bp
from routes.incidents import incidents_bp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "ironcrate-dev-secret")

CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

app.register_blueprint(auth_bp,      url_prefix="/api/auth")
app.register_blueprint(session_bp,   url_prefix="/api/session")
app.register_blueprint(incidents_bp, url_prefix="/api/incidents")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "IronCrate"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
