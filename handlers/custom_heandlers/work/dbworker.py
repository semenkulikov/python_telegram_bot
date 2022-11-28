import sqlite3 as sq

path = r'database\history.db'


def create_tables() -> None:
    """ Функция для создания БД и создания таблиц """
    with sq.connect(path) as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS history(
               id INTEGER PRIMARY KEY autoincrement,
               uid TEXT,
               chat_id TEXT,
               datetime TEXT,
               city TEXT,
               command TEXT);
            """)
        cur.execute("""CREATE TABLE IF NOT EXISTS hotels(
               id INTEGER PRIMARY KEY autoincrement,
               uid TEXT,
               hotel_id TEXT,
               name TEXT,
               address TEXT,
               price TEXT,
               link TEXT);
            """)
        cur.execute("""CREATE TABLE IF NOT EXISTS photos(
                 id INTEGER PRIMARY KEY autoincrement,
                 hotel_id TEXT,
                 photo TEXT);
              """)


def get_data(string: str) -> list:
    """ Функция для получения данных из БД в зависимости от запроса """
    with sq.connect(path) as con:
        cur = con.cursor()
        cur.execute(string)
        return cur.fetchall()


def delete_tables(*args) -> None:
    """ Функция для удаления таблиц из БД """
    with sq.connect(path) as con:
        cur = con.cursor()
        for table in args:
            cur.execute(f"DROP TABLE IF EXISTS {table}")


def delete_data(*args) -> None:
    """ Функция для удаления данных из таблиц """
    with sq.connect(path) as con:
        cur = con.cursor()
        for table in args:
            cur.execute(f"DELETE FROM {table}")
    with sq.connect(path) as con:
        cur = con.cursor()
        for _ in args:
            cur.execute("VACUUM")


def get_all_from_table(table: str) -> list:
    """ Функция для получения всех данных из одной таблицы """
    with sq.connect(path) as con:
        cur = con.cursor()
        cur.execute(f"SELECT * from {table}")
        return cur.fetchall()


def set_data(string, values=tuple(), multiple=False) -> bool:
    """ Функция для записи данных в БД """
    with sq.connect(path) as con:
        cur = con.cursor()
        if multiple:
            cur.executemany(string, values)
        elif len(values) != 0:
            cur.execute(string, values)
        else:
            cur.execute(string)
        return True


def set_history(history: tuple) -> bool:
    """ Функция для записи данных в таблицу history """
    return set_data(
        string=f"INSERT INTO history(uid, chat_id, datetime, city, command)"
               f"VALUES(?, ?, ?, ?, ?);",
        values=history)


def get_history(chat_id: str) -> list:
    """ Функция для получения данных из таблицы history """
    history = get_data(
        string=f"SELECT uid, chat_id, datetime, city, command from history WHERE chat_id = '{chat_id}'")
    return history


def get_hotels(uid: str) -> list:
    """ Функция для получения данных из таблицы hotels """
    hotels = get_data(
        string=f"SELECT uid, hotel_id, name, address, price, link from hotels WHERE uid = '{uid}'")
    return hotels


def set_hotels(hotels: tuple) -> bool:
    """ Функция для записи данных в таблицу hotels """
    return set_data(
        string=f"INSERT INTO hotels(uid, hotel_id, name, address, price, link)"
               f"VALUES(?, ?, ?, ?, ?, ?);",
        values=hotels)


def set_photos(photos: tuple) -> bool:
    """ Функция для записи данных в таблицу photos """
    return set_data(string=f"INSERT INTO photos(hotel_id, photo) VALUES(?, ?);", values=photos)


def get_photos(hotel_id: str) -> list:
    """ Функция для получения данных из таблицы photos """
    return get_data(f"SELECT photo from photos WHERE hotel_id = '{hotel_id}'")


def clear_database():
    delete_data('history')
    delete_data('hotels')
    delete_data('photos')
