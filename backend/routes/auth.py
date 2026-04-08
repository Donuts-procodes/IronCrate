"""
IronCrate — routes/auth.py
Register / Login / Me / Logout
Session key used throughout: 'vehicle_number'  (consistent with session.py)
"""
from flask import Blueprint, request, jsonify, session
from core.firebase import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data    = request.get_json()
    vehicle = data.get("vehicle_number", "").strip().upper()
    owner   = data.get("owner_name", "").strip()
    phone   = data.get("phone", "").strip()

    if not vehicle:
        return jsonify({"error": "Vehicle number is required"}), 400

    try:
        db.child("vehicles").child(vehicle).set({
            "owner_name": owner,
            "phone":      phone,
            "status":     "active",
        })
        session["vehicle_number"] = vehicle
        session["owner_name"]     = owner
        return jsonify({"message": "Registered", "uid": vehicle}), 201
    except Exception as e:
        print(f"[auth/register] DB error: {e}")
        return jsonify({"error": "Failed to register vehicle"}), 500


@auth_bp.post("/login")
def login():
    data    = request.get_json()
    vehicle = data.get("vehicle_number", "").strip().upper()

    if not vehicle:
        return jsonify({"error": "Vehicle number is required"}), 400

    try:
        vehicle_data = db.child("vehicles").child(vehicle).get().val()
        if vehicle_data:
            session["vehicle_number"] = vehicle
            session["owner_name"]     = vehicle_data.get("owner_name", "")
            return jsonify({
                "message": "Login successful",
                "user": {
                    "vehicle_number": vehicle,
                    "owner_name":     vehicle_data.get("owner_name", ""),
                },
            }), 200
        return jsonify({"error": "Vehicle not found. Register first."}), 404
    except Exception as e:
        print(f"[auth/login] DB error: {e}")
        return jsonify({"error": "Database connection error"}), 500


@auth_bp.get("/me")
def me():
    vehicle = session.get("vehicle_number")
    if vehicle:
        return jsonify({
            "vehicle_number": vehicle,
            "owner_name":     session.get("owner_name", ""),
        }), 200
    return jsonify({"error": "Not authenticated"}), 401


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200
