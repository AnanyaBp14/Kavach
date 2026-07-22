import hashlib
import time
from database import get_db_connection

SECRET_KEY = "kavach_hackathon_demo_secret"

def authenticate_user(username, password):
    pass_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, pass_hash))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Create a simple mock JWT token (base64/hash format)
        token_payload = f"{user['username']}:{user['role']}:{int(time.time() + 86400)}"
        token = hashlib.sha256(token_payload.encode()).hexdigest()
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": user["username"],
                "role": user["role"]
            }
        }
    return None
