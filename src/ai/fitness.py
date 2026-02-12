from ai.utils import SolarSystemChromosome
from music.harmony import ScaleData

class FitnessEvaluator:
    def evaluate(self, chromosome: SolarSystemChromosome,
                current_scale: ScaleData) -> float:
        scale_intervals = [(interval + current_scale.root)%12 for interval in current_scale.intervals]
        consonant_intervals = [scale_intervals[i] for i in [0, 2, 4]]
        chord_scores = []
        
        for gene in chromosome.planet_genes:
            root_score = int(gene.chord.root in scale_intervals)
            #if gene.chord.root not in consonant_intervals: root_score *= 0.8
            notes = [(interval + gene.chord.root) % 12 for interval in gene.chord.intervals]
            #triad_score = sum([(note in scale_intervals) * (((note in consonant_intervals) * 0.2) + 0.8) for note in notes[1:3]])/2
            triad_score = sum([(note in scale_intervals) for note in notes[1:3]])/2
            extensions_score = sum([(note in scale_intervals) for note in notes[3:]])/len(notes[3:])
            chord_scores.append((root_score * 0.4) + (triad_score * 0.5) + (extensions_score * 0.1))
        
        score = sum(chord_scores)/len(chromosome.planet_genes)
        return score
        
