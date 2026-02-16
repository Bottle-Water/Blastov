import pygame
import numpy as np
import time
import threading
from queue import Queue
from typing import List, Any

#Local imports
from config import Config
from physics.gravity import Planet, Satellite, calculate_gravity, get_dominant_planet
from physics.orbital_mechanics import predict_path
from gui.renderer import Renderer
from music.midi_output import MIDIHandler
from music.harmony import CHORD_TYPES, int_to_note, note_to_int, ChordData, ScaleData
from genetic_engine import GeneticSolarSystemGenerator
from markov import train_examples
from markov.MarkovChainMelodyGenerator import MarkovChainMelodyGenerator 



def initialize_planets(system_center: np.ndarray) -> List["Planet"]:
    """
    Returns the initial list of planets with predefined orbits.
    
    Args:
        system_center: A numpy array representing the [x, y] center of the system.
    Returns:
        A list of Planet objects.
    """
    return [
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

def get_markov_model() -> "MarkovChainMelodyGenerator":
    """
    Initializes and trains the Markov model for melody generation.
    
    Returns:
        The trained MarkovChainMelodyGenerator instance.
    """
    
    training_data = (
        train_examples.track_1() + train_examples.track_2() +
        train_examples.track_3() + train_examples.track_4() +
        train_examples.track_5() + train_examples.track_6() +
        train_examples.track_7() + train_examples.track_8()
    )
    states = list(set(training_data))
    model = MarkovChainMelodyGenerator(states)
    model.train(training_data)
    return model

def run_ga_thread(generator: Any, current_scale: "ScaleData", queue: Queue) -> None:

    """Worker function for the genetic algorithm thread."""

    chrom, resolved = generator.run(current_scale)
    steps = generator.current_scale_steps
    queue.put({'chromosome': chrom, 'resolved': resolved, 'steps': steps})
    time.sleep(0.1)

def main():

    #Framework initialization
    pygame.init()
    dt = 1.0 / Config.FPS
    screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    renderer = Renderer(screen)

    
    # MIDI & Audio Setup
    midi = MIDIHandler(Config.MIDI_PORT_NAME)
    arp_index = 0
    last_arp_time = time.time()
    current_note = None
    source_planet = None

    # Solar system initialization
    system_center = np.array([Config.WINDOW_WIDTH // 2, Config.WINDOW_HEIGHT // 2])
    planets = initialize_planets(system_center)
    sat = Satellite(np.array([100, 100]))

    # Genetic algorithm and thread state
    ga_timer = 0
    ga_rate = 8.0
    ga_delta = 1 / ga_rate
    ga_queue = Queue()
    ga_active = False
    ga_thread = None
    ga_key_label = ''
    ga_status = ''
    current_scale = ScaleData("CMajor")
    previous_scale = None
    generator = GeneticSolarSystemGenerator(number_of_planets=len(planets))

    #Initialize Markov model for melody
    markov_model = get_markov_model()
    melody_state = markov_model._generate_starting_state() 
    last_melody_time = time.time()
    note_duration = 0
    last_melody_pitch = 72 + current_scale.root
    
    #Input State
    is_dragging = False
    drag_start = (0,0)
    running = True

    while running:
        current_time = time.time()
        ga_timer += dt
        
        #1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                is_dragging = True
                drag_start = pygame.mouse.get_pos()
                sat.freeze()

            elif event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False
                sat.frozen = False
                drag_end = pygame.mouse.get_pos()
                launch_vector = (np.array(drag_start) - np.array(drag_end)) * 0.1
                sat.acc = np.zeros(2)
                sat.vel = launch_vector

            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                ## Change key based on letter pressed
                if event.unicode in ['a','b', 'c', 'd', 'e', 'f', 'g']:
                    previous_scale = current_scale.name
                    root = event.unicode.upper()
                    flavour = 'Major'
                    
                    # Modifiers: Sharp/Flat (Up/Down), Minor (Left) 
                    if keys[pygame.K_UP]:
                        root = int_to_note[(note_to_int[root]+1)%12]
                    if keys[pygame.K_DOWN]:
                        root = int_to_note[(note_to_int[root]-1)%12]
                    if keys[pygame.K_LEFT]:
                        flavour = 'Minor'

                    new_scale = root + flavour
                    ga_key_label = f"{previous_scale}->{new_scale}"
                    current_scale = ScaleData(new_scale)
                    ga_active = True

        #2. Genetic Algorithm Management
        if ga_active and ga_timer >= ga_delta:
            ga_thread = threading.Thread(
                target=run_ga_thread,
                args=(generator, current_scale,ga_queue),
                daemon=True
            )
            ga_thread.start()
            ga_active = True
            ga_timer = 0

        #Process GA results
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
       
        #3. Physics updates
        for p in planets:
            p.update(dt)

        force = calculate_gravity(sat, planets)
        sat.apply_force(force)
        sat.update()

        #4. Music Logic (Harmonic Context & MIDI Arpeggio)
        dominant_planet = get_dominant_planet(sat, planets)
        chord_notes = sorted([interval + dominant_planet.chord.root + (Config.BASE_OCTAVE * 12) for interval in dominant_planet.chord.intervals])
        source_planet = dominant_planet

        # Arpeggio rate based on satellite speed
        speed = np.linalg.norm(sat.vel)
        arp_interval = max(0.05, 0.25 - (speed / Config.MAX_SPEED) * 0.45) * 2.5
        
        #Trigger Arpeggio (Channel 0) 
        if not sat.frozen and len(chord_notes) > 0 and (current_time - last_arp_time) > arp_interval:
            note = chord_notes[arp_index % len(chord_notes)]
            velocity = min(127, int(20 + speed * 2)) 
    
            midi.send_note(note, velocity, duration=arp_interval * 0.8, current_time=current_time, channel=0)
            current_note = note
            arp_index += 1
            last_arp_time = current_time
        
        # Clear current note if enough time has passed since last note
        if current_time - last_arp_time > arp_interval:
            current_note = None

        #5. Markov Melody Logic (Channel 1)
        if not sat.frozen and len(chord_notes) > 0:
            # Check if the previous note's time is up
           if (current_time - last_melody_time) >= note_duration: #rhythm timer/ waits until the time of the previous note is over

               # Prepare data for Markov state generation
               root_midi = 60 + dominant_planet.chord.root #rooth of the current chord
               chord_intervals = dominant_planet.chord.intervals #intervals of the chords
               scale_intervals = current_scale.intervals #current scale information

               melody_state = markov_model._generate_next_state(melody_state,
                    last_melody_pitch,    
                    root_midi,
                    scale_intervals,
                    chord_intervals)
            
               interval, duration = melody_state
               melody_midi = last_melody_pitch + interval 
            
               # Keep melody in playable range
               while melody_midi < 60:
                    melody_midi += 12
               while melody_midi > 96:
                    melody_midi -= 12

               #Timing and Velocity
               note_duration = duration * (arp_interval * 2.0)
               velocity = min(127, int(20 + speed * 2)) 

               midi.send_note(melody_midi, velocity, duration=note_duration,
                   current_time=current_time, channel=1)
               last_melody_pitch = melody_midi #keep current pitch for the next step generation
               last_melody_time = current_time

        
        # Update MIDI (note-off handling)
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