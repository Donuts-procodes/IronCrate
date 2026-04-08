"""
IronCrate — core/detector.py
Thin wrapper around DashcamAnalyzer for use with raw video chunk bytes.
"""
import tempfile
import os
import uuid
from utils.vision import DashcamAnalyzer

_analyzer = DashcamAnalyzer()


def detect_objects(chunk_bytes: bytes) -> dict:
    """
    Write chunk bytes to a temp file, run OpenCV analysis, then clean up.
    Returns the cv_results dict from DashcamAnalyzer.
    """
    tmp_path = os.path.join(tempfile.gettempdir(), f"chunk_{uuid.uuid4().hex}.webm")
    try:
        with open(tmp_path, "wb") as f:
            f.write(chunk_bytes)
        return _analyzer.analyze_video(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
