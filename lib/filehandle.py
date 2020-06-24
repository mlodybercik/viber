from pydub import AudioSegment
from pathlib import Path
from hashlib import sha1
import logging
import os

def hash_file(filename):
    """Returns file hash"""
    func = sha1()
    with open(str(filename), "rb") as file:
        func.update(file.read())
    return func.hexdigest().upper()

def open_audio(filename):
    """Opens file with pydub and returns its raw data and info"""
    ext = filename.name.split(".")[-1]
    audio_file = AudioSegment.from_file(str(filename), ext)
    # TODO, temporary fix.
    audio_file = audio_file.strip_silence()
    channel_count = audio_file.channels
    bytes_per_sample = audio_file.sample_width
    sample_rate = audio_file.frame_rate
    logging.info("Opened %s, %s, %s, %s", filename, channel_count, bytes_per_sample, sample_rate)
    return (channel_count, bytes_per_sample,\
            sample_rate, audio_file.get_array_of_samples())

def walk_paths():
    paths = []
    for root, _, files in os.walk("input/", topdown=False):
        for name in files:
            if os.path.join(root, name)[-3:] in ["wav", "mp3"]:
                paths.append(Path(os.path.join(root, name)))
    return paths