import sqlite3 as sq


with sq.connect(r'database/history.db') as con:
    database = con.cursor()
    database.execute("""CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    sex INTEGER,
    old INTEGER,
    score INTEGER)""")
