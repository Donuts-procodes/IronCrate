"""
IronCrate - Session Routes (Chunked Live Upload)

POST /api/session/chunk     → receive a live video chunk, upload to Firebase,
                               run OpenCV detection on rear chunks
POST /api/session/finalize  → mark session complete, hash all chunks, anchor on chain
GET  /api/session/status/<tx>
"""

from flask import Blueprint, request, jsonify, session
from core.firebase import storage, db
from core.crypto   import sign_and_anchor
from core.detector import detect_objects
import time, uuid, hashlib

session_bp = Blueprint("session", __name__)


# ── Chunk Upload ─────────────────────────────────────────────────────────────
@session_bp.post("/chunk")
def upload_chunk():
    uid = session.get("uid")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401

    if "chunk" not in request.files:
        return jsonify({"error": "No chunk attached"}), 400

    chunk_bytes = request.files["chunk"].read()
    session_id  = request.form.get("session_id", "unknown")
    label       = request.form.get("label", "unknown")
    chunk_index = int(request.form.get("chunk_index", 0))
    lat         = request.form.get("lat", "")
    lon         = request.form.get("lon", "")

    # Upload to Firebase Storage
    path      = f"chunks/{uid}/{session_id}/{label}_{chunk_index:04d}.webm"
    chunk_url = storage.upload(chunk_bytes, path, content_type="video/webm")

    # Save chunk metadata in DB
    db.child("chunks").child(uid).child(session_id).child(f"{label}_{chunk_index:04d}").set({
        "url": chunk_url, "label": label, "index": chunk_index,
        "size": len(chunk_bytes), "ts": int(time.time()), "lat": lat, "lon": lon,
    })

    # OpenCV detection only on rear chunks
    detections = None
    if label == "rear":
        try:
            detections = detect_objects(chunk_bytes)
        except Exception as e:
            detections = {"error": str(e)}

    return jsonify({"chunk_url": chunk_url, "chunk_index": chunk_index, "detections": detections}), 200


# ── Finalize Session ─────────────────────────────────────────────────────────
@session_bp.post("/finalize")
def finalize_session():
    uid = session.get("uid")
    if not uid:
        return jsonify({"error": "Not authenticated"}), 401

    data       = request.get_json()
    session_id = data.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id required"}), 400

    note     = data.get("note", "")
    lat      = data.get("lat", "")
    lon      = data.get("lon", "")
    duration = data.get("duration", 0)

    # Build deterministic fingerprint from all uploaded chunk URLs
    chunks_raw  = db.child("chunks").child(uid).child(session_id).get().val() or {}
    chunk_list  = sorted(chunks_raw.values(), key=lambda x: x.get("index", 0))
    chunk_count = len(chunk_list)
    combined    = "|".join(c["url"] for c in chunk_list)
    video_hash  = hashlib.sha256(combined.encode()).hexdigest()

    metadata = {
        "uid": uid, "vehicle_number": session.get("vehicle_number", ""),
        "session_id": session_id, "timestamp": int(time.time()),
        "duration": duration, "chunk_count": chunk_count,
        "note": note, "lat": lat, "lon": lon,
    }

    # Anchor on blockchain
    try:
        tx_hash = sign_and_anchor(
            video_hash=video_hash, metadata=metadata,
            video_url=f"gs://chunks/{uid}/{session_id}/",
        )
        blockchain_status = "anchored"
    except Exception as exc:
        tx_hash           = None
        blockchain_status = f"failed: {str(exc)}"

    # Save incident record
    incident_id = str(uuid.uuid4())
    incident = {
        "incident_id": incident_id, "session_id": session_id,
        "video_hash": video_hash, "tx_hash": tx_hash,
        "blockchain_status": blockchain_status,
        "chunk_count": chunk_count, "duration": duration, "metadata": metadata,
    }
    db.child("incidents").child(uid).child(incident_id).set(incident)

    return jsonify(incident), 200


# ── TX Status ────────────────────────────────────────────────────────────────
@session_bp.get("/status/<tx_hash>")
def tx_status(tx_hash):
    from core.crypto import get_tx_status
    try:
        return jsonify(get_tx_status(tx_hash)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
