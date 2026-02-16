import mido

class MIDIHandler:
    def __init__(self, port_name: str):
        try:
            self.out_port = mido.open_output(port_name, virtual=True)
            print(f"MIDI Port '{port_name}' opened.")
        except Exception as e:
            print(f"Could not open MIDI port: {e}. Defaulting to first available.")
            try:
                self.out_port = mido.open_output()
            except:
                print("No MIDI outputs available. Running without MIDI.")
                self.out_port = None
        
        self.active_notes = {}  # {note: time_to_off}
        self.last_arp_time = 0.0

    def update(self, current_time: float):
        """Turn off notes that have expired."""
        if not self.out_port:
            return
        notes_to_remove = []
        for key, off_time in self.active_notes.items(): #key is (note, channel)
            if current_time >= off_time:
                note, channel = key
                msg_off = mido.Message('note_off', note=note, velocity=0, channel=channel)
                self.out_port.send(msg_off)
                notes_to_remove.append(key)
        for key in notes_to_remove:
            del self.active_notes[key]

    def send_note(self, note: int, velocity: int, duration: float, current_time: float, channel: int):
        """Sends a note_on and schedules note_off."""
        if not self.out_port:
            return
        msg_on = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
        self.out_port.send(msg_on)
        self.active_notes[(note, channel)] = current_time + duration

    def panic(self):
        """Turn off all notes immediately."""
        if not self.out_port:
            return
        for (note, channel) in list(self.active_notes.keys()):
            msg_off = mido.Message('note_off', note=note, velocity=0, channel=channel)
            self.out_port.send(msg_off)
        self.active_notes.clear()
        self.out_port.reset()