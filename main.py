import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pandas as pd
from datetime import datetime

# Initialize MediaPipe Face Detector
base_options = mp.tasks.BaseOptions(
    model_asset_path='detector.tflite'
)
options = mp.tasks.vision.FaceDetectorOptions(
    base_options=base_options,
    running_mode=mp.tasks.vision.RunningMode.IMAGE
)
detector = mp.tasks.vision.FaceDetector.create_from_options(options)

# Absence tracking variables
absence_start_time = None
absence_threshold = 5
prev_pose = "Looking Straight"
pose_count = 0

print("=" * 50)
print("   AI POWERED PROCTORING SYSTEM")
print("   Developed by Mangesh Deokar")
print("   SYCET IGNITE HACKATHON 2026")
print("=" * 50)
print("\nInstructions:")
print("1. Make sure your face is clearly visible")
print("2. Look straight at camera during exam")
print("3. Do not let others enter the frame")
print("4. Press Q to stop proctoring session")
print("\nStarting system...")

cap = cv2.VideoCapture("test1.mp4")

if not cap.isOpened():
    print("ERROR: Cannot open camera or video file")
    print("Check your IP address or video file name")
    exit()
else:
    print("Camera/Video opened successfully!")

# Get FPS — handle live camera
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0 or fps is None:
    fps = 30  # default for live camera

def get_head_pose(frame, bbox):
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

    threshold = frame_width // 6

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

def log_event(event_type):
    global last_logged_event, last_log_time
    
    current_time = time.time()
    
    # Avoid logging same event repeatedly
    if (event_type != last_logged_event or 
        current_time - last_log_time > log_cooldown):
        
        events.append({
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'event': event_type
        })
        
        last_logged_event = event_type
        last_log_time = current_time
        
        # Save to CSV immediately
        pd.DataFrame(events).to_csv('events_log.csv', index=False)
        print(f"Event logged: {event_type}")

print("Starting Proctoring System...")
print("Press Q to quit")

# Event logger
events = []
last_logged_event = None
last_log_time = 0
log_cooldown = 3  # seconds between same event logs

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("Cannot read frame — check IP or video file")
        break

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # Detect faces
    results = detector.detect(mp_image)
    face_count = len(results.detections) if results.detections else 0

    if face_count > 1:
        # Multiple faces detected
        for detection in results.detections:
            bbox = detection.bounding_box
            cv2.rectangle(frame,
                         (int(bbox.origin_x), int(bbox.origin_y)),
                         (int(bbox.origin_x + bbox.width),
                          int(bbox.origin_y + bbox.height)),
                         (0, 0, 255), 2)
        cv2.putText(frame, f"ALERT: Multiple Faces — {face_count}",
                   (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                   1, (0, 0, 255), 2)
        log_event(f"Multiple Faces Detected — {face_count}")
        absence_start_time = None

    elif face_count == 1:
        # Single face — reset absence timer
        absence_start_time = None
        bbox = results.detections[0].bounding_box

        # Draw green box around face
        cv2.rectangle(frame,
                     (int(bbox.origin_x), int(bbox.origin_y)),
                     (int(bbox.origin_x + bbox.width),
                      int(bbox.origin_y + bbox.height)),
                     (0, 255, 0), 2)

        # Get head pose
        pose = get_head_pose(frame, bbox)

        # Smoothing — only alert if same pose 3 times in a row
        if pose == prev_pose:
            pose_count += 1
        else:
            pose_count = 0
            prev_pose = pose

        if pose == "Looking Straight":
            cv2.putText(frame, "Status: OK",
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                       1, (0, 255, 0), 2)
        else:
            if pose_count >= 3:
                cv2.putText(frame, f"ALERT: {pose}",
                           (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f"Warning: {pose}",
                           (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                           1, (0, 165, 255), 2)
                log_event(f"Suspicious Pose — {pose}")

    else:
        # No face detected — start absence timer
        current_time = time.time()

        if absence_start_time is None:
            absence_start_time = current_time

        absence_duration = current_time - absence_start_time

        if absence_duration >= absence_threshold:
            cv2.putText(frame, f"ALERT: Absent for {int(absence_duration)}s",
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                       1, (0, 0, 255), 2)
            log_event(f"Candidate Absent — {int(absence_duration)} seconds")

        else:
            cv2.putText(frame, f"No Face — {int(absence_duration)}s",
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                       1, (0, 165, 255), 2)

    # Show frame counter and FPS
    cv2.putText(frame, f"FPS: {int(fps)}",
               (frame.shape[1] - 100, 30),
               cv2.FONT_HERSHEY_SIMPLEX,
               0.7, (255, 255, 255), 2)

    cv2.imshow("AI Proctoring System", frame)

    if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
detector.close()

print("\n" + "=" * 50)
print("   PROCTORING SESSION ENDED")
print("=" * 50)

if events:
    final_df = pd.DataFrame(events)
    final_df.to_csv('events_log.csv', index=False)
    
    print(f"\nSession Summary:")
    print(f"Total Suspicious Events: {len(events)}")
    print(f"\nEvent Breakdown:")
    print(final_df['event'].value_counts().to_string())
    print(f"\nDetailed log saved to events_log.csv")
    print(f"View dashboard for visual report")
else:
    print("\nNo suspicious events detected")
    print("Session was clean!")