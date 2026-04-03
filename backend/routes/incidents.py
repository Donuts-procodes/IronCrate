"""
IronCrate - Incidents Routes
GET /api/incidents        → list all incidents for current user
GET /api/incidents/<id>   → single incident detail
"""

from flask import Blueprint, jsonify, session
from core.firebase import db
from core.crypto   import get_incident_from_chain

incidents_bp = Blueprint("incidents", __name__)


@incidents_bp.get("/")
def list_incidents():
    uid = session.get("uid")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401

    raw = db.child("incidents").child(uid).get().val() or {}
    incidents = sorted(raw.values(), key=lambda x: x.get("timestamp", 0), reverse=True)
    return jsonify(incidents), 200


@incidents_bp.get("/<incident_id>")
def get_incident(incident_id):
    uid = session.get("uid")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401

    record = db.child("incidents").child(uid).child(incident_id).get().val()
    if not record:
        return jsonify({"error": "Not found"}), 404

    # Optionally enrich with on-chain data
    if record.get("tx_hash"):
        try:
            chain_data = get_incident_from_chain(record["tx_hash"])
            record["chain_data"] = chain_data
        except Exception:
            record["chain_data"] = None

    return jsonify(record), 200
