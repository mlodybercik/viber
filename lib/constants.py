from .database import get_settings
import sqlite3
import struct

DEFAULTS = {
    "MAX_FORWARD_DISTANCE": 150,
    "DEFAULT_PEAK_SIZE": 25,
    "DEFAULT_OVERLAP": 0.5,
    "DEFAULT_LENGTH": 1,
    "NFFT_SIZE": 1024
}

TYPES = {
    float: "f",
    int: "i",
    str: "s"
}

def check_for_settings(conn: sqlite3.Connection, DEF=DEFAULTS):
    defaults = {}
    for name, type_, value in get_settings(conn):
        unpacked_value = struct.unpack(type_, value)[0]
        defaults[name] = unpacked_value
    return defaults==DEFAULTS

def pack_settings():
    settings = []
    for key, value in DEFAULTS.items():
        type_ = TYPES[type(value)]
        value = struct.pack(type_, value)
        settings.append(tuple([key, type_, value]))
    return settings