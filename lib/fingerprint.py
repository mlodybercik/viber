import mmh3

def hash_frequencies(values):
    for freq1, freq2, time in values:
        yield mmh3.hash(freq1.tobytes() + freq2.tobytes() + time.tobytes())