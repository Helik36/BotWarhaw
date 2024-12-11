import logging
import sqlite3


from Admin.database.actionWithDB.general_query import PATH

path = PATH

async def append_in_db_topic(topic: dict):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    for i, j in topic.items():
        print(f"{j} - {i}")
        cursor.execute("INSERT INTO topics (id_data, name) VALUES (?, ?)",
                       [i, j]) # обрати внимание на порядок переменных
    conn.commit()
    conn.close()

    return logging.info(f"Топик/тема `{topic}` - добавлен")


async def del_from_db_topic(topic):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM topics WHERE name = ?", [topic])

    conn.commit()
    conn.close()

    return logging.info(f"Топик/тема `{topic}` - удалён")