import os
import cloudinary
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Force load .env from the backend directory
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Configure Cloudinary once at startup
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)

# Import blueprints AFTER env is loaded
from routes.auth import auth_bp
from routes.incidents import incidents_bp
from routes.session import session_bp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "ironcrate-dev-secret")

CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

app.register_blueprint(auth_bp,      url_prefix="/api/auth")
app.register_blueprint(incidents_bp, url_prefix="/api/incidents")
app.register_blueprint(session_bp,   url_prefix="/api/session")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
