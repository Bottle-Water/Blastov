# Blastov!

**Final Project: Generative music tool**

This project creates a "Solar system" generative music tool. It consists of a genetic algorithm creating chord progressions and a Markov chain model creating a melody on top of that, with a physics-based UI.


## Prerequisites

- **Python 3.10**
- **pip** (Python package manager)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/upf-smc-genai-music/final-project-generative-music-tool-zoda.git
   cd final-project-generative-music-tool-zoda

   ```

2. **Install dependencies:**
   ```pip install -r requirements.txt```

## Usage

Run the main script to start:

```Bash
python main.py
```

-  Open a DAW session that contains two tracks with VSTs on. Select HarmonicGravity_Out as your MIDI input, with each channel (1/2) routed to a different track.

- Click and drag to aim and fire satellite.

- Choose your key by pressing the corresponding key on your keyboard, e.g. press 'G' to modulate to G major. Hold the up or down key while choosing your modulation to access e.g. G# or Gb, and hold the left key to access minor keys.

- Happy orbitting!

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
