import sqlite3
import bcrypt
import hashlib
import time

#In-memory session token store
_token_store = {}

#Initialize users table and migrate pro_access column if missing
def init_user_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()

    # Create base table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            name TEXT,
            password_hash TEXT
        )
    """)
    conn.commit()

    #Add pro_access column if missing
    cur.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cur.fetchall()]
    if "pro_access" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN pro_access TEXT DEFAULT 'no'")
        conn.commit()

    conn.close()


#Register new user
def register_user(name, username, password):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cur.execute("""
            INSERT INTO users (username, name, password_hash, pro_access)
            VALUES (?, ?, ?, 'no')
        """, (username, name, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


#Authenticate credentials
def authenticate_user(username, password):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return bcrypt.checkpw(password.encode('utf-8'), row[0])
    return False


#Check if user has Pro access
def is_user_pro(username):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT pro_access FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] == "yes"


#Grant Pro access
def upgrade_user_to_pro(username):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET pro_access = 'yes' WHERE username = ?", (username,))
    conn.commit()
    conn.close()


#Revoke Pro access
def revoke_user_pro(username):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET pro_access = 'no' WHERE username = ?", (username,))
    conn.commit()
    conn.close()


#Fetch full user profile
def get_user_profile(username):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT username, name, pro_access FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "username": row[0],
            "name": row[1],
            "is_premium": row[2] == "yes",
            "is_admin": row[0] == "admin"
        }
    return None


#Create a session token (to survive Ctrl+R)
def create_user_session(username):
    token_raw = f"{username}-{time.time()}"
    token = hashlib.sha256(token_raw.encode()).hexdigest()
    _token_store[token] = username
    return token


#Get username from session token
def get_username_from_token(token):
    return _token_store.get(token)
