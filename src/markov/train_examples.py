"""
Melodic Training Data for Markov Chain Generation.

This module contains a collection of 'tracks' used to train the MarkovChainMelodyGenerator.
Each track is represented as a list of tuples following the format:
    (interval, duration)

Definitions:
    - Interval (int): The relative jump from the previous note in semitones 
    - Duration (float): The length of the note in beats 
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
        (0, 1), (+7, 0.5), (-2, 0.5), (-5, 1), 
        (0, 1), (+5, 1), (-1, 0.5), (-4, 1.5),
        (+12, 1), (-7, 1), (-5, 2)              
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