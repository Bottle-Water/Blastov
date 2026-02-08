from dataclasses import dataclass
from typing import Tuple, List
from music_data import ChordData

@dataclass
class PlanetGene:
    chord: ChordData
    weight: float

@dataclass
class SolarSystemChromosome():
    planet_genes: Tuple[PlanetGene, ...]
