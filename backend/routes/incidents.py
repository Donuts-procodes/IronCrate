import os
import hashlib
import tempfile
import uuid
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify

# 1. IMPORT ONLY WHAT YOU NEED FROM YOUR CONFIG
# Note: 'from config import db' assumes config.py is in the same folder as app.py
from config import db 
from utils.vision import DashcamAnalyzer

incidents_bp = Blueprint('incidents', __name__)
analyzer = DashcamAnalyzer()

# 2. CONFIGURE CLOUDINARY (Since it's not in your config.py)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def generate_file_hash(filepath):
    """Generates SHA-256 for tamper evidence"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@incidents_bp.post('/upload')
def upload_incident():
    # Fetch form data
    driver_info = request.form.get('driver_info')
    own_speed_gps = request.form.get('speed') 
    location = request.form.get('location')
    front_cam = request.files.get('front_video')
    
    if not front_cam:
        return jsonify({"error": "Front video required"}), 400

    # Create a unique temporary path
    temp_dir = tempfile.gettempdir()
    unique_filename = f"temp_front_{uuid.uuid4().hex}.mp4"
    front_path = os.path.join(temp_dir, unique_filename)
    
    try:
        # Save file to temp disk
        front_cam.save(front_path)
        
        # 3. Generate Tamper-Proof Hash
        front_hash = generate_file_hash(front_path)
        
        # 4. Run OpenCV Analysis
        print(f"Analyzing: {unique_filename}")
        cv_results = analyzer.analyze_video(front_path)
        
        # 5. Upload to Cloudinary
        print("Uploading to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            front_path, 
            resource_type="video",
            folder="ironcrate_incidents"
        )
        
        # 6. Construct Payload
        payload = {
            "driver_info": driver_info,
            "own_speed_kmh": own_speed_gps,
            "location_coords": location,
            "video_hash": front_hash,
            "video_url": upload_result.get('secure_url'),
            "ai_analysis": cv_results,
            "timestamp": {".sv": "timestamp"} 
        }
        
        # 7. Save to Firebase (using the 'db' we imported from config)
        db.child("incidents").push(payload)
        
        return jsonify({
            "message": "Incident secured and analyzed",
            "data": payload
        }), 201

    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({"error": str(e)}), 500
        
    finally:
        # 8. Cleanup
        if os.path.exists(front_path):
            os.remove(front_path)