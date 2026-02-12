from ai.utils import SolarSystemChromosome
from music.harmony import ScaleData

class FitnessEvaluator:
    def evaluate(self, chromosome: SolarSystemChromosome,
                current_scale: ScaleData) -> float:
        """
        Evaluate how consonant a chord is with the current scale. 

        Returns:
            score (float): A value from 0-1. 
        """
        scale_intervals = [(interval + current_scale.root)%12 for interval in current_scale.intervals]
        chord_scores = []
        
        #Each gene represents a chord
        for gene in chromosome.planet_genes:
            root_score = int(gene.chord.root in scale_intervals)
            notes = [(interval + gene.chord.root) % 12 for interval in gene.chord.intervals]
            #This looks at the 3rd and 5th of the chord
            triad_score = sum([(note in scale_intervals) for note in notes[1:3]])/2
            extensions_score = sum([(note in scale_intervals) for note in notes[3:]])/len(notes[3:])
            #This weights the fitness so that more dissonance is allowed in the extensions
            chord_scores.append((root_score * 0.4) + (triad_score * 0.5) + (extensions_score * 0.1))
        
        score = sum(chord_scores)/len(chromosome.planet_genes)
        return score
        
