import sqlite3

def db_connection():
    # Connect to SQLite database (or create if it doesn't exist)
    conn = sqlite3.connect("instance/procurement.db")
    conn.row_factory = sqlite3.Row
    return conn, conn.cursor()

def create_tables():
    conn, cursor = db_connection()
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('Super Admin', 'Admin', 'Staff', 'Customer')),
            department NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_by TEXT,
            edited_by TEXT
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            stock_quantity INTEGER NOT NULL DEFAULT 0,
            department TEXT NOT NULL,
            description TEXT NOT NULL,
            supplier_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            edited_by TEXT
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by TEXT,
            edited_by TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Department (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
        """
    )
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT CHECK(type IN ('Error', 'Success')),
            action TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id)
        )
        """
    )

    
    conn.commit()
    conn.close()

# Execute table creation
create_tables()
