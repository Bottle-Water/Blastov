import numpy as np
from typing import List, Tuple
from physics.gravity import Planet, calculate_gravity
from config import Config

def predict_path(start_pos: np.ndarray, start_vel: np.ndarray, planets: List[Planet], steps: int = 120, dt: float = 1.0/Config.FPS) -> List[Tuple[float, float]]:
    """
    Simulates the satellite trajectory into the future.

    Arguments:
        steps: Number of frames to predict (120 steps = 2 seconds at 60fps)
        dt: Time step (default 1/60 seconds)
    """
    path = []
    # Create temporary physics state
    temp_pos = start_pos.copy()
    temp_vel = start_vel.copy()
    
    # We use a dummy object for calculate_gravity to work
    class GhostSat:
        def __init__(self, p, v):
            self.pos = p
            self.vel = v

    ghost = GhostSat(temp_pos, temp_vel)

	# We use ghost planets to simulate the future trajectory of the real planets, to predict 
    # the future effect on the path of the sattelite
    class GhostPlanet:
        def __init__(self, p: Planet):
            self.pos = p.pos.copy()
            self.mass = p.mass
            self.orbit_center = p.orbit_center.copy() if getattr(p, "orbit_center", None) is not None else None
            self.orbit_radius = getattr(p, "orbit_radius", 0.0)
            self.angular_speed = getattr(p, "angular_speed", 0.0)
            self.angle = getattr(p, "angle", 0.0)

        def update(self, dt: float):
            if self.orbit_center is None or self.orbit_radius == 0.0 or self.angular_speed == 0.0:
                return
            self.angle += self.angular_speed * dt
            self.pos = self.orbit_center + np.array([np.cos(self.angle), np.sin(self.angle)]) * self.orbit_radius

    ghost_planets = [GhostPlanet(p) for p in planets]

    for _ in range(steps):
        # advance planets in time
        for gp in ghost_planets:
            gp.update(dt)

        force = calculate_gravity(ghost, ghost_planets)
        ghost.vel += force
        speed = np.linalg.norm(ghost.vel)
        if speed > Config.MAX_SPEED:
            ghost.vel = (ghost.vel / speed) * Config.MAX_SPEED
        ghost.pos += ghost.vel
        ghost.vel *= Config.DAMPING
        path.append((int(ghost.pos[0]), int(ghost.pos[1])))
    return path