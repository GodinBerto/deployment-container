import sqlite3
from config import Config

def db_connection():
    # Connect to SQLite database (or create if it doesn't exist)
    conn = sqlite3.connect(f"{Config.DATABASE_PATH}instance/safoai.db")
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

def create_tables():
    conn, cursor = db_connection()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'invited', 'joined')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invited_at TIMESTAMP,
            joined_at TIMESTAMP
        )
        """
    )

    
    conn.commit()
    conn.close()

# Execute table creation
create_tables()
