# api.py
# Secured REST API for AI Proctoring System
import glob
from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import pandas as pd
import os
import config
from security import (
    validate_api_key,
    validate_event_data,
    generate_checksum,
    log_security_event,
    get_security_events
)

# GET all students summary
@app.route('/api/students', methods=['GET'])
@validate_api_key
def get_all_students():
    
    # Find all student log files
    log_files = glob.glob('logs/events_*.csv')
    
    students_summary = []
    
    for log_file in log_files:
        df = pd.read_csv(log_file)
        
        if len(df) > 0:
            student_id = df['student_id'].iloc[0]
            
            students_summary.append({
                'student_id': student_id,
                'total_events': len(df),
                'multiple_face_alerts': int(len(df[df['event'].str.contains('Multiple', na=False)])),
                'pose_alerts': int(len(df[df['event'].str.contains('Pose', na=False)])),
                'absence_alerts': int(len(df[df['event'].str.contains('Absent', na=False)])),
                'risk_level': get_risk_level(len(df))
            })
    
    return jsonify({
        'status': 'success',
        'total_students': len(students_summary),
        'students': students_summary
    })

# GET specific student events
@app.route('/api/students/<student_id>', methods=['GET'])
@validate_api_key
def get_student_events(student_id):
    log_file = f'logs/events_{student_id}.csv'
    
    if not os.path.exists(log_file):
        return jsonify({
            'status': 'error',
            'message': f'No data found for student {student_id}'
        }), 404
    
    df = pd.read_csv(log_file)
    
    return jsonify({
        'status': 'success',
        'student_id': student_id,
        'total_events': len(df),
        'risk_level': get_risk_level(len(df)),
        'events': df.to_dict(orient='records')
    })

app = Flask(__name__)

# ================================
# CORS Protection
# ================================
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000",
                   "http://localhost:8501"],
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["X-API-Key", "Content-Type"]
    }
})

# ================================
# Rate Limiting
# ================================
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"]
)

# ================================
# Helper Functions
# ================================

def load_events():
    if os.path.exists(config.LOG_FILE):
        df = pd.read_csv(config.LOG_FILE)
        return df
    return pd.DataFrame(columns=['date', 'timestamp', 'event'])

def get_risk_level(total_events):
    if total_events >= 10:
        return "HIGH"
    elif total_events >= 5:
        return "MEDIUM"
    else:
        return "LOW"

# ================================
# PUBLIC ENDPOINTS — No auth needed
# ================================

@app.route('/api/health', methods=['GET'])
@limiter.limit("30 per minute")
def health_check():
    import psutil
    return jsonify({
        'status': 'healthy',
        'cpu_usage': f"{psutil.cpu_percent()}%",
        'memory_usage': f"{psutil.virtual_memory().percent}%",
        'log_file_exists': os.path.exists(config.LOG_FILE),
        'api_version': '1.0'
    })

# ================================
# PROTECTED ENDPOINTS — Auth needed
# ================================

@app.route('/api/events', methods=['GET'])
@limiter.limit("50 per minute")
@validate_api_key
def get_events():
    df = load_events()
    
    # Generate checksum for data integrity
    data = df.to_dict(orient='records')
    checksum = generate_checksum(data)
    
    return jsonify({
        'status': 'success',
        'total_events': len(df),
        'checksum': checksum,
        'events': data
    })

@app.route('/api/summary', methods=['GET'])
@limiter.limit("30 per minute")
@validate_api_key
def get_summary():
    df = load_events()

    if len(df) == 0:
        return jsonify({
            'status': 'success',
            'message': 'No events logged yet'
        })

    summary = {
        'total_events': int(len(df)),
        'multiple_face_alerts': int(
            len(df[df['event'].str.contains('Multiple', na=False)])),
        'pose_alerts': int(
            len(df[df['event'].str.contains('Pose', na=False)])),
        'absence_alerts': int(
            len(df[df['event'].str.contains('Absent', na=False)])),
        'risk_level': get_risk_level(len(df)),
        'checksum': generate_checksum(df.to_dict())
    }

    return jsonify({
        'status': 'success',
        'summary': summary
    })

@app.route('/api/events/<event_type>', methods=['GET'])
@limiter.limit("30 per minute")
@validate_api_key
def get_events_by_type(event_type):
    df = load_events()
    filtered = df[df['event'].str.contains(
        event_type, case=False, na=False)]

    return jsonify({
        'status': 'success',
        'event_type': event_type,
        'count': len(filtered),
        'events': filtered.to_dict(orient='records')
    })

@app.route('/api/events', methods=['POST'])
@limiter.limit("20 per minute")
@validate_api_key
def add_event():
    data = request.get_json()

    # Validate input
    errors = validate_event_data(data)
    if errors:
        log_security_event(f"Invalid event data: {errors}")
        return jsonify({
            'status': 'error',
            'errors': errors
        }), 400

    from datetime import datetime

    new_event = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'event': data['event']
    }

    df = load_events()
    df = pd.concat([df, pd.DataFrame([new_event])],
                   ignore_index=True)
    df.to_csv(config.LOG_FILE, index=False)

    return jsonify({
        'status': 'success',
        'message': 'Event logged',
        'event': new_event,
        'checksum': generate_checksum(new_event)
    }), 201

@app.route('/api/events', methods=['DELETE'])
@limiter.limit("5 per minute")
@validate_api_key
def clear_events():
    if os.path.exists(config.LOG_FILE):
        os.remove(config.LOG_FILE)
        log_security_event("All events cleared via API")

    return jsonify({
        'status': 'success',
        'message': 'All events cleared'
    })

# ================================
# ADMIN ENDPOINTS
# ================================

@app.route('/api/security/logs', methods=['GET'])
@limiter.limit("10 per minute")
@validate_api_key
def get_security_logs():
    return jsonify({
        'status': 'success',
        'security_events': get_security_events()
    })

# ================================
# Error Handlers
# ================================

@app.errorhandler(429)
def rate_limit_exceeded(e):
    log_security_event("Rate limit exceeded")
    return jsonify({
        'status': 'error',
        'message': 'Too many requests — slow down',
        'retry_after': '60 seconds'
    }), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

# ================================
# Run Server
# ================================

if __name__ == '__main__':
    print("=" * 50)
    print("   AI Proctoring Secured REST API")
    print("   Running on http://localhost:5000")
    print("=" * 50)
    print("\nSecurity Features Active:")
    print("✅ API Key Authentication")
    print("✅ Rate Limiting — 100 req/hour")
    print("✅ CORS Protection")
    print("✅ Input Validation")
    print("✅ Checksum Verification")
    print("✅ Security Event Logging")
    print("\nTest with API Key: EXAM001")
    print("\nAvailable Endpoints:")
    print("GET    /api/health         — Public")
    print("GET    /api/events         — Protected")
    print("GET    /api/summary        — Protected")
    print("POST   /api/events         — Protected")
    print("DELETE /api/events         — Protected")
    print("GET    /api/security/logs  — Admin")
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)