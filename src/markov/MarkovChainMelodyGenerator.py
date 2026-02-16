import numpy as np
from typing import List, Tuple


class MarkovChainMelodyGenerator:
    """
    A Markov Chain model that generates melodies based on learned (interval, duration) states,
    with real-time harmonic biasing for chords and scales.
    """

    def __init__(self, states: List[Tuple[int, float]]):
        """
        Initializes the MarkovChain with the given states.

        Args:
            states (list of tuples): List of possible (pitch, duration) pairs.
        """
        self.states = states
        self.initial_probabilities = np.zeros(len(states))
        self.transition_matrix = np.zeros((len(states), len(states)))
        self._state_indexes = {state: i for (i, state) in enumerate(states)}

    def train(self, notes: List[Tuple[int, float]]) -> None:
        """
        Builds initial probabilities and transition matrix from a list
        of notes.

        Args:
            notes (list): List of (interval,duration) tuples.
        """
        for note in notes:
            state = note 
            self.initial_probabilities[self._state_indexes[state]] += 1

        self._normalize_initial_probabilities()
        self._calculate_transition_matrix(notes)
    

    def _calculate_initial_probabilities(self, notes: List[Tuple[int, float]]) -> None:
        """
        Calculate the initial probabilities from the provided notes.

        Args:
            notes (list): List of (interval,duration) tuples.
        """
        for note in notes:
            self._increment_initial_probability_count(note)
        self._normalize_initial_probabilities()
    
    def _normalize_initial_probabilities(self) -> None:
        """
        Normalize the initial probabilities array such that the sum of all probabilities equals 1.
        """
        total = np.sum(self.initial_probabilities)

        if total:
            self.initial_probabilities /= total

        self.initial_probabilities = np.nan_to_num(self.initial_probabilities)
    
    def _calculate_transition_matrix(self, notes: List[Tuple[int, float]]) -> None:
        """
        Calculate the transition matrix from the provided notes.

        Args:
            notes (list): List of (interval,duration) tuples.
        """
        for i in range(len(notes) - 1):
            self._increment_transition_count(notes[i], notes[i + 1])

        self._normalize_transition_matrix()
    
    def _increment_transition_count(self, current_state: Tuple[int, float],
     next_state: Tuple[int, float]) -> None:
        """
        Increment the transition count between the current state and the next state.
        """
        current_idx = self._state_indexes[current_state]
        next_idx = self._state_indexes[next_state]
        self.transition_matrix[current_idx, next_idx] += 1
        
    
    def _normalize_transition_matrix(self) -> None:
        """
        Normalizes each row of the transition matrix so that it represents 
        a probability distribution of transitioning to the next state.
        """
        row_sums = self.transition_matrix.sum(axis=1)

        with np.errstate(divide='ignore', invalid='ignore'):           
            self.transition_matrix = np.where(
                row_sums[:, None], # Condition: Check each row's sum.
                # True case: Normalize if sum is not zero.
                self.transition_matrix / row_sums[:, None],
                0, # False case: Keep as zero if sum is zero.
            )
    
    def _generate_starting_state(self) -> Tuple[int, float]:
        """
        Generate a starting state based on the initial probabilities.
        
        Returns:
            tuple: A state (interval, duration) chosen from the list of possible
            states. 
        """
        initial_index = np.random.choice(
            list(self._state_indexes.values()),
            p=self.initial_probabilities
        )
        return self.states[initial_index]
    
    def _apply_chord_bias(self, probs: np.ndarray, current_pitch : int,
        root_midi: int,
        scale_intervals: List[int],
        chord_intervals: List[int]) -> np.ndarray:
        """
        Applies harmonic weights to transition probabilities based on the current 
        musical context (chord and scale).

        Args:
            probs (np.array): 1D array of base transition probabilities for the
            current state.
            current_pitch (int): The absolute MIDI pitch of the last played note.
            root_midi (int): The absolute MIDI pitch of the current chord's root.
            scale_intervals (list): Semitone offsets from the root representing the current scale.
            chord_intervals (list): Semitone offsets from the root representing the current chord.

        Returns:
            np.array: A new 1D array of normalized probabilities adjusted for harmonic correctness.
        
        """
        weighted = probs.copy()
        weighted += 0.001  #epsilon to prevent absolute zero

        root_pc = root_midi % 12

        for i, (interval, _) in enumerate(self.states):

            predicted_pitch = current_pitch + interval
            note_pc = predicted_pitch % 12
            rel = (note_pc - root_pc) % 12

            # Apply weights
            if rel in chord_intervals:
               weighted[i] *= 15.0  # Chord tone bias
            elif rel in scale_intervals: 
               weighted[i] *= 2.0  # Scale tone bias
            else:
                weighted[i] *= 0.05 #Out-of-key penalty

        # Renormalize
        total = np.sum(weighted)
        if total > 0:
            weighted /= total

        return weighted

    def _generate_next_state(
        self, 
        current_state: Tuple[int, float], 
        current_pitch: int, 
        root_midi: int, 
        scale_intervals: List[int], 
        chord_intervals: List[int]
        ) -> Tuple[int, float]:
        """
        Generate the next state based on the transition matrix and the current state.

        Args:
            current_state (tuple): The current state in the Markov Chain.
            current_pitch (int): The absolute MIDI pitch of the last played note.
            root_midi (int): The absolute MIDI pitch of the current chord's root.
            scale_intervals (list): Semitone offsets representing the current scale.
            chord_intervals (list): Semitone offsets representing the current chord.

        Returns:
            tuple: The next generated state (interval, duration).
        """
        if self._does_state_have_subsequent(current_state):

            base_probs = self.transition_matrix[
            self._state_indexes[current_state]].copy()

            weighted_probs = self._apply_chord_bias(
            base_probs, current_pitch, root_midi,scale_intervals, chord_intervals) #apply weights based on chord and scale information
            index = np.random.choice(
                list(self._state_indexes.values()),
                p= weighted_probs,
            )
            return self.states[index]

        return self._generate_starting_state() #safety return

    def _does_state_have_subsequent(self, state: Tuple[int, float]) -> bool:
        """
        Check if a given state has a subsequent state in the transition matrix.

        Args:
            state (tuple): The state to check.

        Returns:
            True if the state has a subsequent state, False otherwise.
        """
        state_idx = self._state_indexes[state]
        return self.transition_matrix[state_idx].sum() > 0

