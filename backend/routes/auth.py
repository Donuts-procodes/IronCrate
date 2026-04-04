from flask import Blueprint, request, jsonify, session
import pyrebase
import os

auth_bp = Blueprint('auth', __name__)

# Initialize Firebase Database
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DB_URL"),
    "storageBucket": "ironcrate-75923.firebasestorage.app"
}
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

@auth_bp.post('/register')
def register():
    """Matches frontend: api.post('/auth/register', data)"""
    data = request.json
    
    # Exact keys matching React's 'form' state
    vehicle = data.get('vehicle_number')
    owner = data.get('owner_name')
    phone = data.get('phone')
    
    if not vehicle:
        return jsonify({"error": "Vehicle number is required"}), 400
        
    try:
        # Save to Firebase Realtime Database
        db.child("vehicles").child(vehicle).set({
            "owner_name": owner,
            "phone": phone,
            "status": "active"
        })
        
        # Save user in Flask Session
        session['vehicle_number'] = vehicle
        session['owner_name'] = owner
        
        # React expects a 'uid' back
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