from music_data import CHORD_TYPES, SCALE_TYPES, int_to_note, ChordData, ScaleData
from utils import PlanetGene, SolarSystemChromosome
from fitness import FitnessEvaluator
from dataclasses import dataclass
from typing import Tuple, List
from random import randrange, choice, random

class GeneticSolarSystemGenerator:
    def __init__(self, system_size=5,
                 population_size=20,
                 mutation_rate=0.05,
                 fitness_weights=None):
        self.system_size = system_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.fitness_weights = fitness_weights

        #Actually, bc starting from random will always sound bad, we could 
        #just make sure we always initialise with some starting scale and 
        #optimise there from a random population, and give the generator 
        #an optional argument to pass a population *in* (?)
        self.population = []
        for _ in range(self.population_size):
            chromosome = self.create_random_chromosome()
            self.population.append(chromosome)

        self.fitness_evaluator = FitnessEvaluator()
        

    def step(self, current_scale: ScaleData):
        population_with_fitness = [(chrom, self._evaluate_fitness(chrom, current_scale)) for chrom in self.population]
        population_with_fitness.sort(key=lambda x: x[1], reverse=True)
        self.population = [chrom for chrom, _ in population_with_fitness]

        best = self.population[0]
        best_fit = population_with_fitness[0][1]
        avg_fit = sum(fit for _, fit in population_with_fitness) / len(population_with_fitness)

        # Selection (Keep top 20%)
        next_gen = self.population[:int(self.population_size * 0.2)]
        
        # Reproduction (Crossover + Mutation)
        while len(next_gen) < self.population_size:
            parent1 = choice(self.population[:int(self.population_size * 0.5)])
            parent2 = choice(self.population[:int(self.population_size * 0.5)])
            child = self._crossover(parent1, parent2)
            #child = self._mutate(child)
            next_gen.append(child)
        
        self.population = next_gen
        return (best, best_fit, avg_fit) #actually it isn't best we'll return - it's just a descendant of our initial 
    
    def create_random_chromosome(self) -> SolarSystemChromosome:
        planet_genes = []        

        for _ in range(self.system_size):
            root = randrange(12)
            chord_type = choice(CHORD_TYPES)
            flavour = list(chord_type.keys())[0] #must be a better way
            intervals = list(chord_type.values())[0]
            name = int_to_note[root] + flavour
            chord = ChordData(name, root, intervals)
            weight = (random() * 0.9) + 0.1
            planet_genes.append(PlanetGene(chord, weight))
        
        return SolarSystemChromosome(planet_genes)

    def _crossover(self, p1: SolarSystemChromosome, p2: SolarSystemChromosome) -> SolarSystemChromosome:
        # Trying single point for now! but will get more complex 
        crossover_point = randrange(self.system_size)
        p1_genes = p1.planet_genes[:crossover_point]
        p2_genes = p2.planet_genes[crossover_point:]
        child = SolarSystemChromosome((p1_genes + p2_genes))
        return child 
    
    def _mutate(self, chrom: SolarSystemChromosome) -> SolarSystemChromosome:
        new_genes = []

        for gene in chrom.planet_genes:
            if random() < self.mutation_rate:
               #Mutate. Either shift root up chromatically  or change chord type 
                if random() < 0.5:
                    gene.chord.root = (gene.chord.root + 1) % 12
                else:
                    chord_type = choice(CHORD_TYPES) #at the moment this could well be the same type 
                    new_flavour = list(chord_type.keys())[0]
                    new_intervals = list(chord_type.values())[0] 
                    name = int_to_note[gene.chord.root] + new_flavour
                    gene.chord = ChordData(name, gene.chord.root, new_intervals)
                    gene.chord.intervals = new_intervals
                
            new_genes.append(gene)
        
        return SolarSystemChromosome(new_genes)

    def _evaluate_fitness(self, chrom: SolarSystemChromosome,
                          current_scale: ScaleData) -> float:
        return self.fitness_evaluator.evaluate(chrom, current_scale)



def main():
    generator = GeneticSolarSystemGenerator()
    cmajor_scale = ScaleData(0, SCALE_TYPES["Major"])
    gen = 0
    avg_fit = 0

    while avg_fit < 0.85 and gen < 200:
        best, best_fit, avg_fit = generator.step(cmajor_scale)
        if gen % 10 == 0:
            print(f"Gen {gen}: best fit {best_fit}, avg fit {avg_fit}")
        gen += 1
    
    print(f"Finished on gen {gen+1}: best fit {best_fit}, avg fit {avg_fit}")
    for gene in best.planet_genes:
        print(f"chord: {gene.chord}, weight: {gene.weight}")

if __name__ == "__main__":
    main()