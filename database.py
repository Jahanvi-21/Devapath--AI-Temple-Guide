import sqlite3
from pathlib import Path
import hashlib

# ==========================
# Database Connection
# ==========================
DB_PATH = Path(__file__).parent / "users.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ==========================
# Create Users Table
# ==========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()

# ==========================
# Password Hash
# ==========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================
# Register User
# ==========================
def signup(name, email, password):

    try:
        cursor.execute(
            """
            INSERT INTO users(name,email,password)
            VALUES(?,?,?)
            """,
            (
                name,
                email,
                hash_password(password)
            )
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False


# ==========================
# Login User
# ==========================
def login(email, password):

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email=? AND password=?
        """,
        (
            email,
            hash_password(password)
        )
    )

    return cursor.fetchone()

# ==========================
# Check Email Exists
# ==========================
def email_exists(email):

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    return cursor.fetchone() is not None
