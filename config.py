# config.py
# All configuration settings for proctoring system
import os 

def get_student_log_file(student_id):
    # Create logs folder if not exists
    os.makedirs('logs', exist_ok=True)
    return f"logs/events_{student_id}.csv"
# Camera settings
VIDEO_SOURCE = 0  # change to 0 for webcam or DroidCam URL

# Detection settings
FACE_MODEL_PATH = "detector.tflite"
MIN_DETECTION_CONFIDENCE = 0.5

# Absence settings
ABSENCE_THRESHOLD = 5  # seconds before absence alert

# Head pose settings
POSE_THRESHOLD_FACTOR = 6  # frame_width divided by this value
POSE_CONFIRMATION_FRAMES = 3  # frames before confirming pose alert

# Logging settings
LOG_FILE = "events_log.csv"
LOG_COOLDOWN = 3  # seconds between same event logs

# Display settings
FONT = 1  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1
FONT_THICKNESS = 2
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_WHITE = (255, 255, 255)

# Security
EXAM_PIN = "1234"