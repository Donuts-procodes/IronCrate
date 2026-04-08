
import pyrebase
import os
from config import db
from flask import Blueprint, request, jsonify, session
from config import db  # Ensure you've moved Firebase init to config.py
auth_bp = Blueprint('auth', __name__)

# Initialize Firebase Database
# Initialize Firebase Database
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),  # Changed from FIREBASE_DB_URL
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),      # Good practice to include this
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET") 
}
@auth_bp.post('/register')
def register():
    data = request.json
    
    # 1. MATCH THESE TO YOUR REACT STATE
    # If your React code uses 'registration_number', use that here!
    vehicle = data.get('registration_number') 
    owner = data.get('owner_full_name')
    phone = data.get('phone_number')
    
    # 2. Updated Validation (Matching the error message in your screenshot)
    if not vehicle or not owner:
        return jsonify({"error": "Vehicle number and Owner name are required"}), 400
        
    try:
        # 3. Save to Firebase
        db.child("vehicles").child(vehicle).set({
            "owner_name": owner,
            "phone": phone,
            "status": "active"
        })
        
        session['vehicle_number'] = vehicle
        return jsonify({"message": "Registered", "uid": vehicle}), 201
        
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({"error": "Failed to register vehicle"}), 500



@auth_bp.post('/login')
def login():
    """Matches frontend: api.post('/auth/login', { vehicle_number })"""
    data = request.json
    vehicle = data.get('vehicle_number')
    
    try:
        # Check if vehicle exists in Firebase
        vehicle_data = db.child("vehicles").child(vehicle).get().val()
        
        if vehicle_data:
            # Login successful, create session
            session['vehicle_number'] = vehicle
            session['owner_name'] = vehicle_data.get('owner_name')
            
            return jsonify({
                "message": "Login successful", 
                "user": {
                    "vehicle_number": vehicle, 
                    "owner_name": vehicle_data.get('owner_name')
                }
            }), 200
        else:
            return jsonify({"error": "Vehicle not found. Register first."}), 404
            
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({"error": "Database connection error"}), 500


@auth_bp.get('/me')
def me():
    """Matches frontend: api.get('/auth/me') - checks if user is logged in"""
    vehicle = session.get('vehicle_number')
    owner = session.get('owner_name')
    
    if vehicle:
        return jsonify({"vehicle_number": vehicle, "owner_name": owner}), 200
        
    return jsonify({"error": "Not authenticated"}), 401


@auth_bp.post('/logout')
def logout():
    """Matches frontend: api.post('/auth/logout')"""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200