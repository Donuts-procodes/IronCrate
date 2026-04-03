"""
IronCrate - core/detector.py

Receives raw video chunk bytes (webm), decodes frames with OpenCV,
detects cars and pedestrians via HOG + Haar cascades,
and estimates speed via Lucas-Kanade Optical Flow.

Returns a dict:
  {
    "cars":        int,
    "pedestrians": int,
    "speed_kmh":   float | None,
    "frame_count": int,
  }
"""

import cv2
import numpy as np
import tempfile
import os

# ── Calibration ──────────────────────────────────────────────────────────────
# Pixels-per-second → km/h.  Tune against a known GPS reading on your device.
SPEED_CALIBRATION = 0.12

# ── Lazy-load detectors (only initialised once per worker process) ────────────
_hog        = None
_car_cascade = None

def _get_hog():
    global _hog
    if _hog is None:
        _hog = cv2.HOGDescriptor()
        _hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    return _hog

def _get_car_cascade():
    global _car_cascade
    if _car_cascade is None:
        # OpenCV ships this cascade; if not found we skip car detection
        cascade_path = cv2.data.haarcascades + "haarcascade_car.xml"
        if not os.path.exists(cascade_path):
            # Try common alternative location
            cascade_path = os.path.join(
                os.path.dirname(cv2.__file__), "data", "haarcascade_car.xml"
            )
        if os.path.exists(cascade_path):
            _car_cascade = cv2.CascadeClassifier(cascade_path)
    return _car_cascade


# ── Speed estimator (stateless — runs on a short clip) ───────────────────────
def _estimate_speed(frames: list[np.ndarray]) -> float | None:
    """
    Estimate speed from a sequence of grayscale frames using
    Lucas-Kanade Optical Flow. Returns km/h or None if not enough data.
    """
    if len(frames) < 3:
        return None

    feature_params = dict(maxCorners=120, qualityLevel=0.3, minDistance=7, blockSize=7)
    lk_params      = dict(
        winSize=(15, 15), maxLevel=2,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
    )

    prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
    prev_pts  = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feature_params)

    displacements = []
    for frame in frames[1:]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_pts is None or len(prev_pts) < 5:
            prev_pts = cv2.goodFeaturesToTrack(gray, mask=None, **feature_params)
            prev_gray = gray
            continue

        curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None, **lk_params)
        good_prev = prev_pts[status == 1]
        good_curr = curr_pts[status == 1]

        if len(good_curr) > 0:
            d = np.linalg.norm(good_curr - good_prev, axis=1)
            displacements.append(float(np.median(d)))

        prev_gray = gray
        prev_pts  = good_curr.reshape(-1, 1, 2) if len(good_curr) > 0 else None

    if not displacements:
        return None

    avg_disp = float(np.mean(displacements))
    speed    = round(avg_disp * SPEED_CALIBRATION * 30, 1)   # ×30 fps assumption
    return speed


# ── Main entry point ──────────────────────────────────────────────────────────
def detect_objects(chunk_bytes: bytes) -> dict:
    """
    Decode a webm/mp4 chunk and return detection counts + speed.
    Writes to a temp file because OpenCV VideoCapture needs a file path.
    """
    # Write bytes to a temp file
    suffix = ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(chunk_bytes)
        tmp_path = tmp.name

    try:
        cap = cv2.VideoCapture(tmp_path)
        if not cap.isOpened():
            return {"cars": 0, "pedestrians": 0, "speed_kmh": None, "frame_count": 0, "error": "Could not open chunk"}

        frames      = []
        sample_frames = []   # 1 in every 8 frames for detection (speed)
        frame_idx   = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            if frame_idx % 8 == 0:
                sample_frames.append(frame)
            frame_idx += 1

        cap.release()

        if not sample_frames:
            return {"cars": 0, "pedestrians": 0, "speed_kmh": None, "frame_count": 0}

        # ── Car detection (Haar cascade) ──────────────────────────────────
        cars_detected = 0
        cascade = _get_car_cascade()
        if cascade and not cascade.empty():
            for frame in sample_frames[:3]:   # check first 3 sample frames
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detections = cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60)
                )
                cars_detected = max(cars_detected, len(detections))

        # ── Pedestrian detection (HOG) ────────────────────────────────────
        peds_detected = 0
        hog = _get_hog()
        for frame in sample_frames[:3]:
            resized = cv2.resize(frame, (640, 360))
            rects, _ = hog.detectMultiScale(
                resized, winStride=(8, 8), padding=(4, 4), scale=1.05
            )
            peds_detected = max(peds_detected, len(rects))

        # ── Speed estimation ──────────────────────────────────────────────
        speed = _estimate_speed(frames[:30])   # use up to 30 frames

        return {
            "cars":        int(cars_detected),
            "pedestrians": int(peds_detected),
            "speed_kmh":   speed,
            "frame_count": frame_idx,
        }

    finally:
        os.unlink(tmp_path)
