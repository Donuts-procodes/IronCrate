import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# 1. LOAD DOTENV FIRST
load_dotenv()

# 2. NOW IMPORT ROUTES (after environment variables exist)
from routes.auth import auth_bp
from routes.incidents import incidents_bp

app = Flask(__name__)
# ... the rest of your app.py code
app.secret_key = os.getenv("FLASK_SECRET", "super-secret-key")

# Enable CORS for the React frontend
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# Register Blueprints (Routes)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(incidents_bp, url_prefix="/api/incidents")

@app.get("/api/health")
def health():
    return {"status": "IronCrate Secure Backend Active"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)