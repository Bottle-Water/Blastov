import pygame
import numpy as np
import torch
import time
from config import Config
from physics.gravity import Planet, Satellite, calculate_gravity
from physics.orbital_mechanics import predict_path
from gui.renderer import Renderer
from music.harmony import get_planet_chord_notes, get_dominant_planet
from music.midi_output import MIDIHandler
from ai.model import HarmonicLSTM

def main():
    pygame.init()
    is_dragging = False
    dt = 1.0 / Config.FPS
    drag_start = (0,0)
    screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    renderer = Renderer(screen)
    
    # MIDI Handler
    midi = MIDIHandler(Config.MIDI_PORT_NAME)
    arp_index = 0
    last_arp_time = time.time()
    current_note = None
    source_planet = None

    # Initialize World
    system_center = np.array([Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2])

    planets = [
        Planet(pos=np.array([400, 360]), mass=10, chord_root=1, quality='major',
               orbit_center=system_center, orbit_radius=130.0, angular_speed=0.18, angle=3.14),
        Planet(pos=np.array([880, 360]), mass=10, chord_root=5, quality='major',
               orbit_center=system_center, orbit_radius=240.0, angular_speed=-0.12, angle=0.0),
        Planet(pos=np.array([640, 150]), mass=10, chord_root=7, quality='minor',
               orbit_center=system_center, orbit_radius=210.0, angular_speed=0.4, angle=1.5),
        Planet(pos=np.array([640, 150]), mass=10, chord_root=6, quality='minor',
               orbit_center=system_center, orbit_radius=100.0, angular_speed=0.22, angle=2),
    ]
    sat = Satellite(np.array([100, 100]))


    
    # AI Model
    model = HarmonicLSTM()
    model.eval()

    running = True
    while running:
        current_time = time.time()
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                is_dragging = True
                drag_start = pygame.mouse.get_pos()
                sat.freeze()

            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False
                sat.frozen = False
                drag_end = pygame.mouse.get_pos()
                launch_vector = (np.array(drag_start) - np.array(drag_end)) * 0.1
                sat.acc = np.zeros(2)
                sat.vel = launch_vector

        for p in planets:
            p.update(dt)

        # Physics Update
        force = calculate_gravity(sat, planets)
        sat.apply_force(force)
        sat.update()

        # Harmonic Context & MIDI Arpeggio
        # Get the dominant planet and use its chord
        dominant_planet = get_dominant_planet(sat, planets)
        chord_notes = get_planet_chord_notes(dominant_planet, base_octave=Config.BASE_OCTAVE)
        source_planet = dominant_planet
        

        ## DEMO TO BE REPLACED BY AI MODEL INFERENCE ##
        # Arpeggio rate based on satellite speed
        speed = np.linalg.norm(sat.vel)
        # Map speed (0-15) to arp interval (0.5s - 0.05s)
        arp_interval = max(0.05, 0.5 - (speed / Config.MAX_SPEED) * 0.45)
        


        if not sat.frozen and len(chord_notes) > 0 and (current_time - last_arp_time) > arp_interval:
            note = chord_notes[arp_index % len(chord_notes)]
            velocity = min(127, int(40 + speed * 5))  # Velocity scales with speed
            midi.send_note(note, velocity, duration=arp_interval * 0.8, current_time=current_time)
            current_note = note
            arp_index += 1
            last_arp_time = current_time
        


        # Clear current note if enough time has passed since last note
        if current_time - last_arp_time > arp_interval:
            current_note = None
        
        # Update MIDI (turn off expired notes)
        midi.update(current_time)
        
        # 4. Rendering
        renderer.draw_world(sat, planets)
        renderer.draw_hud(sat, planets, current_note, source_planet, speed)

        if is_dragging:
            current_mouse = pygame.mouse.get_pos()
            potential_vel = (np.array(drag_start) - np.array(current_mouse)) * 0.1
            path = predict_path(sat.pos, potential_vel, planets, dt=dt)
            renderer.draw_trajectory(path)

        pygame.display.flip()
        clock.tick(Config.FPS)

    midi.panic()
    pygame.quit()

if __name__ == "__main__":
    main()