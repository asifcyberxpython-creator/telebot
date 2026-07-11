"""
CyberAI Bot — Database Session Manager
Handles session state, user settings, and activity logs storage.
"""

import json
import os
import datetime
from pathlib import Path
from bot.config import SESSIONS_FILE, HISTORY_FILE, IP_LOGS_DIR

# In-memory session cache to store active user sessions (including non-serializable objects like tunnel_service)
_sessions = {}

def load_sessions():
    """Load session data from SESSIONS_FILE into the in-memory cache."""
    global _sessions
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    # Initialize default structure if some keys are missing
                    session = {
                        "user_id": v.get("user_id", int(k) if k.isdigit() else k),
                        "created_at": v.get("created_at", datetime.datetime.now().isoformat()),
                        "settings": {
                            "default_cam_mode": "front",
                            "default_redirect_time": 5,
                            "notifications": True,
                            **v.get("settings", {})
                        },
                        "state": {
                            "flow": "",
                            "step": "",
                            **v.get("state", {})
                        },
                        "tunnel_service": None
                    }
                    _sessions[str(k)] = session
        except Exception:
            pass

# Initialize cache at startup
load_sessions()

def get_session(user_id):
    """Retrieve user's session, creating a default one if not found."""
    user_id_str = str(user_id)
    if user_id_str not in _sessions:
        _sessions[user_id_str] = {
            "user_id": int(user_id) if user_id_str.isdigit() else user_id,
            "created_at": datetime.datetime.now().isoformat(),
            "settings": {
                "default_cam_mode": "front",
                "default_redirect_time": 5,
                "notifications": True
            },
            "state": {
                "flow": "",
                "step": ""
            },
            "tunnel_service": None
        }
        save_session(user_id, _sessions[user_id_str])
    return _sessions[user_id_str]

def save_session(user_id, session):
    """Save the session back to file, excluding non-serializable objects like tunnel_service."""
    user_id_str = str(user_id)
    _sessions[user_id_str] = session

    # Rebuild the serializable sessions dict
    serializable_sessions = {}
    for uid, sess in _sessions.items():
        sess_copy = {}
        for k, v in sess.items():
            if k != 'tunnel_service':
                sess_copy[k] = v
        serializable_sessions[uid] = sess_copy

    try:
        Path(SESSIONS_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_sessions, f, indent=2)
    except Exception:
        pass

def get_conversation_state(user_id):
    """Retrieve the conversation state dictionary for a user."""
    session = get_session(user_id)
    return session.get("state", {})

def set_conversation_state(user_id, state, data=None):
    """Set the conversation state flow and step, optionally adding arbitrary data."""
    session = get_session(user_id)
    if isinstance(state, dict):
        session["state"] = state
    else:
        session["state"] = {
            "flow": state,
            "step": ""
        }
    if data is not None:
        session["state"]["data"] = data
    save_session(user_id, session)

def clear_conversation_state(user_id):
    """Reset the conversation state for a user."""
    session = get_session(user_id)
    session["state"] = {
        "flow": "",
        "step": ""
    }
    save_session(user_id, session)

def get_user_setting(user_id, setting_name, default=None):
    """Get a specific setting for a user."""
    session = get_session(user_id)
    return session.get("settings", {}).get(setting_name, default)

def set_user_setting(user_id, setting_name, value):
    """Set a specific setting for a user."""
    session = get_session(user_id)
    if "settings" not in session:
        session["settings"] = {}
    session["settings"][setting_name] = value
    save_session(user_id, session)

def log_activity(user_id, action, details=""):
    """Log an activity to both activity.log and history.json."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    # 1. Append to activity.log
    log_line = f"{timestamp} | {user_id} | {action.upper()} | {details}\n"
    try:
        IP_LOGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(IP_LOGS_DIR / "activity.log", "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass

    # 2. Append to history.json
    try:
        history = {}
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
        
        user_key = str(user_id)
        if user_key not in history:
            history[user_key] = []
            
        history[user_key].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "details": details
        })
        
        # Keep only the last 100 history entries
        history[user_key] = history[user_key][-100:]
        
        Path(HISTORY_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass

class SessionManager:
    """Class interface for session management (used in main.py)."""
    @staticmethod
    def get_all_users():
        users = []
        for k in _sessions.keys():
            if k.isdigit():
                users.append(int(k))
            else:
                users.append(k)
        return users

    @staticmethod
    def get_session(user_id):
        return get_session(user_id)

    @staticmethod
    def save_session(user_id, session):
        save_session(user_id, session)