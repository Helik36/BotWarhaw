import logging
import sqlite3
from datetime import datetime

from Admin.database.actionWithDB.general_query import PATH


path = PATH


async def append_in_db_channel(channnel: dict):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    for i, j in channnel.items():
        cursor.execute("INSERT INTO channels (id_data, name) VALUES (?, ?)",
                       [i, j])
    conn.commit()
    conn.close()

    return logging.info(f"Канал `{channnel}` - добавлен")

async def del_from_db_channel(channnel):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM channels WHERE name = ?", [channnel])

    conn.commit()
    conn.close()

    return logging.info(f"Канал `{channnel}` - удалён")



# Добавить текст в БД для удаления из поста
async def append_in_db_delete_text_from_cmd(text):
    # Нужно, чтобы когда добавлятся текст со скобками, перед ним ставился слеш, иначе регулярка воспринимает как часть скрипта, а не текста
    replace_symbols = ["(", ")"]
    for symbol in replace_symbols:
        text = text.replace(f"{symbol}", f"\\{symbol}")

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("INSERT INTO DBdelete_text (text_trigger) VALUES (?)", [text])
    conn.commit()

    conn.close()
    return logging.info(f"Фильтр `{text}`  для удаления из поста - добавлен")


# Показать фильтр для удаления текста из поста
async def get_from_db_delete_text():
    conn = sqlite3.connect('database/DataChannelAndChat.db')
    cursor = conn.cursor()

    get_text = [text[0] for text in cursor.execute("SELECT text_trigger FROM DBdelete_text")]
    conn.close()

    return get_text


# Удалить из бд фильтр для удаления из поста
async def delete_from_db_delete_text_from_cmd(text):
    # Т.к ранее текст со скобками добавлялся со слешом, то и удалить его нужно со слешом
    replace_symbols = ["(", ")"]
    for symbol in replace_symbols:
        text = text.replace(f"{symbol}", f"\\{symbol}")

    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM DBdelete_text WHERE text_trigger = ?", [text])
    conn.commit()

    conn.close()
    return print(f"Фильтр `{text}` удалён")


def create_table_time_pause_post():
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS time_pause_for_post (
        id INTEGER PRIMARY KEY,
        time_end_pause_post TEXT NOT NULL
    )
    """)

    conn.commit()

    cursor.execute("INSERT INTO time_pause_for_post (time_end_pause_post) VALUES (?)", [str(datetime.now())])

    conn.commit()
    conn.close()

async def get_time_pause_post():
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    res = [text[0] for text in cursor.execute("SELECT time_end_pause_post FROM time_pause_for_post")]

    return res[0]

async def set_new_time_pause_post(time):

    conn = sqlite3.connect('database/DataChannelAndChat.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE time_pause_for_post set time_end_pause_post = ? ", [time])

    conn.commit()
    conn.close()

