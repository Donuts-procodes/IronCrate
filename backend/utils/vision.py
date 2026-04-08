"""
IronCrate — utils/vision.py
OpenCV-based dashcam video analyser.
"""
import cv2
import os


class DashcamAnalyzer:
    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Resolve cascade path relative to the backend root
        base_dir     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cascade_path = os.path.join(base_dir, "haarcascade_cars.xml")

        self.car_cascade = None
        if os.path.exists(cascade_path):
            clf = cv2.CascadeClassifier(cascade_path)
            if not clf.empty():
                self.car_cascade = clf
            else:
                print(f"[vision] WARNING: cascade file could not be loaded: {cascade_path}")
        else:
            print(f"[vision] WARNING: cascade file not found at {cascade_path}")

    def analyze_video(self, video_path: str) -> dict:
        cap = cv2.VideoCapture(video_path)

        total_pedestrians  = 0
        total_cars         = 0
        max_relative_speed = 0.0
        prev_car_sizes     = {}
        frame_count        = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % 10 == 0:
                frame = cv2.resize(frame, (640, 480))
                gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Pedestrian detection
                boxes, _ = self.hog.detectMultiScale(frame, winStride=(8, 8))
                total_pedestrians = max(total_pedestrians, len(boxes))

                # Car detection + rudimentary speed estimation
                if self.car_cascade is not None:
                    cars = self.car_cascade.detectMultiScale(gray, 1.1, 1)
                    total_cars = max(total_cars, len(cars))
                    for i, (x, y, w, h) in enumerate(cars):
                        size = w * h
                        if i in prev_car_sizes:
                            growth = size - prev_car_sizes[i]
                            if growth > max_relative_speed:
                                max_relative_speed = growth
                        prev_car_sizes[i] = size

            frame_count += 1

        cap.release()

        return {
            "max_pedestrians_in_frame": total_pedestrians,
            "max_cars_in_frame":        total_cars,
            "collision_risk_factor":    round(max_relative_speed / 1000, 2),
            "cv_analysis_complete":     True,
        }
