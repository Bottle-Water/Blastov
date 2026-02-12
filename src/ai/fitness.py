from ai.utils import SolarSystemChromosome
from music.harmony import ScaleData

class FitnessEvaluator:
    def evaluate(self, chromosome: SolarSystemChromosome,
                current_scale: ScaleData) -> float:
        scale_intervals = [(interval + current_scale.root)%12 for interval in current_scale.intervals]
        chord_scores = []
        weights = [] #it feels bad that these are unlinked!
        
        for gene in chromosome.planet_genes:
            notes = [(interval + gene.chord.root) % 12 for interval in gene.chord.intervals]
            #root_score = int(gene.chord.root in scale_intervals)
            notes_score = sum([(note in scale_intervals) for note in notes])/len(notes)
            #chord_scores.append((root_score * 1/3) + (notes_score * 2/3))
            chord_scores.append(notes_score)
            weights.append(gene.weight)
        
        weights = [weight / sum(weights) for weight in weights]
        #can try adding weights back in if it works in context
        score = sum([score * weight for score, weight in zip(chord_scores, weights)]) 
        score = sum(chord_scores)/len(chromosome.planet_genes)
        return score
        
