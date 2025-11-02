import sqlite3

def setup_feedback_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create conversation_turns table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_turns (
            turn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            prompt TEXT,
            response TEXT,
            feedback TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Feedback database setup complete.")

if __name__ == "__main__":
    setup_feedback_db()
