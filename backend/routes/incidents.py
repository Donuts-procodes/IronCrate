from flask import Blueprint, request, jsonify
import hashlib
import cloudinary
import cloudinary.uploader
import pyrebase
import os
import tempfile
import uuid  # <-- Added for unique filenames
from utils.vision import DashcamAnalyzer

incidents_bp = Blueprint('incidents', __name__)
analyzer = DashcamAnalyzer()

# Initialize Firebase
firebase = pyrebase.initialize_app({
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DB_URL"),
    "storageBucket": "ironcrate-75923.firebasestorage.app"
})
db = firebase.database()

def generate_file_hash(filepath):
    """Generates SHA-256 for tamper evidence"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@incidents_bp.post('/upload')
def upload_incident():
    # 1. Auth check would go here
    
    driver_info = request.form.get('driver_info')
    own_speed_gps = request.form.get('speed') 
    location = request.form.get('location')
    
    front_cam = request.files.get('front_video')
    
    if not front_cam:
        return jsonify({"error": "Front video required"}), 400

    # 2. Save video temporarily to disk using a UNIQUE filename
    temp_dir = tempfile.gettempdir()
    unique_filename = f"temp_front_{uuid.uuid4().hex}.mp4" # <-- Fix applied here
    front_path = os.path.join(temp_dir, unique_filename)
    front_cam.save(front_path)
    
    try:
        # 3. Generate Tamper-Proof Hash
        front_hash = generate_file_hash(front_path)
        
        # 4. Run OpenCV Analysis
        print(f"Running OpenCV Analysis on {unique_filename}...")
        cv_results = analyzer.analyze_video(front_path)
        
        # 5. Upload to Cloudinary
        print("Uploading to Cloudinary...")
        upload_result = cloudinary.uploader.upload(front_path, resource_type="video")
        
        # 6. Construct Immutable Payload
        payload = {
            "driver_info": driver_info,
            "own_speed_kmh": own_speed_gps,
            "location_coords": location,
            "video_hash": front_hash,
            "video_url": upload_result['secure_url'],
            "ai_analysis": cv_results,
            "timestamp": {".sv": "timestamp"} # <-- Syntax Fix applied here
        }
        
        # 7. Save to Firebase Realtime Database
        db.child("incidents").push(payload)
        
    finally:
        # 8. Cleanup local file to prevent server storage overflow
        if os.path.exists(front_path):
            os.remove(front_path)

    return jsonify({
        "message": "Incident secured and analyzed",
        "data": payload
    }), 201