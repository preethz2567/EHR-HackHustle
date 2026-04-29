import secrets
import time
from datetime import datetime, timezone, timedelta
import threading
from flask import request, jsonify, g
from functools import wraps

# In-memory session store
# session_id -> DoctorSession
ACTIVE_SESSIONS = {}

class DoctorSession:
    def __init__(self, doctor_id: str, patient_id: str, access_token: str, duration_minutes: int = 30):
        self.session_id = secrets.token_urlsafe(32)
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.access_token = access_token
        
        self.login_time = datetime.now(timezone.utc)
        self.session_expiry = self.login_time + timedelta(minutes=duration_minutes)
        self.status = "active"

    def is_valid(self) -> bool:
        if self.status != "active":
            return False
        return not self.is_expired()

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.session_expiry

    def extend_session(self, additional_minutes: int = 30):
        if self.status == "active":
            self.session_expiry += timedelta(minutes=additional_minutes)

    def end_session(self):
        self.status = "ended"

def cleanup_expired_sessions():
    """Background task to remove expired sessions."""
    while True:
        now = datetime.now(timezone.utc)
        expired_keys = []
        for sid, session in ACTIVE_SESSIONS.items():
            if session.is_expired() or session.status != "active":
                expired_keys.append(sid)
        
        for sid in expired_keys:
            del ACTIVE_SESSIONS[sid]
            
        if expired_keys:
            print(f"[SessionManager] Cleaned up {len(expired_keys)} expired sessions at {now.isoformat()}")
            
        time.sleep(60)

def init_session_manager():
    """Start the background cleanup thread."""
    t = threading.Thread(target=cleanup_expired_sessions, daemon=True)
    t.start()
    print("[SessionManager] Background cleanup thread started.")

def session_required(f):
    """
    Middleware decorator to enforce valid DoctorSession.
    Extracts Session-Id from headers.
    Returns 401 if missing, invalid, or expired.
    Sets g.doctor_session to the active session.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        session_id = request.headers.get("Session-Id")
        if not session_id:
            return jsonify({
                "status": "error", 
                "message": "Missing Session-Id header."
            }), 401

        session = ACTIVE_SESSIONS.get(session_id)
        if not session or not session.is_valid():
            return jsonify({
                "status": "error", 
                "message": "Session expired, please login again"
            }), 401

        # Extend session automatically on activity? 
        # The prompt says 30 min timeout, extend logic can be added later or explicit
        
        g.doctor_session = session
        return f(*args, **kwargs)
    return wrapper
