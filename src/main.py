import pygame
import numpy as np
import time
from config import Config
import threading
from queue import Queue
from physics.gravity import Planet, Satellite, calculate_gravity, get_dominant_planet
from physics.orbital_mechanics import predict_path
from gui.renderer import Renderer
from music.midi_output import MIDIHandler
from music.harmony import CHORD_TYPES, ChordData, ScaleData, int_to_note, note_to_int
from genetic_engine import GeneticSolarSystemGenerator

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

    # Initialize solar system
    system_center = np.array([Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2])
    planets = [
        Planet(pos=np.array([400, 360]), mass=10, chord=ChordData(0, CHORD_TYPES[0]),
               orbit_center=system_center, orbit_radius=130.0, angular_speed=0.18, angle=3.14),
        Planet(pos=np.array([880, 360]), mass=10, chord=ChordData(0, CHORD_TYPES[0]),
               orbit_center=system_center, orbit_radius=240.0, angular_speed=-0.12, angle=0.0),
        Planet(pos=np.array([640, 150]), mass=10, chord=ChordData(0, CHORD_TYPES[0]),
               orbit_center=system_center, orbit_radius=210.0, angular_speed=0.4, angle=1.5),
        Planet(pos=np.array([640, 150]), mass=10, chord=ChordData(0, CHORD_TYPES[0]),
               orbit_center=system_center, orbit_radius=100.0, angular_speed=0.22, angle=2),
        Planet(pos=np.array([640, 150]), mass=10, chord=ChordData(0, CHORD_TYPES[0]),
               orbit_center=system_center, orbit_radius=70.0, angular_speed=0.42, angle=0.7),
    ]
    sat = Satellite(np.array([100, 100]))

    # Genetic algorithm and thread state
    """
    The genetic algorithm is run step-by-step, rather than running until completion
    in a batch. This way, we can show the evolutionary process of the algorithm as it 
    shifts keys. 
    """
    ga_timer = 0
    ga_rate = 8.0
    ga_delta = 1/ga_rate
    ga_queue = Queue()
    ga_active = False
    ga_thread = None
    ga_key_label = ''
    ga_status = ''
    current_scale = ScaleData("CMajor")
    previous_scale = None
    generator = GeneticSolarSystemGenerator(number_of_planets=len(planets))

    def run_ga(generator, current_scale):
        chrom, resolved = generator.run(current_scale)
        steps = generator.current_scale_steps
        ga_queue.put({'chromosome': chrom, 'resolved': resolved,
                      'steps': steps})
        time.sleep(0.1)
    
    running = True
    while running:
        current_time = time.time()
        ga_timer += dt
        
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

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                #When note name key pressed, change to that key.
                if event.unicode in ['a','b', 'c', 'd', 'e', 'f', 'g']:
                    previous_scale = current_scale.name
                    root = event.unicode.upper()
                    flavour = 'Major'
                    #Holding the up or down key at the same time makes it 
                    #sharp or flat. 
                    if keys[pygame.K_UP]:
                        root = int_to_note[(note_to_int[root]+1)%12]
                    if keys[pygame.K_DOWN]:
                        root = int_to_note[(note_to_int[root]-1)%12]
                    #Holding left gets the minor key.
                    if keys[pygame.K_LEFT]:
                        flavour = 'Minor'
                    new_scale = root + flavour
                    ga_key_label = f"{previous_scale}->{new_scale}"
                    current_scale = ScaleData(new_scale)
                    ga_active = True

        #Get next chord state when the timer triggers. 
        if ga_active and ga_timer >= ga_delta:
            ga_thread = threading.Thread(
                target=run_ga,
                args=(generator, current_scale,),
                daemon=True
            )
            ga_thread.start()
            ga_active = True
            ga_timer = 0

        #Get ga result
        if ga_active and not ga_queue.empty():
            ga_result = ga_queue.get()

            for i, gene in enumerate(ga_result["chromosome"].planet_genes):
                planets[i].chord = gene.chord

            if generator.current_scale_steps >= generator.max_gens:
                ga_status = "Didn't resolve"
                ga_active = False
            elif ga_result['resolved']:
                ga_status = 'Resolved'
                ga_active = False
            else:
                ga_status = f"{ga_result["steps"]} steps"

        for p in planets:
            p.update(dt)

        # Physics Update
        force = calculate_gravity(sat, planets)
        sat.apply_force(force)
        sat.update()

        # Harmonic Context & MIDI Arpeggio
        # Get the dominant planet and use its chord
        dominant_planet = get_dominant_planet(sat, planets)
        chord_notes = sorted([interval + dominant_planet.chord.root + (Config.BASE_OCTAVE * 12) for interval in dominant_planet.chord.intervals])
        source_planet = dominant_planet
        
        # Arpeggio rate based on satellite speed
        speed = np.linalg.norm(sat.vel)
        # Map speed (0-15) to arp interval (0.5s - 0.05s)
        arp_interval = max(0.025, 0.25 - (speed / Config.MAX_SPEED) * 0.45)
        
        #Iterate through the arpeggio 
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
        
        # Rendering
        renderer.draw_world(sat, planets)
        renderer.draw_hud(sat, planets, current_note, source_planet, speed, ga_key_label, ga_status)

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