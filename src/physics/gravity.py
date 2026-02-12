import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple
from config import Config
from music.harmony import ChordData

@dataclass
class Planet:
    pos: np.ndarray  # [x, y]
    mass: float
    #chord_root: int  # 0-11
    #quality: str  # 'major', 'minor', 'dim'
    chord: ChordData
    radius: float = 30.0
    # Orbit parameters (optional)
    orbit_center: np.ndarray = None
    orbit_radius: float = 0.0
    angular_speed: float = 0.0  # radians / second
    angle: float = 0.0

    def update(self, dt: float = 1.0 / Config.FPS):
        """Advance planet along circular orbit if parameters are set."""
        if self.orbit_center is None or self.orbit_radius == 0.0 or self.angular_speed == 0.0:
            return
        self.angle += self.angular_speed * dt
        self.pos = self.orbit_center + np.array([np.cos(self.angle), np.sin(self.angle)]) * self.orbit_radius

class Satellite:
    def __init__(self, pos: np.ndarray):
        self.pos = pos.astype(float)
        self.vel = np.zeros(2, dtype=float)
        self.acc = np.zeros(2, dtype=float)
        self.history: List[np.ndarray] = []
        self.frozen = True

    def apply_force(self, force: np.ndarray):
        self.acc += force

    def update(self):
        if not self.frozen:
            self.vel += self.acc
            # Limit speed
            speed = np.linalg.norm(self.vel)
            if speed > Config.MAX_SPEED:
                self.vel = (self.vel / speed) * Config.MAX_SPEED
                
            self.pos += self.vel
            self.vel *= Config.DAMPING
            self.acc *= 0
            
            # Trail history
            self.history.append(self.pos.copy())
            if len(self.history) > 50:
                self.history.pop(0)

    def freeze(self):
        self.vel = np.zeros(2, dtype=float)
        self.acc = np.zeros(2, dtype=float)
        self.frozen = True

def calculate_gravity(sat: Satellite, planets: List[Planet]) -> np.ndarray:
    total_force = np.zeros(2)
    for p in planets:
        diff = p.pos - sat.pos
        dist = np.linalg.norm(diff)
        dist = max(dist, Config.MIN_DISTANCE) # Prevent division by zero
        
        force_mag = (Config.G * p.mass) / (dist ** 2)
        total_force += (diff / dist) * force_mag
    return total_force

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