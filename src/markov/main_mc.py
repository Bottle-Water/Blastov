import random

from music21.note import Note
from music21 import stream, metadata
# from music21 import configure
from train_examples import fur_elise
from MarkovChainMelodyGenerator import MarkovChainMelodyGenerator


def create_training_data():
    '''
    Creates a list of sample training notes based on a melody composed by me.

    Returns:
        list: List of music21.note.Note objects.
    
    ''' 
    return [
        Note("C5", quarterLength=1),
        Note("E5", quarterLength=1),
        Note("G5", quarterLength=1),
        Note("F5", quarterLength=1),
        Note("A5", quarterLength=2),
        Note("G5", quarterLength=0.5),
        Note("F5", quarterLength=0.5),
        Note("E5", quarterLength=1),
        Note("D5", quarterLength=1),
        Note("E5", quarterLength=1),
        Note("D5", quarterLength=2),
        Note("C5", quarterLength=2),
        Note("E5", quarterLength=0.5),
        Note("F5", quarterLength=0.5),
        Note("D5", quarterLength=0.5),
        Note("E5", quarterLength=0.5),
        Note("G5", quarterLength=0.5),
        Note("B5", quarterLength=0.5),
        Note("A5", quarterLength=1),
        Note("G5", quarterLength=1),
        Note("F5", quarterLength=0.5),
        Note("A5", quarterLength=0.5),
        Note("G5", quarterLength=2),
        Note("E5", quarterLength=2),
        Note("C5", quarterLength=2),
    ]
    
def visualize_melody(melody):
    '''
    Visualize a sequence of (pitch, duration) pairs using music21.

    Parameters:
        melody (list): List of (pitch, duration) pairs.
    '''

    #configure.run()

    score = stream.Score()
    score.metadata = metadata.Metadata(title="Generated Melody")
    part = stream.Part()

    for n, d in melody:
        part.append(Note(n, quarterLength=d))
    score.append(part)
    score.show()

def main():
    '''
    Main function for training the chain, generating a melody and visualizing the result
    '''

    states = [
        ('C3', 0.5), ('C#3', 0.5), ('D3', 0.5), ('D#3', 0.5), ('E3', 0.5), ('F3', 0.5), ('F#3', 0.5), ('G3', 0.5), ('G#3', 0.5), ('A3', 0.5), ('A#3', 0.5), ('B3', 0.5),
        ('C3', 1), ('C#3', 1), ('D3', 1), ('D#3', 1), ('E3', 1), ('F3', 1), ('F#3', 1), ('G3', 1), ('G#3', 1), ('A3', 1), ('A#3', 1), ('B3', 1),
        ('C3', 1.5), ('C#3', 1.5), ('D3', 1.5), ('D#3', 1.5), ('E3', 1.5), ('F3', 1.5), ('F#3', 1.5), ('G3', 1.5), ('G#3', 1.5), ('A3', 1.5), ('A#3', 1.5), ('B3', 1.5),
        ('C3', 2), ('C#3', 2), ('D3', 2), ('D#3', 2), ('E3', 2), ('F3', 2), ('F#3', 2), ('G3', 2), ('G#3', 2), ('A3', 2), ('A#3', 2), ('B3', 2),
        
        ('C4', 0.5), ('C#4', 0.5), ('D4', 0.5), ('D#4', 0.5), ('E4', 0.5), ('F4', 0.5), ('F#4', 0.5), ('G4', 0.5), ('G#4', 0.5), ('A4', 0.5), ('A#4', 0.5), ('B4', 0.5),
        ('C4', 1), ('C#4', 1), ('D4', 1), ('D#4', 1), ('E4', 1), ('F4', 1), ('F#4', 1), ('G4', 1), ('G#4', 1), ('A4', 1), ('A#4', 1), ('B4', 1),
        ('C4', 1.5), ('C#4', 1.5), ('D4', 1.5), ('D#4', 1.5), ('E4', 1.5), ('F4', 1.5), ('F#4', 1.5), ('G4', 1.5), ('G#4', 1.5), ('A4', 1.5), ('A#4', 1.5), ('B4', 1.5),
        ('C4', 2), ('C#4', 2), ('D4', 2), ('D#4', 2), ('E4', 2), ('F4', 2), ('F#4', 2), ('G4', 2), ('G#4', 2), ('A4', 2), ('A#4', 2), ('B4', 2),
        
        ('C5', 0.5), ('C#5', 0.5), ('D5', 0.5), ('D#5', 0.5), ('E5', 0.5), ('F5', 0.5), ('F#5', 0.5), ('G5', 0.5), ('G#5', 0.5), ('A5', 0.5), ('A#5', 0.5), ('B5', 0.5),
        ('C5', 1), ('C#5', 1), ('D5', 1), ('D#5', 1), ('E5', 1), ('F5', 1), ('F#5', 1), ('G5', 1), ('G#5', 1), ('A5', 1), ('A#5', 1), ('B5', 1),
        ('C5', 1.5), ('C#5', 1.5), ('D5', 1.5), ('D#5', 1.5), ('E5', 1.5), ('F5', 1.5), ('F#5', 1.5), ('G5', 1.5), ('G#5', 1.5), ('A5', 1.5), ('A#5', 1.5), ('B5', 1.5),
        ('C5', 2), ('C#5', 2), ('D5', 2), ('D#5', 2), ('E5', 2), ('F5', 2), ('F#5', 2), ('G5', 2), ('G#5', 2), ('A5', 2), ('A#5', 2), ('B5', 2),
    ]
    chord_sequence = [
    (60, "maj7"),  # Cmaj7
    (65, "min7"),  # Fmin7
    (67, "dom7"),  # G7
    (60, "maj7"),
    ] * 32  # repeat for length


    training_data = fur_elise()

    model = MarkovChainMelodyGenerator(states)
    model.train(training_data)

    generated_modely = model.generate(128, chord_sequence)
    visualize_melody(generated_modely)


if __name__ == '__main__':
    main()