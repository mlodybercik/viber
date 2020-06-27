from lib.database import insert_settings
from lib.constants import pack_settings
import sqlite3
import logging

conn = sqlite3.connect("fingerprint_database.db")
base = conn.cursor()

# there will be two tables, one containing the names of sound and id of it along with its hash
# second will hold the fingerprints
# TABLE songs = INT id, TEXT song_hash, TEXT name,
# TABLE fingerprints = INT id_of_song, INT fingerprint

print("WARNING! THIS WILL REMOVE CURRENT DATABASE")
print("ARE YOU SURE YOU WANT TO DO IT?")

if input("? [y/N] ").upper() != "Y":
    exit(-1)


base.execute("""DROP TABLE IF EXISTS songs""")
base.execute("""DROP TABLE IF EXISTS fingerprints""")
base.execute("""DROP TABLE IF EXISTS settings""")
base.execute("""DROP TABLE IF EXISTS current_recognition""")

base.execute("""CREATE TABLE songs 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, song_hash TEXT)""")

base.execute("""CREATE TABLE fingerprints
                (id_of_song INT, fingerprint INT KEY)""")

base.execute("""CREATE TABLE settings
                (name TEXT, type TEXT, value BLOB)""")

insert_settings(conn, pack_settings())

conn.commit()

logging.info("Succesfully created new database")