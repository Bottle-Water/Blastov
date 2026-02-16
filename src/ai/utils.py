from dataclasses import dataclass
from typing import Tuple
from music.harmony import ChordData

@dataclass
class PlanetGene:
    """
    Holds the chord for each planet. 

    Attributes:
        chord (ChordData): Stores the name, intervals and root.
    """
    chord: ChordData

@dataclass
class SolarSystemChromosome():
    planet_genes: Tuple[PlanetGene, ...]
