import numpy as np
from typing import List, Dict
from physics.gravity import Planet, Satellite
from config import Config

# Chord intervals from root: root, 3rd, 5th, octave
CHORD_INTERVALS = {
    'major': [0, 4, 7, 12],      # Major triad + octave
    'minor': [0, 3, 7, 12],      # Minor triad + octave
    'dim': [0, 3, 6, 12],        # Diminished triad + octave
    'dom7': [0, 4, 7, 10],       # Dominant 7th
    'maj7': [0, 4, 7, 11],       # Major 7th
    'min7': [0, 3, 7, 10],       # Minor 7th 
    'dim7': [0, 3, 6, 9]         # Diminished chord
}

# Scale degree (1-7) to semitone offset in major scale
# By changing this we can do non diatonic chords if wanted
SCALE_DEGREE_TO_SEMITONE = {
    1: 0,   # I   - C
    2: 2,   # ii  - D
    3: 4,   # iii - E
    4: 5,   # IV  - F
    5: 7,   # V   - G
    6: 9,   # vi  - A
    7: 11,  # vii - B
}

def get_planet_chord_notes(planet: Planet, base_octave: int = 4) -> List[int]:
    """Returns MIDI note numbers for a specific planet's chord.
    
    The chord is built from:
    - KEY from config (e.g., C = 0)
    - chord_root as scale degree (1=I, 2=ii, 3=iii, 4=IV, 5=V, 6=vi, 7=vii)
    - quality (major, minor, dim, dom7)
    """
    # Convert scale degree to semitone offset, then add KEY
    semitone_offset = SCALE_DEGREE_TO_SEMITONE.get(planet.chord_root, 0)
    root_note = (Config.KEY + semitone_offset) % 12
    
    # Get chord intervals based on quality
    intervals = CHORD_INTERVALS.get(planet.quality, CHORD_INTERVALS['major']) # maj as default
    
    # Build chord notes
    notes = []
    for interval in intervals:
        pitch_class = (root_note + interval) % 12
        midi_note = base_octave * 12 + pitch_class
        notes.append(midi_note)
    
    return sorted(notes)

def get_dominant_planet(sat: Satellite, planets: List[Planet]) -> Planet:
    """Returns the planet with the strongest gravitational influence on the satellite."""
    max_weight = 0
    dominant = planets[0]
    for p in planets:
        dist = np.linalg.norm(p.pos - sat.pos)
        weight = p.mass / (dist + 1.0)
        if weight > max_weight:
            max_weight = weight
            dominant = p
    return dominant

def get_planet_weights(sat: Satellite, planets: List[Planet]) -> Planet:
    """Returns a list of weights of all planets, normalised to 0-1"""
    weights = []
    total_weight = 0
    for p in planets:
        dist = np.linalg.norm(p.pos - sat.pos)
        weight = p.mass / (dist + 1.0)
        weights.append(weight)
        total_weight += weight

    weights = [val/total_weight for val in weights]
    return weights

def get_interval_velocities(planets: List[Planet], weights: List) -> List:
    velocities = np.zeros(12)

    # It feels wrong to have weights and planets linked by index and nothing
    # else! But idk a better way
    for i, p in enumerate(planets):
        # Also this is copied from that function up there! I guess this can 
        # be rearranged
        semitone_offset = SCALE_DEGREE_TO_SEMITONE.get(p.chord_root, 0)
        root_note = (Config.KEY + semitone_offset) % 12
        intervals = CHORD_INTERVALS.get(p.quality, CHORD_INTERVALS['major']) # maj as default
        intervals = [(root_note + interval) % 12 for interval in intervals]
        
        for interval in intervals:
            if velocities[interval] == 0:
                velocities[interval] = weights[i]
            else:
                velocities[interval] = max(velocities[interval], weights[i])
    
    # Sorry - I'm learning to use list comprehension lol 
    velocities = [max(pow(vel, 2)-0.1, 0) for vel in velocities]
    velocities = [int(vel * 127) for vel in velocities]
    return velocities

def get_notes() -> List:
    """
    Returns chromatic notes in desired octave
    """
    base_note = (Config.BASE_OCTAVE * 12) + Config.KEY
    return np.arange(12) + base_note