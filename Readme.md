# 🎓 AI Powered Automated Proctoring System
### SYCET IGNITE HACKATHON 2026

---

## 🎯 Problem Statement
Build a webcam based monitoring system for online exams that detects 
suspicious activities automatically using AI and Computer Vision.

---

## ✨ Features

- ✅ Real time face detection using MediaPipe AI
- ✅ Multiple face detection and instant alerts
- ✅ Head pose estimation — detects looking left, right, up, down
- ✅ Absence detection — alerts after 5 seconds of no face
- ✅ Automatic event logging with timestamps per student
- ✅ Live admin dashboard for exam supervisors
- ✅ REST API for third party exam platform integration
- ✅ API Key authentication and rate limiting
- ✅ Multi student support with unique session IDs
- ✅ Risk assessment — HIGH, MEDIUM, LOW
- ✅ System performance monitoring

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| MediaPipe | AI face detection model |
| OpenCV | Video processing and display |
| Streamlit | Live admin dashboard |
| Flask | REST API server |
| Pandas and NumPy | Event logging and analytics |
| Flask-Limiter | API rate limiting |
| Flask-CORS | Cross origin resource sharing |
| PSUtil | System performance monitoring |

---

## 🚀 How To Run

### Step 1 — Clone Repository
```bash
git clone https://github.com/Mvdcoder07/proctoring-system
cd proctoring-system
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Download MediaPipe Model
```bash
curl -o detector.tflite https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite
```

### Step 4 — Run Proctoring System
```bash
python main.py
```

### Step 5 — Run Dashboard in New Terminal
```bash
streamlit run dashboard.py
```

### Step 6 — Run REST API in New Terminal
```bash
python api.py
```

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/health | Public | System health check |
| GET | /api/events | API Key | Get all suspicious events |
| GET | /api/summary | API Key | Get analytics summary |
| GET | /api/students | API Key | Get all students overview |
| GET | /api/students/<id> | API Key | Get specific student data |
| POST | /api/events | API Key | Log new event |
| DELETE | /api/events | API Key | Clear all events |
| GET | /api/security/logs | API Key | Get security logs |

### Test API
```bash
# Health check — no key needed
curl http://localhost:5000/api/health

# Protected endpoint — API key required
curl -H "X-API-Key: EXAM001" http://localhost:5000/api/events
```

---

## 🔒 Security Features

- API Key Authentication — only authorized apps can access
- Rate Limiting — 100 requests per hour per IP
- CORS Protection — only allowed origins can connect
- Input Validation — prevents malicious data
- Checksum Verification — ensures data integrity
- Security Event Logging — tracks unauthorized access attempts

---

## 🐳 Docker Setup

### Build Image
```bash
docker build -t proctoring-system .
```

### Run Container
```bash
docker run -p 5000:5000 -p 8501:8501 proctoring-system
```

---

## 📊 How It Works For Real Exam Platform (ex. GMNS platform)

1. Student opens exam on GM Network platform
2. GM Network calls /api/health to verify system ready
3. Exam starts — main.py monitors student webcam
4. Suspicious events logged automatically with student ID
5. GM Network polls /api/summary every 30 seconds
6. HIGH RISK students flagged automatically
7. Admin monitors all students via dashboard
8. Exam ends — GM Network calls DELETE /api/events
9. System ready for next student

---

## 👥 Team
**Tech Titans**
Member 1 - Mangesh Deokar
Member 2 - Prasad Najan
Member 3 - Abhishek Gajre
BTech CSE — Data Science
Shreeyash College of Engineering and Technology
Chhatrapati Sambhajinagar, Maharashtra

---

## 📄 License
This project was developed for SYCET IGNITE HACKATHON 2026.
© 2026 Tech Titans — All Rights Reserved.