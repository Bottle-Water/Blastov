from dataclasses import dataclass
from typing import Tuple, List

CHORD_TYPES = [
    {"maj7":    (0, 4, 7, 11)},
    {"7":       (0, 4, 7, 10)},
    {"min7":    (0, 3, 7, 10)},
    {"minmaj7": (0, 3, 7, 11)},
    {"dim7":    (0, 3, 6, 9)}
]

@dataclass
class ChordData:
    """
    Represents a chord.

    Attributes:
        name (str): The chord symbol (e.g. "Dm7")
        root (int): The interval, 0-11, that represents the root
        intervals (Tuple[int, ...]): Intervals relative to the root
    """
    name: str
    root: int
    intervals: Tuple[int, ...]

SCALE_TYPES = {"Major": [0, 2, 4, 5, 7, 9, 11],}

@dataclass
class ScaleData:
    root: int
    intervals: Tuple[int, ...] #maybe replace with some representation of a mode 

note_to_int={'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 
             'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
int_to_note={0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#',
             7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}