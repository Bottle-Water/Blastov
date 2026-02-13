import mido
import time

# Replace this with the exact name of your loopMIDI port
port_name = "loopMIDI Port 1"

try:
    outport = mido.open_output(port_name)
    print(f"Connected to {port_name}")
except Exception as e:
    print("Could not open MIDI port:", e)
    exit()

# Send a quick test chord
notes = [60, 64, 67]  # C major chord
for note in notes:
    outport.send(mido.Message('note_on', note=note, velocity=100))
time.sleep(1)
for note in notes:
    outport.send(mido.Message('note_off', note=note, velocity=0))
