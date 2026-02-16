from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    # Window
    WINDOW_WIDTH: int = 720
    WINDOW_HEIGHT: int = 720
    FPS: int = 30

    # Physics
    G: float = 200.0  # Gravitational constant
    DAMPING: float = 0.9999999
    MAX_SPEED: float = 15.0
    MIN_DISTANCE: float = 50.0  # Collision threshold

    # Music
    MIDI_PORT_NAME: str = "HarmonicGravity_Out"
    DEFAULT_BPM: int = 120
    BASE_OCTAVE: int = 5  # MIDI 60 (C4)
    KEY: int = 0  # 0=C, 1=C#, 2=D, etc.
    
    # AI
    INPUT_SIZE: int = 17 # 12 (chord (12 notes)) + 3 (history) + 1 (planet) + 1 (velocity)
    HIDDEN_SIZE: int = 32
    SEQ_LEN: int = 3
    OUTPUT_SIZE: int = 25 # Intervals -12 to +12 
    LEARNING_RATE: float = 0.001
    EPOCHS: int = 20
    