"""
IronCrate — routes/session.py
Chunked live-recording upload and session finalisation.

POST  /api/session/chunk        → receive one live video chunk
POST  /api/session/finalize     → hash all chunks, anchor on Polygon
GET   /api/session/status/<tx>  → transaction receipt
"""
import hashlib
import time
import uuid

from flask import Blueprint, request, jsonify, session
from core.firebase import db, storage
from core.crypto   import sign_and_anchor, get_tx_status
from core.detector import detect_objects

session_bp = Blueprint("session", __name__)


def _require_auth():
    """Return vehicle_number or None."""
    return session.get("vehicle_number")


# ── Chunk Upload ──────────────────────────────────────────────────────────────
@session_bp.post("/chunk")
def upload_chunk():
    vehicle = _require_auth()
    if not vehicle:
        return jsonify({"error": "Not authenticated"}), 401

    if "chunk" not in request.files:
        return jsonify({"error": "No chunk attached"}), 400

    chunk_bytes = request.files["chunk"].read()
    session_id  = request.form.get("session_id", "unknown")
    label       = request.form.get("label", "front")   # "front" or "rear"
    chunk_index = int(request.form.get("chunk_index", 0))
    lat         = request.form.get("lat", "")
    lon         = request.form.get("lon", "")

    # Upload to Firebase Storage
    path      = f"chunks/{vehicle}/{session_id}/{label}_{chunk_index:04d}.webm"
    chunk_url = storage.child(path).put(chunk_bytes)

    # Persist chunk metadata
    db.child("chunks").child(vehicle).child(session_id)\
      .child(f"{label}_{chunk_index:04d}").set({
          "url":   path,
          "label": label,
          "index": chunk_index,
          "size":  len(chunk_bytes),
          "ts":    int(time.time()),
          "lat":   lat,
          "lon":   lon,
      })

    # Run detection only on rear-facing chunks
    detections = None
    if label == "rear":
        try:
            detections = detect_objects(chunk_bytes)
        except Exception as e:
            detections = {"error": str(e)}

    return jsonify({
        "chunk_path":  path,
        "chunk_index": chunk_index,
        "detections":  detections,
    }), 200


# ── Finalize Session ──────────────────────────────────────────────────────────
@session_bp.post("/finalize")
def finalize_session():
    vehicle = _require_auth()
    if not vehicle:
        return jsonify({"error": "Not authenticated"}), 401

    data       = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    note     = data.get("note", "")
    lat      = data.get("lat", "")
    lon      = data.get("lon", "")
    duration = data.get("duration", 0)

    # Build fingerprint from all chunk paths
    chunks_raw  = db.child("chunks").child(vehicle).child(session_id).get().val() or {}
    chunk_list  = sorted(chunks_raw.values(), key=lambda x: x.get("index", 0))
    chunk_count = len(chunk_list)
    combined    = "|".join(c["url"] for c in chunk_list)
    video_hash  = hashlib.sha256(combined.encode()).hexdigest()

    metadata = {
        "vehicle_number": vehicle,
        "owner_name":     session.get("owner_name", ""),
        "session_id":     session_id,
        "timestamp":      int(time.time()),
        "duration":       duration,
        "chunk_count":    chunk_count,
        "note":           note,
        "lat":            lat,
        "lon":            lon,
    }

    # Attempt blockchain anchoring
    try:
        tx_hash           = sign_and_anchor(
            video_hash=video_hash,
            metadata=metadata,
            video_url=f"gs://chunks/{vehicle}/{session_id}/",
        )
        blockchain_status = "anchored"
    except Exception as exc:
        print(f"[session/finalize] Blockchain error: {exc}")
        tx_hash           = None
        blockchain_status = f"failed: {str(exc)}"

    # Persist incident record
    incident_id = str(uuid.uuid4())
    incident = {
        "incident_id":        incident_id,
        "session_id":         session_id,
        "vehicle_number":     vehicle,
        "video_hash":         video_hash,
        "tx_hash":            tx_hash,
        "blockchain_status":  blockchain_status,
        "chunk_count":        chunk_count,
        "duration":           duration,
        "metadata":           metadata,
    }
    db.child("incidents").child(vehicle).child(incident_id).set(incident)

    return jsonify(incident), 200


# ── TX Status ─────────────────────────────────────────────────────────────────
@session_bp.get("/status/<tx_hash>")
def tx_status(tx_hash):
    try:
        return jsonify(get_tx_status(tx_hash)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
