import cv2
# import numpy as np
import os  # <-- Required for finding the file path

class DashcamAnalyzer:
    def __init__(self):
        # Initialize OpenCV's built-in Pedestrian detector
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        # Get the absolute path to the root folder where app.py lives
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cascade_path = os.path.join(base_dir, 'haarcascade_cars.xml')
        
        try:
            self.car_cascade = cv2.CascadeClassifier(cascade_path)
            # OpenCV's CascadeClassifier doesn't always throw an error if it fails to load, 
            # it just returns an empty object. This checks to ensure it actually loaded.
            if self.car_cascade.empty():
                print(f"WARNING: Could not load cascade file at {cascade_path}")
                self.car_cascade = None
        except Exception as e:
            print(f"Error loading cascade: {e}")
            self.car_cascade = None

    def analyze_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        
        total_pedestrians = 0
        total_cars = 0
        max_relative_speed = 0.0
        
        frame_count = 0
        prev_car_sizes = {} # Used to track if cars are approaching rapidly (speed)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process every 10th frame to save massive amounts of CPU time
            if frame_count % 10 == 0:
                # Resize for faster processing
                frame = cv2.resize(frame, (640, 480))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 1. Detect Pedestrians
                boxes, weights = self.hog.detectMultiScale(frame, winStride=(8,8))
                pedestrian_count = len(boxes)
                total_pedestrians = max(total_pedestrians, pedestrian_count)
                
                # 2. Detect Cars & Estimate Relative Speed
                if self.car_cascade:
                    cars = self.car_cascade.detectMultiScale(gray, 1.1, 1)
                    total_cars = max(total_cars, len(cars))
                    
                    for (i, (x, y, w, h)) in enumerate(cars):
                        current_size = w * h
                        # A very rudimentary speed estimation:
                        # If the bounding box gets exponentially larger, the car is approaching fast.
                        if i in prev_car_sizes:
                            growth_rate = current_size - prev_car_sizes[i]
                            if growth_rate > max_relative_speed:
                                max_relative_speed = growth_rate
                        prev_car_sizes[i] = current_size

            frame_count += 1

        cap.release()
        
        return {
            "max_pedestrians_in_frame": total_pedestrians,
            "max_cars_in_frame": total_cars,
            "collision_risk_factor": round(max_relative_speed / 1000, 2), # Normalized dummy value
            "cv_analysis_complete": True
        }