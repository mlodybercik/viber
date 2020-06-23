from lib.audiohandle import divide, detect_peaks, generate_point_mesh, return_position, create_buffer
from lib.hashtree import generate_tree, merge_trees, extract_values_from_tree
from lib.database import look_for_hashes, search_for_song_id
from lib.filehandle import open_audio, hash_file
from lib.fingerprint import hash_frequencies
from pathlib import Path
import matplotlib.mlab as mlab
import numpy as np
import logging
import sqlite3
import sys

conn = sqlite3.connect("fingerprint_database.db")
file = Path(sys.argv[1])
try:
    channel_count, Bps, sample_rate, audio_arr = open_audio(file)
except FileNotFoundError:
    print(f"Couldnt find the file, f{sys.argv[1]}")
    exit(-1)
print(f"Parsing {file}")
channel_count, Bps, sample_rate, audio_arr = open_audio(file)
audio_arr = create_buffer(audio_arr)
# mp3 seem kinda bugged, so we are skipping first and last two seconds of data
if file.name.split(".")[-1] == "mp3":
    audio_arr = audio_arr[2*sample_rate:-2*sample_rate]
audio = divide(audio_arr, desired_length=1, sample_rate=sample_rate, overlap=0.5)
hash_tree = {}
for fragment in audio:
    # create spectrum and multiply it by 10*log10
    spectrum = mlab.specgram(fragment[0], NFFT=1024, Fs=sample_rate)
    with np.errstate(divide='ignore'):
        spectrum = 10*np.log10(spectrum[0])
    # now to detect the peaks inside
    peaks = detect_peaks(spectrum[:256])
    mesh = generate_point_mesh(return_position(peaks))
    merge_trees(hash_tree, generate_tree(mesh))
print("Fingerprinting complete")

potential_finds = {}

for fetch in look_for_hashes(conn, 
                             hash_frequencies(extract_values_from_tree(hash_tree))):
    for item in fetch:
        if item in potential_finds:
            potential_finds[item] += 1
        else:
            potential_finds[item] = 1

three = sorted(potential_finds)[-3:]
for i in three:
    name, _id = search_for_song_id(conn, i[0])
    print(f"{name} {_id}")
    