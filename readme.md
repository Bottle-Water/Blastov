# Blastov!

**Final Project: Generative music tool**

This project creates a "Solar system" generative music tool. It consists of a genetic algorithm creating chord progressions and a Markov chain model creating a melody on top of that, based on a Physics-based UI.


## Prerequisites

- **Python 3.10**
- **pip** (Python package manager)
- *(Optional)* **MuseScore 4** installed on Windows (for automatic score visualization).

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd final-project-generative-music-tool-zoda

   ```

2. **Install dependencies:**
   ```pip install -r requirements.txt```

## Usage

Run the main script to start the evolution process:

```Bash
python main.py
```

-  Open a DAW session that contains two tracks with VSTs on. Select HarmonicGravity_Out as your MIDI input, with each channel (1/2) routed to a different track.

- Click and drag to aim and fire satellite.

- Choose your key by pressing the corresponding key on your keyboard, e.g. press 'G' to modulate to G major. Hold the up or down key while choosing your modulation to access e.g. G# or Gb, and hold the left key to access minor keys.


