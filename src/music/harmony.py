import numpy as np
from typing import List, Dict
from config import Config

CHORD_TYPES = [
    {"maj7":    (0, 4, 7, 11)},
    {"minmaj7": (0, 3, 7, 11)},
    {"7":       (0, 4, 7, 10)},
    {"min7":    (0, 3, 7, 10)},
    {"dim7":    (0, 3, 6, 9)},
    {"maj9":    (0, 2, 4, 7, 11)},
    {"maj7#11": (0, 4, 6, 7, 11)},
    {"min7add4": (0, 3, 5, 7, 10)}
]

class ChordData:
    """
    Represents a chord.

    Attributes:
        name (str): The chord symbol (e.g. "Dm7")
        root (int): The interval, 0-11, that represents the root
        intervals (Tuple[int, ...]): Intervals relative to the root
    """
    def __init__(self, root: int, chord_type: dict):   
        self.root = root
        self.intervals = list(list(chord_type.values())[0])
        self.flavour = list(chord_type.keys())[0]
        self.name = int_to_note[self.root] + self.flavour

    def update_name(self):
        self.name = int_to_note[self.root] + self.flavour

SCALE_TYPES = {"Major": [0, 2, 4, 5, 7, 9, 11],
               "Minor": [0, 2, 3, 5, 7, 8, 10]}

class ScaleData:
    def __init__(self, name):
        self.name = name
        mode_pos = 1
        for i, c in enumerate(self.name):
            if not c.isalnum():
                mode_pos = i+1
        self.root = note_to_int[self.name[:mode_pos]]
        self.intervals = SCALE_TYPES[self.name[mode_pos:]]

note_to_int={'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 
             'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
int_to_note={0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#',
             7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}


def get_notes() -> List:
    """
    Returns chromatic notes in desired octave
    """
    base_note = (Config.BASE_OCTAVE * 12) + Config.KEY
    return np.arange(12) + base_note