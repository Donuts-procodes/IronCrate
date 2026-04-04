"""
IronCrate - Secure Dashcam Backend
"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "super-secret-key")

# Enable CORS for the React frontend
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# Register Blueprints (Routes)
from routes.auth import auth_bp
from routes.incidents import incidents_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(incidents_bp, url_prefix="/api/incidents")

@app.get("/api/health")
def health():
    return {"status": "IronCrate Secure Backend Active"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)