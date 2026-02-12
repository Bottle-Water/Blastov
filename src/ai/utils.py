from dataclasses import dataclass
from typing import Tuple, List
from music.harmony import ChordData

@dataclass
class PlanetGene:
    chord: ChordData
    weight: float

@dataclass
class SolarSystemChromosome():
    planet_genes: Tuple[PlanetGene, ...]
