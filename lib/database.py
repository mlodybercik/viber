from types import GeneratorType as Generator
from typing import Union, List
import sqlite3
import numpy as np

def insert_into_songs(conn: sqlite3.Connection, name: str, hash_: str) -> int:
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO songs(name, song_hash)
                    VALUES (?, ?)""", (name, hash_))
    conn.commit()
    cursor.execute("""SELECT id FROM songs WHERE song_hash LIKE (?)""", [hash_])
    return cursor.fetchone()[0]

def add_id(fingerprint, id_):
    return (id_, fingerprint)

def split_and_generate(data: Union[list, Generator], id_: int, how_big: int = 1500, to_id: bool = True, add_id = add_id):
    # this will split the data into smaller chunks that can be processed by sqlite3
    if not to_id:
        add_id = lambda a, b: a
    else:
        add_id = add_id
    if type(data) == Generator:
        try:
            while True: # TODO: fix while True, its very dangerous
                t = []
                for _ in range(how_big):
                    t.append(add_id(next(data), id_))
                yield t
        except StopIteration:
            yield t
    else:
        chunks = np.ceil(len(data)/how_big)
        for i in range(chunks-1):
            t = []
            for i in data[i*how_big: (i+1)*how_big]:
                t.append(add_id(i, id_))
            yield t

def insert_into_fingerprints(conn: sqlite3.Connection, id_: int, fingerprints) -> None:
    cursor = conn.cursor()
    for fingerprint in split_and_generate(fingerprints, id_):
        cursor.executemany("""INSERT INTO fingerprints(id_of_song, fingerprint)
                              VALUES (?, ?)""", fingerprint)
    conn.commit()

def search_for_song_hash(conn: sqlite3.Connection, hash_: str) -> tuple:
    cursor = conn.cursor()
    cursor.execute("""SELECT name, id FROM songs WHERE song_hash=(?)""", [hash_])
    return cursor.fetchone()

def search_for_song_id(conn: sqlite3.Connection, id_: int) -> tuple:
    cursor = conn.cursor()
    cursor.execute("""SELECT name, id FROM songs WHERE id=(?)""", [id_])
    return cursor.fetchone()

def get_settings(conn: sqlite3.Connection) -> List[tuple]:
    cursor = conn.cursor()
    cursor.execute("""SELECT name, type, value FROM settings""")
    return cursor.fetchmany(100)

def insert_settings(conn: sqlite3.Connection, settings: List[tuple]) -> None:
    cursor = conn.cursor()
    cursor.executemany("""INSERT INTO settings(name, type, value)
                          VALUES(?,?,?)""", settings)
    conn.commit()

def insert_into_temp(conn: sqlite3.Connection, id_: int, fingerprints) -> None:
    cursor = conn.cursor()
    for fingerprint in split_and_generate(fingerprints, id_, to_id=True, add_id=lambda b, c: tuple([b])):
        cursor.executemany("""INSERT INTO current_recognition(fingerprint)
                            VALUES (?)""", tuple(fingerprint))
    conn.commit()

def look_for_hashes(conn: sqlite3.Connection, amount_to_fetch: int = 998) -> List[tuple]:
    cursor = conn.cursor()
    cursor.execute(f"""SELECT id_of_song
                       FROM fingerprints
                       WHERE fingerprint IN (
                           SELECT fingerprint FROM current_recognition)""")
    
    while fetch := cursor.fetchmany(amount_to_fetch):
        yield fetch

def create_temp(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""CREATE TEMP TABLE IF NOT EXISTS current_recognition
                      (fingerprint INT STORAGE MEMORY KEY)""")
    conn.commit()

def clear_temp(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""DELETE FROM current_recognition WHERE 1""")
    conn.commit()

def count_in_database(conn: sqlite3.Connection, database: str) -> int:
    cursor = conn.cursor()
    cursor.execute(f"""SELECT COUNT(*) FROM ({database})""")
    return cursor.fetchone()[0]