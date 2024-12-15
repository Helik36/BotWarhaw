import asyncio
import sqlite3

PATH = "Admin/database/DataChannelAndChat.db"
# PATH = "../DataChannelAndChat.db"


async def get_from_db_data(table: str) -> dict:

    if not table.isidentifier():
        raise ValueError("Некорректное имя таблицы")

    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    query = f"SELECT id_data, name FROM {table}"
    names_table_data = {}
    for i, j in cursor.execute(query):
        names_table_data[i] = j
    conn.close()

    return names_table_data


async def select_id_channel(table, name):

    conn = sqlite3.connect(PATH)
    cursor = conn.cursor()

    query = f"SELECT id_data FROM {table} WHERE name = '{name}'"
    name_id = []
    for i in cursor.execute(query):
        name_id.append(i[0])
    conn.close()

    print(name_id[0])
    return name_id[0]

if __name__ == "__main__":

    PATH = "../DataChannelAndChat.db"
    asyncio.run(select_id_channel("channels", "MyTestGroup"))

