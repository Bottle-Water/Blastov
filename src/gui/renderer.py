from importlib.resources import path
import pygame
from typing import List, Tuple
from physics.gravity import Planet, Satellite
import numpy as np

class Renderer:
    def __init__(self, screen: pygame.Surface):
        """Initializes the renderer with a pygame surface and default font."""
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 18)
        self.sat_angle = 0

    def draw_world(self, sat: Satellite, planets: List[Planet]) -> None:
        """Renders the space background, planets, orbits, and the satellite."""
        self.screen.fill((10, 10, 25)) # Deep space blue

        # Draw Trail
        if len(sat.history) > 2:
            pygame.draw.lines(self.screen, (100, 100, 255), False, [p for p in sat.history], 2)

        # Draw Planets
        for p in planets:
            # draw orbit (if any)
            if getattr(p, "orbit_center", None) is not None and getattr(p, "orbit_radius", 0) > 1:
                pygame.draw.circle(self.screen, (40, 40, 60), p.orbit_center.astype(int), int(p.orbit_radius), 1)

            color = p.color
            pygame.draw.circle(self.screen, color, p.pos.astype(int), int(p.radius))
            # Label
            label = self.font.render(p.chord.name, True, (255, 255, 255))
            self.screen.blit(label, (p.pos[0] - 20, p.pos[1] + p.radius + 5))

        # Draw Satellite as triangle pointing in velocity direction
        size = 12
        if np.linalg.norm(sat.vel) > 0.5:
            # Calculate angle from velocity
            angle = np.arctan2(sat.vel[1], sat.vel[0])
            self.sat_angle = angle

        

        # Define triangle points (isosceles triangle pointing right initially)
        # Tip at (size, 0), base corners at (-size/2, size/2) and (-size/2, -size/2)
        triangle = np.array([
            [size, 0],           # tip
            [-size/2, size/2],   # base bottom
            [-size/2, -size/2]   # base top
        ])
        
        # Rotation matrix
        cos_a = np.cos(self.sat_angle)
        sin_a = np.sin(self.sat_angle)
        rotation = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        
        # Rotate and translate to satellite position
        rotated = triangle @ rotation.T + sat.pos
        
        pygame.draw.polygon(self.screen, (255, 255, 255), rotated.astype(int))

        ## If booster is active, draw a flame
        if sat.show_booster:
            flame_length = 10
            flame_width = 5
            # Flame points (pointing left from the back of the triangle)
            flame = np.array([
                [-size/2 - flame_length, 0],  # tip of the flame
                [-size/2, flame_width/2],     # top of the base
                [-size/2, -flame_width/2]     # bottom of the base
            ])

            # rotate thrust based on thrust angle 
            angle = sat.thrust_angle
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            rotation_local = np.array([[cos_a, sin_a], [sin_a, -cos_a]])
            flame = flame @ rotation_local.T
            rotated_flame = flame @ rotation.T + sat.pos
            pygame.draw.polygon(self.screen, (255, 100, 0), rotated_flame.astype(int))

    

    def draw_trajectory(self, path: List[Tuple[int, int]]):
        """Draws the predicted path as a series of small dots."""
        for point in path[::3]:  # Draw every 3rd point
            pygame.draw.circle(self.screen, (150, 150, 150), point, 2)
    
    def draw_hud(self, sat: Satellite, planets: List[Planet], current_note: int = None, 
                 source_planet: Planet = None, speed: float = 0.0, ga_key_label: str = '', 
                 ga_status: str = ''):
        """Draws HUD with MIDI output info and planet distances."""

        y_offset = 10
        line_height = 25
        
        # Speed
        speed_text = self.font.render(f"Speed: {speed:.2f}", True, (255, 255, 255))
        self.screen.blit(speed_text, (10, y_offset))
        y_offset += line_height
        
        # Current MIDI output
        if current_note is not None and source_planet is not None:
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_name = note_names[current_note % 12]
            octave = (current_note // 12) - 1
            
            midi_text = self.font.render(f"Playing: {note_name}{octave} (MIDI {current_note})", True, (100, 255, 100))
            self.screen.blit(midi_text, (10, y_offset))
            y_offset += line_height
            
            chord_text = self.font.render(f"From: {source_planet.chord.name}", True, (100, 255, 100))
            self.screen.blit(chord_text, (10, y_offset))
            y_offset += line_height
        
        # Distances to planets
        y_offset += 10
        dist_header = self.font.render("Distances:", True, (200, 200, 255))
        self.screen.blit(dist_header, (10, y_offset))
        y_offset += line_height
        
        for i, p in enumerate(planets):
            dist = np.linalg.norm(p.pos - sat.pos)
            dist_text = self.font.render(f"  {p.chord.name}: {dist:.1f}px", True, (180, 180, 180))
            self.screen.blit(dist_text, (10, y_offset))
            y_offset += line_height

        # Displays genetic algorithm status
        dist_text = self.font.render(f"{ga_key_label}: {ga_status}", True, (180, 180, 180))
        self.screen.blit(dist_text, (10, 670))