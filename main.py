import cv2
import time
import config
from detector import FaceDetector
from logger import EventLogger

def verify_pin():
    print("=" * 50)
    print("   AI POWERED PROCTORING SYSTEM")
    print("   Developer: Tech Titans")
    print("   SYCET IGNITE HACKATHON 2026")
    print("=" * 50)
    
    pin = input("\nEnter exam PIN to start: ")
    if pin != config.EXAM_PIN:
        print("Invalid PIN — Access Denied")
        exit()
    print("\nPIN verified — Starting system...")

def get_student_info():
    print("\nStudent Verification")
    student_id = input("Enter your Student ID: ")
    student_name = input("Enter your Name: ")
    return student_id, student_name

def main():
    verify_pin()

    student_id, student_name = get_student_info()
    print(f"\nWelcome {student_name} — ID: {student_id}")

    # Initialize modules
    detector = FaceDetector()
    logger = EventLogger(student_id)

    # Open video source
    cap = cv2.VideoCapture(config.VIDEO_SOURCE)

    if not cap.isOpened():
        print("ERROR: Cannot open camera or video file")
        print("Check VIDEO_SOURCE in config.py")
        exit()

    print("System started successfully!")
    print("Press Q to stop\n")

    # Get FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 30

    # Tracking variables
    absence_start_time = None
    prev_pose = "Looking Straight"
    pose_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Video ended or camera disconnected")
            break

        # Detect faces
        detections = detector.detect_faces(frame)
        face_count = len(detections)

        if face_count > 1:
            # Multiple faces
            for detection in detections:
                detector.draw_face_box(
                    frame, detection.bounding_box, config.COLOR_RED)

            cv2.putText(frame, f"ALERT: Multiple Faces — {face_count}",
                       (50, 50), config.FONT,
                       config.FONT_SCALE, config.COLOR_RED,
                       config.FONT_THICKNESS)
            absence_start_time = None
            logger.log_event(f"Multiple Faces Detected — {face_count}")

        elif face_count == 1:
            # Single face
            absence_start_time = None
            bbox = detections[0].bounding_box

            detector.draw_face_box(frame, bbox, config.COLOR_GREEN)

            pose = detector.get_head_pose(frame, bbox)

            # Smoothing
            if pose == prev_pose:
                pose_count += 1
            else:
                pose_count = 0
                prev_pose = pose

            if pose == "Looking Straight":
                cv2.putText(frame, "Status: OK",
                           (50, 50), config.FONT,
                           config.FONT_SCALE, config.COLOR_GREEN,
                           config.FONT_THICKNESS)
            else:
                if pose_count >= config.POSE_CONFIRMATION_FRAMES:
                    cv2.putText(frame, f"ALERT: {pose}",
                               (50, 50), config.FONT,
                               config.FONT_SCALE, config.COLOR_RED,
                               config.FONT_THICKNESS)
                    logger.log_event(f"Suspicious Pose — {pose}")
                else:
                    cv2.putText(frame, f"Warning: {pose}",
                               (50, 50), config.FONT,
                               config.FONT_SCALE, config.COLOR_ORANGE,
                               config.FONT_THICKNESS)

        else:
            # No face
            current_time = time.time()

            if absence_start_time is None:
                absence_start_time = current_time

            absence_duration = current_time - absence_start_time

            if absence_duration >= config.ABSENCE_THRESHOLD:
                cv2.putText(frame,
                           f"ALERT: Absent for {int(absence_duration)}s",
                           (50, 50), config.FONT,
                           config.FONT_SCALE, config.COLOR_RED,
                           config.FONT_THICKNESS)
                logger.log_event(
                    f"Candidate Absent — {int(absence_duration)} seconds")
            else:
                cv2.putText(frame,
                           f"No Face — {int(absence_duration)}s",
                           (50, 50), config.FONT,
                           config.FONT_SCALE, config.COLOR_ORANGE,
                           config.FONT_THICKNESS)

        # Show FPS
        cv2.putText(frame, f"FPS: {int(fps)}",
                   (frame.shape[1] - 100, 30),
                   config.FONT, 0.7,
                   config.COLOR_WHITE,
                   config.FONT_THICKNESS)

        cv2.imshow("AI Proctoring System", frame)

        if cv2.waitKey(int(1000/fps)) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    logger.print_summary()

if __name__ == "__main__":
    main()