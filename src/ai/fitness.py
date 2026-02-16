from ai.utils import SolarSystemChromosome
from music.harmony import ScaleData

class FitnessEvaluator:
    """
    Evaluates the musical fitness of a chromosome based on harmonic consonance.
    """

    ROOT_WEIGHT = 0.4
    TRIAD_WEIGHT = 0.5
    EXTENSION_WEIGHT = 0.1

    def evaluate(self, chromosome: SolarSystemChromosome,
                current_scale: ScaleData) -> float:
        """
        Evaluate how consonant a sequence of chords is with the current scale.

        Args:
            chromosome (SolarSystemChromosome): The individual to be evaluated.
            current_scale (ScaleData): The harmonic context (key and scale).

        Returns:
            float: A fitness score between 0.0 and 1.0.
        """

        scale_intervals = [(interval + current_scale.root)%12 for interval in current_scale.intervals]
        chord_scores = []
        
        #Each gene represents a chord
        for gene in chromosome.planet_genes:
            # 1. Εvaluate the root note
            root_score = int(gene.chord.root in scale_intervals)
            notes = [(interval + gene.chord.root) % 12 for interval in gene.chord.intervals]

            # 2. Evaluate the Triad (3rd and 5th)
            triad_score = sum([(note in scale_intervals) for note in notes[1:3]])/2
            
            # 3. Evaluate Extensions (7ths, 9ths, etc.)
            extensions_score = sum([(note in scale_intervals) for note in notes[3:]])/len(notes[3:])

            #Weights fitness so that more dissonance is allowed in the extensions
            chord_scores.append((root_score * self.ROOT_WEIGHT) + (triad_score * self.TRIAD_WEIGHT) +
            (extensions_score * self.EXTENSION_WEIGHT))
        
        score = sum(chord_scores)/len(chromosome.planet_genes)
        return score
        
