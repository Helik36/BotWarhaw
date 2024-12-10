import sqlite3
from config_for_DB import PATH

path = PATH

async def append_in_db_topic(topic: dict):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    for i, j in topic.items():
        print(f"{j} - {i}")
        cursor.execute("INSERT INTO channels (id_channel, name_channel) VALUES (?, ?)",
                       [j, i]) # обрати внимание на порядок переменных
    conn.commit()
    conn.close()

    return print(f"Топик/тема `{topic}` - добавлен")


async def del_from_db_topic(channnel):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM channels WHERE name_channel = ?", [channnel])

    conn.commit()
    conn.close()

    return print(f"Топик/тема `{channnel}` - удалён")