import sqlite3
import datetime

def cleanup_db():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()

    # Get retention period
    cursor.execute("SELECT value FROM settings WHERE key = 'retention_period_days'")
    retention_period_days = int(cursor.fetchone()[0])

    # Calculate cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_period_days)

    # Get old conversation IDs
    cursor.execute("SELECT conversation_id FROM conversations WHERE timestamp < ?", (cutoff_date,))
    old_conversation_ids = [row[0] for row in cursor.fetchall()]

    if old_conversation_ids:
        # Delete from conversation_turns
        cursor.executemany("DELETE FROM conversation_turns WHERE conversation_id = ?", [(id,) for id in old_conversation_ids])

        # Delete from conversations
        cursor.executemany("DELETE FROM conversations WHERE conversation_id = ?", [(id,) for id in old_conversation_ids])

        print(f"Deleted {len(old_conversation_ids)} old conversations.")
    else:
        print("No old conversations to delete.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    cleanup_db()
