# detector.py
# Face detection and head pose estimation

import cv2
import mediapipe as mp
import config

class FaceDetector:
    def __init__(self):
        # Initialize MediaPipe detector
        base_options = mp.tasks.BaseOptions(
            model_asset_path=config.FACE_MODEL_PATH
        )
        options = mp.tasks.vision.FaceDetectorOptions(
            base_options=base_options,
            running_mode=mp.tasks.vision.RunningMode.IMAGE
        )
        self.detector = mp.tasks.vision.FaceDetector.create_from_options(options)
        print("Face detector initialized successfully")

    def detect_faces(self, frame):
        # Convert frame to MediaPipe image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )
        results = self.detector.detect(mp_image)
        return results.detections if results.detections else []

    def get_head_pose(self, frame, bbox):
        frame_height, frame_width = frame.shape[:2]
        frame_center_x = frame_width // 2
        frame_center_y = frame_height // 2

        x = int(bbox.origin_x)
        y = int(bbox.origin_y)
        w = int(bbox.width)
        h = int(bbox.height)

        face_center_x = x + w // 2
        face_center_y = y + h // 2

        x_deviation = face_center_x - frame_center_x
        y_deviation = face_center_y - frame_center_y

        threshold = frame_width // config.POSE_THRESHOLD_FACTOR

        if x_deviation < -threshold:
            return "Looking Left"
        elif x_deviation > threshold:
            return "Looking Right"
        elif y_deviation < -threshold:
            return "Looking Up"
        elif y_deviation > threshold:
            return "Looking Down"
        else:
            return "Looking Straight"

    def draw_face_box(self, frame, bbox, color):
        cv2.rectangle(frame,
                     (int(bbox.origin_x), int(bbox.origin_y)),
                     (int(bbox.origin_x + bbox.width),
                      int(bbox.origin_y + bbox.height)),
                     color, 2)

    def close(self):
        self.detector.close()