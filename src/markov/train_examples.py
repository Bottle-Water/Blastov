""" from music21 import note as Note


def track_5():
    
    Returns:
        list: List of music21.note.Note objects.
    
    return [
        Note.Note("A4", quarterLength=1.5),
        Note.Note("G4", quarterLength=0.5),
        Note.Note("E4", quarterLength=1),
        Note.Note("A4", quarterLength=1),
        Note.Note("C5", quarterLength=1.5),
        Note.Note("B4", quarterLength=0.5),
        Note.Note("A4", quarterLength=1),
        Note.Note("G4", quarterLength=1),
        
        Note.Note("F4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        Note.Note("G4", quarterLength=1),
        Note.Note("A4", quarterLength=2),
        
        Note.Note("C5", quarterLength=1),
        Note.Note("B4", quarterLength=1),
        Note.Note("A4", quarterLength=1),
        Note.Note("G4", quarterLength=2),

        Note.Note("E4", quarterLength=1.5),
        Note.Note("F4", quarterLength=0.5),
        Note.Note("G4", quarterLength=1),
        Note.Note("A4", quarterLength=1.5),
        Note.Note("G4", quarterLength=0.5),
        Note.Note("E4", quarterLength=2),
    ]


def track_1():
    '''
    Creates a list of sample training notes for the melody of "Mary Had a Little Lamb".

    Returns:
        list: List of music21.note.Note objects.
    
    '''
    return [
        Note.Note("E4", quarterLength=1),
        Note.Note("D4", quarterLength=1),
        Note.Note("C4", quarterLength=1),
        Note.Note("D4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        Note.Note("E4", quarterLength=2),

        Note.Note("D4", quarterLength=1),
        Note.Note("D4", quarterLength=1),
        Note.Note("D4", quarterLength=2),
        Note.Note("E4", quarterLength=1),
        Note.Note("G4", quarterLength=1),
        Note.Note("G4", quarterLength=2),
        
        Note.Note("E4", quarterLength=1),
        Note.Note("D4", quarterLength=1),
        Note.Note("C4", quarterLength=1),
        Note.Note("D4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        
    ]

def track_2():
    Melody 2: slow, flowing, minor-key inspired.
    return [
        Note.Note("D4", quarterLength=1.5),
        Note.Note("C4", quarterLength=0.5),
        Note.Note("A3", quarterLength=1),
        Note.Note("D4", quarterLength=1),
        Note.Note("F4", quarterLength=1.5),
        Note.Note("E4", quarterLength=0.5),
        Note.Note("D4", quarterLength=1),
        Note.Note("C4", quarterLength=1),

        Note.Note("B3", quarterLength=1),
        Note.Note("A3", quarterLength=1),
        Note.Note("C4", quarterLength=1),
        Note.Note("D4", quarterLength=2),
    ]

def track_3():
Melody 3: melancholic with slight upward movement.
    return [
        Note.Note("E4", quarterLength=1),
        Note.Note("G4", quarterLength=1),
        Note.Note("F4", quarterLength=1),
        Note.Note("E4", quarterLength=1.5),
        Note.Note("D4", quarterLength=0.5),
        Note.Note("C4", quarterLength=1),
        Note.Note("E4", quarterLength=1),
        Note.Note("G4", quarterLength=1.5),
        Note.Note("F4", quarterLength=0.5),
        Note.Note("D4", quarterLength=2),
    ]

def track_4():
    Melody 4: descending minor line, simple and sad.
    return [
        Note.Note("A4", quarterLength=1),
        Note.Note("G4", quarterLength=1),
        Note.Note("F4", quarterLength=1),
        Note.Note("E4", quarterLength=1.5),
        Note.Note("D4", quarterLength=0.5),
        Note.Note("C4", quarterLength=1),
        Note.Note("B3", quarterLength=1),
        Note.Note("A3", quarterLength=2),
    ]
 """
def track_5():
    return [
        (-2, 0.5),
        (-3, 1),
        (+5, 1),
        (+3, 1.5),
        (-1, 0.5),
        (-2, 1),
        (-2, 1),

        (-2, 1),
        (-1, 1),
        (+3, 1),
        (+2, 2),

        (+3, 1),
        (-1, 1),
        (-2, 1),
        (-2, 2),

        (-3, 1.5),
        (+1, 0.5),
        (+2, 1),
        (+2, 1.5),
        (-2, 0.5),
        (-3, 2),
    ]

def track_1():
    return [
        (-2, 1),
        (-2, 1),
        (+2, 1),
        (+2, 1),
        (0, 1),
        (0, 2),

        (-2, 1),
        (0, 1),
        (0, 2),
        (+2, 1),
        (+3, 1),
        (0, 2),

        (-3, 1),
        (-2, 1),
        (+2, 1),
        (+2, 1),
        (0, 1),
        (0, 1),
    ]
def track_2():
    return [
        (-2, 0.5),
        (-3, 1),
        (+5, 1),
        (+3, 1.5),
        (-1, 0.5),
        (-2, 1),
        (-2, 1),

        (-1, 1),
        (-2, 1),
        (+3, 1),
        (+2, 2),
    ]

def track_3():
    return [
        (+3, 1),
        (-1, 1),
        (-2, 1.5),
        (-2, 0.5),
        (-2, 1),
        (+4, 1),
        (+3, 1.5),
        (-1, 0.5),
        (-3, 2),
    ]

def track_4():
    return [
        (-2, 1),
        (-2, 1),
        (-1, 1.5),
        (-2, 0.5),
        (-2, 1),
        (-1, 1),
        (-2, 2),
    ]

def track_6():
    return [
        (0, 1), (+7, 0.5), (-2, 0.5), (-5, 1),  # Octave/Fifth jumps
        (0, 1), (+5, 1), (-1, 0.5), (-4, 1.5),
        (+12, 1), (-7, 1), (-5, 2)              # Big octave drop
    ]

def track_7():
    return [
        (+1, 0.5), (+1, 0.5), (+1, 0.5), (+2, 1),
        (-1, 0.5), (-1, 0.5), (-1, 0.5), (-2, 1),
        (0, 0.5), (+1, 0.5), (-1, 0.5), (0, 2)
    ]

def track_8():
    return [
        (+2, 1), (+3, 1), (+2, 1), (-2, 1), 
        (-3, 1), (-2, 1), (0, 2),
        (+7, 1), (-2, 1), (-5, 1), (0, 2)
    ]