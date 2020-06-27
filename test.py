from lib.audiohandle import divide, detect_peaks, generate_point_mesh, return_position, create_buffer, find_clips
from lib.hashtree import generate_tree, merge_trees, extract_values_from_tree
from lib.database import search_for_song_id, look_for_hashes, insert_into_temp, create_temp, clear_temp, count_in_database
from lib.constants import DEFAULTS, check_for_settings
from lib.filehandle import open_audio, hash_file
from pydub.exceptions import CouldntDecodeError
from lib.fingerprint import hash_frequencies
from pathlib import Path
import matplotlib.mlab as mlab
import numpy as np
import logging
import sqlite3
from time import time
import sys


conn = sqlite3.connect("fingerprint_database.db")

if not check_for_settings(conn, DEFAULTS):
    print("Database was created on other settings, results may differ!")


file = Path(sys.argv[1])
try:
    *_, audio_arr = open_audio(file)
except FileNotFoundError:
    print(f"Couldnt find the file, {sys.argv[1]}")
    exit(-1)
except CouldntDecodeError as e:
    print(f"Couldnt open the file, {sys.argv[1]}")
    print(e)
    exit(-1)

tests = []

print(f"Testing on {file}")
channel_count, Bps, sample_rate, audio_arr = open_audio(file)
audio_arr = create_buffer(audio_arr)
start, end = find_clips(audio_arr)
end = int(end * 0.03)

def generate_test(array, start, end):
    yield array[start:int(end*0.1)]                                # short
    if len(_ := array[start:int(end*0.05)]) > 1024:                # very short
        yield _
    yield array[start:end]*0.1                                     # silent
    yield array[start:end]*0.01                                    # very silent
    yield array[start:end]*0.001                                   # very very silent
    yield [x+np.random.randint(100) for x in array[start:end]]     # noisy
    yield [x+np.random.randint(9000) for x in array[start:end]]    # very noisy

for no, test_array in enumerate(generate_test(audio_arr, start, end)):
    print(f"#{no+1}", end="", flush=True)
    audio = divide(test_array, desired_length=DEFAULTS["DEFAULT_LENGTH"],
                sample_rate=sample_rate, overlap=DEFAULTS["DEFAULT_OVERLAP"])
    hash_tree = {}
    begin = time()
    for fragment in audio:
        # create spectrum and multiply it by 10*log10
        spectrum = mlab.specgram(fragment[0], NFFT=DEFAULTS["NFFT_SIZE"], Fs=sample_rate)
        with np.errstate(divide='ignore'):
            spectrum = 10*np.log10(spectrum[0])
        # now to detect the peaks inside
        peaks = detect_peaks(spectrum[:256])
        mesh = generate_point_mesh(return_position(peaks))
        merge_trees(hash_tree, generate_tree(mesh))
    print(", fingerprinting", end="", flush=True)
    stop = time()
    create_temp(conn)
    insert_into_temp(conn, 0, hash_frequencies(extract_values_from_tree(hash_tree)))
    hashes = count_in_database(conn, "current_recognition")
    potential_finds = {}

    for fetch in look_for_hashes(conn):
        for item in fetch:
            item = item[0]
            if item in potential_finds:
                potential_finds[item] += 1
            else:
                potential_finds[item] = 1

    clear_temp(conn)
    tests.append(potential_finds)
    print(", looking for hashes.")
    print("Generated {} unique hashes, in {:.4f} seconds. {}HPS.".format(hashes, stop-begin, round(hashes/(stop-begin))))
    print()

for no, i in enumerate(tests):
    hits = sorted(i, key=i.get, reverse=True)[:5]
    print(f"Test #{no+1}")
    for j in hits:
        name, _id = search_for_song_id(conn, j)
        print(f"Hits: {potential_finds[_id]}\tName: {name}")
    print()