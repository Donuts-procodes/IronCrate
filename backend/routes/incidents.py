import cloudinary.uploader
from flask import Blueprint, request, jsonify

incidents_bp = Blueprint('incidents', __name__)

@incidents_bp.route('/upload-video', methods=['POST'])
def upload_video():
    # 1. Check if video exists in the request
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video']

    try:
        # 2. Bypass Blockchain and upload directly to Cloudinary
        # The format="mp4" forces Cloudinary to convert .webm files to .mp4
        upload_result = cloudinary.uploader.upload(
            video_file,
            resource_type="video",
            folder="ironcrate_videos",
            format="mp4" 
        )
        
        video_url = upload_result.get("secure_url")
        
        # 3. Save this video_url to your Firebase Realtime Database here
        # db.child("incidents").push({"video_url": video_url, "status": "logged"})

        return jsonify({"message": "Upload successful", "url": video_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500