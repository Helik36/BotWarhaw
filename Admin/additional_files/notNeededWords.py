import sqlite3

async def upd_delete_text():
    conn = sqlite3.connect(
        'database/DBnotNeededWords.db')  # Тут надо менять путь в зависимости от того, где запускаешь файл
    cursor = conn.cursor()

    DELETE_TEXT = [row[0] for row in cursor.execute("SELECT text_trigger FROM DBdelete_text")]
    conn.close()

    for text in range(len(DELETE_TEXT)):
        DELETE_TEXT[text] = DELETE_TEXT[text].replace(f"\\", "")

    return DELETE_TEXT


async def upd_stop_post():
    conn = sqlite3.connect(
        'database/DBnotNeededWords.db')  # Тут надо менять путь в зависимости от того, где запускаешь файл
    cursor = conn.cursor()

    STOP_POST = [row[0] for row in cursor.execute("SELECT text_stop_post_trigger FROM DBstop_post")]
    conn.close()

    for text in range(len(STOP_POST)):
        STOP_POST[text] = STOP_POST[text].replace(f"\\", "")

    return STOP_POST


if __name__ == "__main__":
    conn = sqlite3.connect(
        '../database/DBnotNeededWords.db')  # Тут надо менять путь в зависимости от того, где запускаешь файл
    cursor = conn.cursor()

    DELETE_TEXT = [row[0] for row in cursor.execute("SELECT text_trigger FROM DBdelete_text")]
    STOP_POST = [row[0] for row in cursor.execute("SELECT text_stop_post_trigger FROM DBstop_post")]

    conn.close()
    print(DELETE_TEXT)
    print(STOP_POST)
