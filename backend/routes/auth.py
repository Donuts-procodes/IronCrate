"""
IronCrate - Auth Routes
POST /api/auth/register  → save vehicle + owner info
POST /api/auth/login     → lookup by vehicle number
GET  /api/auth/me        → current session user
POST /api/auth/logout
"""

from flask import Blueprint, request, jsonify, session
from core.firebase import db, storage
import uuid, time

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json()
    required = ["vehicle_number", "owner_name", "phone"]
    if missing := [f for f in required if not data.get(f)]:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    uid = str(uuid.uuid4())
    record = {
        "uid":            uid,
        "vehicle_number": data["vehicle_number"].upper().strip(),
        "owner_name":     data["owner_name"].strip(),
        "phone":          data["phone"].strip(),
        "registered_at":  int(time.time()),
    }

    db.child("users").child(uid).set(record)

    session["uid"]            = uid
    session["vehicle_number"] = record["vehicle_number"]
    return jsonify({"message": "Registered successfully", "uid": uid}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    vehicle = data.get("vehicle_number", "").upper().strip()
    if not vehicle:
        return jsonify({"error": "vehicle_number required"}), 400

    users = db.child("users").get().val() or {}
    user  = next((v for v in users.values() if v.get("vehicle_number") == vehicle), None)
    if not user:
        return jsonify({"error": "Vehicle not registered"}), 404

    session["uid"]            = user["uid"]
    session["vehicle_number"] = user["vehicle_number"]
    return jsonify({"message": "Logged in", "user": user}), 200


@auth_bp.get("/me")
def me():
    uid = session.get("uid")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401
    user = db.child("users").child(uid).get().val()
    return jsonify(user), 200


@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200
