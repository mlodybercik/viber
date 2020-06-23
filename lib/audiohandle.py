import numpy as np
import matplotlib.mlab as mlab
from scipy.ndimage.filters import maximum_filter
from scipy.ndimage.morphology import generate_binary_structure, binary_erosion
from .filehandle import open_audio


MAX_FORWARD_DISTANCE = 150


def create_buffer(sound):
    return np.frombuffer(sound, dtype=np.int16)

def calculate_frames(buffer, desired_length=0.3, sample_rate=48_000, overlap=0.15):
    """Calculate amount of segments that could be made out of this buffer with given
    parameters and other simple information."""
    ms = int(1000*(len(buffer)/sample_rate))
    overlap *= sample_rate
    desired_length *= sample_rate
    segments = int((len(buffer)-2*overlap)/desired_length)
    return ms, segments, int(overlap), int(desired_length)

def divide(buffer, desired_length=0.3, sample_rate=48_000, overlap=0.15) -> np.array:
    """
    Generate divided chunks.
    buffer - buffer to divide [array]
    deisred_length - lengths of divided chunks [time in seconds],
    sample_rate - sampling of buffer [n],
    overlap - how much overlap on each frame [time in seconds]
    """
    if overlap > desired_length:
        raise Exception("overlap > desired_length")
    
    ms, fragments, \
    overlap, desired_length = calculate_frames(buffer, 
                                               desired_length=desired_length,
                                               sample_rate=sample_rate,
                                               overlap=overlap)
    
    i = overlap
    while len(buffer) - i > 0:
        yield (buffer[i-overlap:i+desired_length+overlap], i-overlap)
        i += desired_length

def detect_peaks(buffer, size=25):
    local_max = maximum_filter(buffer, size=size)==buffer
    background = (buffer==0)
    eroded_background = binary_erosion(background, structure=np.ones((1,1)), border_value=1)
    detected_peaks = local_max ^ eroded_background
    return detected_peaks

def return_position(buffer_mask):
    for y, vy in enumerate(buffer_mask):
        for x, vx in enumerate(vy):
            if vx:
                yield (y, x)

def same_point(p1, p2):
    return p1[0] == p2[0] and p1[1] == p2[1]

def get_point_distance_arr(p1, p2):
    # points are in reverse order, (y, x)
    return np.sqrt((p2[1]-p1[1])**2+(p2[0]-p1[0])**2)

def get_point_distance_point(x1, y1, x2, y2):
    # points are in reverse order, (y, x)
    return np.sqrt((x2-x1)**2+(y2-y1)**2)

def generate_point_mesh(position_list):
    # y is first in the array (frequency, time)
    # i have to sort the whole list, by the x coordinate
    array = np.array(list(position_list))
    # a[a[:,1].argsort()]
    # https://stackoverflow.com/questions/2828059/sorting-arrays-in-numpy-by-column
    array = array[array[:,1].argsort()]
    # by enumerating by the x coordinate I eliminate the need for complex, and costly
    # "is behind" algorithm
    for i, point1 in enumerate(array):
        for point2 in array[i:]:
            if same_point(point1, point2):
                continue
            # first fast check if its definitely too far from us
            if point2[0] - point1[0] > MAX_FORWARD_DISTANCE or \
               point2[1] - point1[1] > MAX_FORWARD_DISTANCE:
                continue
            # now, the real check
            if get_point_distance_arr(point1, point2) > MAX_FORWARD_DISTANCE:
                continue
            # point2 - point1 is a valid point, now time to create raw hash data
            assert point2[1]-point1[1] >= 0
            #          freq1,     freq2,          delta_time
            yield (point1[0], point2[0], point2[1]-point1[1])