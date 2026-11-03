import sqlite3

DATABASE_NAME = "chat_history.db"


def create_database():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            timestamp TEXT,
            status TEXT,
            user_message TEXT,
            bot_response TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_chat(
    user_id,
    username,
    first_name,
    timestamp,
    status,
    user_message,
    bot_response
):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chats (
            user_id,
            username,
            first_name,
            timestamp,
            status,
            user_message,
            bot_response
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        username,
        first_name,
        timestamp,
        status,
        user_message,
        bot_response
    ))

    conn.commit()
    conn.close()