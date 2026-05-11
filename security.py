# security.py
# Network and Security Layer

import hashlib
import hmac
import time
import functools
from flask import request, jsonify
import config

# ================================
# API Key Management
# ================================

# Valid API keys — in production store in database
VALID_API_KEYS = {
    "EXAM001": "School A",
    "EXAM002": "College B",
    "ADMIN01": "Admin User"
}

def validate_api_key(f):
    """Decorator to validate API key on every request"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'API key missing',
                'hint': 'Add X-API-Key header'
            }), 401
        
        if api_key not in VALID_API_KEYS:
            # Log unauthorized attempt
            log_security_event(
                f"Unauthorized API access attempt with key: {api_key}"
            )
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 403
        
        return f(*args, **kwargs)
    return decorated

# ================================
# Request Validation
# ================================

def validate_event_data(data):
    """Validate incoming event data"""
    errors = []
    
    if not data:
        errors.append("Request body is empty")
        return errors
    
    if 'event' not in data:
        errors.append("Event type is required")
    
    if 'event' in data:
        if not isinstance(data['event'], str):
            errors.append("Event must be a string")
        if len(data['event']) > 200:
            errors.append("Event description too long")
        if len(data['event']) < 3:
            errors.append("Event description too short")
    
    return errors

# ================================
# Checksum Verification
# ================================

def generate_checksum(data):
    """Generate checksum for data integrity"""
    data_string = str(data).encode('utf-8')
    return hashlib.sha256(data_string).hexdigest()

def verify_checksum(data, checksum):
    """Verify data integrity using checksum"""
    expected = generate_checksum(data)
    return hmac.compare_digest(expected, checksum)

# ================================
# Security Event Logger
# ================================

security_events = []

def log_security_event(event):
    """Log security related events"""
    security_events.append({
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'event': event,
        'ip': request.remote_addr if request else 'unknown'
    })
    print(f"SECURITY: {event}")

def get_security_events():
    """Get all security events"""
    return security_events

# ================================
# IP Whitelist
# ================================

WHITELISTED_IPS = [
    '127.0.0.1',    # localhost
    '::1',           # localhost IPv6
]

def is_ip_whitelisted(ip):
    """Check if IP is whitelisted"""
    return ip in WHITELISTED_IPS

def require_whitelist(f):
    """Decorator to require whitelisted IP"""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        client_ip = request.remote_addr
        if not is_ip_whitelisted(client_ip):
            log_security_event(
                f"Access attempt from non-whitelisted IP: {client_ip}"
            )
            return jsonify({
                'status': 'error',
                'message': 'Access denied from your IP'
            }), 403
        return f(*args, **kwargs)
    return decorated