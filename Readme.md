# AI Powered Automated Proctoring System
### SYCET IGNITE HACKATHON 2026

## Problem Statement
Build a webcam based monitoring system for online exams 
that detects suspicious activities automatically.

## Features
- Real time face detection
- Multiple face detection and alerts
- Head pose estimation — detects looking away
- Absence detection — alerts after 5 seconds
- Automatic event logging with timestamps
- Live dashboard for exam supervisors

## Tech Stack
- Python
- OpenCV — video processing
- MediaPipe — AI face detection
- Streamlit — dashboard
- Pandas — event logging

## How To Run

### Install dependencies
pip install -r requirements.txt

### Download MediaPipe model
curl -o detector.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite

### Run proctoring system
python main.py

### Run dashboard in separate terminal
streamlit run dashboard.py

## Developer
[Team Name]
BTech CSE Data Science
Shreeyash College of Engineering and Technology
Chhatrapati Sambhajinagar