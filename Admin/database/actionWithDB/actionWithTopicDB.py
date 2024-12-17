import asyncio
import logging
import sqlite3
from Admin.database.actionWithDB.general_query import PATH

path = PATH


async def get_topic_from_channel(name_channel: str) -> dict:
    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    topics = {}
    query = cursor.execute("SELECT id_data, name FROM topics WHERE channel = ?",
                           [name_channel])

    for i, j in query:
        topics[i] = j
    conn.close()

    return topics


async def append_in_db_topic(data_topic: list):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    name_channel, thread_id, name_topic = data_topic
    cursor.execute("INSERT INTO topics (channel, id_data, name) VALUES (?, ?, ?)",
                   [name_channel, thread_id, name_topic])
    conn.commit()
    conn.close()

    return logging.info(f"Топик/тема `{name_topic}` - добавлен")


async def del_from_db_topic(topic):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM topics WHERE name = ?", [topic])

    conn.commit()
    conn.close()

    return logging.info(f"Топик/тема `{topic}` - удалён")


if __name__ == "__main__":
    PATH = "../DataChannelAndChat.db"
    print(asyncio.run(get_topic_from_channel("MyTestGroup")))
