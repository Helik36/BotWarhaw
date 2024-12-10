from datetime import datetime, timedelta
import sqlite3


path = "Admin/database/DataChannelAndChat.db"

def createbase_for_admin():

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY,
        id_channel INTEGER,
        name TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DBdelete_text (
        id INTEGER PRIMARY KEY,
        text_trigger TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_pause_for_post (
        id INTEGER PRIMARY KEY,
        time_end_pause_post TEXT NOT NULL
    )
    """)

    conn.commit()

    # cursor.execute("INSERT INTO time_pause_for_post (time_end_pause_post) VALUES (?)", [str(datetime.now())])
    #
    # conn.commit()
    conn.close()


if __name__ == "__main__":
    createbase_for_admin()