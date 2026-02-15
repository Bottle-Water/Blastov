from typing import Dict, Tuple

# Constants and Mappings
CHORD_TYPES = [
    {"maj7":    (0, 4, 7, 11)},
    {"minmaj7": (0, 3, 7, 11)},
    {"7":       (0, 4, 7, 10)},
    {"min7":    (0, 3, 7, 10)},
    {"dim7":    (0, 3, 6, 9)},
    {"maj9":    (0, 4, 7, 11, 2)},
    {"maj7#11": (0, 4, 7, 11, 6)},
    {"min7add4": (0, 3, 7, 10, 4)}
]

SCALE_TYPES = {"Major": [0, 2, 4, 5, 7, 9, 11],
               "Minor": [0, 2, 3, 5, 7, 8, 10]}

note_to_int={'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 
             'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
int_to_note={0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#',
             7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}


# Classes initialization
class ChordData:
    """
    Represents a musical chord with a root and interval structure.
    """
    def __init__(self, root: int, chord_type: Dict[str, Tuple[int, ...]]) -> None:
        """
        Initializes the ChordData object.

        Args:
            root (int): The MIDI root note (0-11) representing the chord base.
            chord_type (dict): A single-entry dictionary from CHORD_TYPES containing 
                               the name and interval tuple.
        
        Returns:
            None
        """  
        self.root = root
        self.intervals = list(list(chord_type.values())[0])
        self.flavour = list(chord_type.keys())[0]
        self.name = int_to_note[self.root] + self.flavour

    def update_name(self) -> None:
        """
        Updates the name string based on the current root and flavour.
        Used if the root is modified through mutation.
        """
        self.name = int_to_note[self.root] + self.flavour


class ScaleData:
    """
    Holds the name, root and interval pattern of a scale. 
    """
    def __init__(self, name: str) -> None:
        self.name = name
        
        #Seperate the input into root and chord type
        mode_pos = 1
        for i, c in enumerate(self.name):
            if not c.isalnum():
                mode_pos = i+1

        self.root = note_to_int[self.name[:mode_pos]]
        self.intervals = SCALE_TYPES[self.name[mode_pos:]]



