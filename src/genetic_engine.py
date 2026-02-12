from music.harmony import CHORD_TYPES, ChordData, ScaleData
from ai.utils import PlanetGene, SolarSystemChromosome
from ai.fitness import FitnessEvaluator
from random import randrange, choice, random
from matplotlib import pyplot as plt
import numpy as np
import math

class GeneticSolarSystemGenerator:
    def __init__(self, number_of_planets=5,
                 max_gens = 70,
                 population_size=150,
                 threshold = 0.95,
                 mutation_rate=0.05,
                 random_immigration_prop = 0.05,
                 subpop_size = 40):
        
        self.number_of_planets = number_of_planets
        self.max_gens = max_gens
        self.population_size = population_size
        self.threshold = threshold
        self.mutation_rate = mutation_rate
        self.random_immigration_prop = random_immigration_prop
        self.subpop_size = subpop_size
        self.subpop = []

        #Initialise random population
        self.population = []
        for _ in range(self.population_size):
            chromosome = self.create_random_chromosome()
            self.population.append(chromosome)
        #Initialise 0 fitness for each
        self.population_with_fitness = [(chrom, 0) for chrom in self.population]

        self.fitness_evaluator = FitnessEvaluator()
        self.current_scale_steps = 0
        self.previous_scale = None
    
    def run(self, current_scale: ScaleData) -> SolarSystemChromosome:
        """
        Step the generator towards the target scale, and return status. 

        Rather than returning the best candidate, our model prefers to 
        keep track of one arbritrary candidate, to ensure that our output
        shows one smooth evolutionary journey.
        """
        resolved = False
        queen, stats = self._step(current_scale)
        
        #Keep track of how many consecutive steps towards this particular scale. 
        if self.previous_scale and current_scale.name == self.previous_scale.name:
            self.current_scale_steps += 1
        else:
            self.current_scale_steps = 1

        if stats["Avg fit"] > self.threshold or self.current_scale_steps == self.max_gens:
            resolved = True
        
        self.previous_scale = current_scale
        return queen, resolved
    

    def _step(self, current_scale: ScaleData):
        """
        Steps the model.

        Includes an implementation of the 'SORIGA' algorithm: 
        https://link.springer.com/article/10.1007/s10710-007-9024-z
        It is a more targeted development on the 'random immigrant' system 
        in which a proportion of the population is replaced with random 
        chromosomes each generation (which is also implemented below). In
        SORIGA, we initialise a small random population which includes the 
        lowest ranked member. We then prevent this subpopulation from 
        crossing over with the main population, until, by crossing it over
        with itself, the fitness of the group raises and the group no 
        longer contains the worst member of the population. 
        (This is a good system for breaking up homogenous populations.)
        """
        #Identify the chromosome we are following down the generations
        queen_idx = 0
        
        #Initialise a new subpopulation if it was emptied last step. 
        if not self.subpop:
            #Find the worst performing chromosome, and build the group with its
            #index neighbours (these indexes are arbritrary - the selection is 
            #essentially random).
            worst_idx = np.argsort([x[1] for x in self.population_with_fitness])[0]
            start_idx = worst_idx + math.floor(-((self.subpop_size-1)/2))
            stop_idx  = worst_idx + math.floor(((self.subpop_size-1)/2))
            self.subpop = np.arange(start=start_idx, stop=stop_idx+1)
            self.subpop = [x % self.population_size for x in self.subpop]
            for i in self.subpop:
                self.population[i] = self.create_random_chromosome()

        fitnesses = np.argsort([x[1] for x in self.population_with_fitness])

        #SELECTION
        #The best 20% of the population (excluding those chosen for the subpopulation) 
        #are chosen for the parent pool.
        superpop_fitnesses = [x for x in fitnesses if x not in self.subpop]
        superpop_fitnesses = list(filter(lambda a: a != queen_idx, superpop_fitnesses))
        parents = superpop_fitnesses[int(-0.2*self.population_size):]

        #Repeat the process within the subpopulation. We only choose 10% of the subpopulation
        #as parents to speed up growth. 
        subpop_fitnesses = [x for x in fitnesses if x in self.subpop]
        subpop_fitnesses = list(filter(lambda a: a != queen_idx, subpop_fitnesses))
        subpop_parents = subpop_fitnesses[-int(self.subpop_size*0.1):]
        
        #CROSSOVER
        for i in range(self.population_size):
            #The 'queen' (our chosen chromosome) is always crossed over with a selected
            #parent to ensure it follows the improvements in fitness. It produces one child,
            #which becomes the next queen. 
            if i == queen_idx:
                king = self.population[choice(subpop_parents)]
                princess = self._crossover(self.population[queen_idx], king)
                self.population[i] = princess
            elif i in self.subpop and i not in subpop_parents:
                parent1 = self.population[choice(subpop_parents)]
                parent2 = self.population[choice(subpop_parents)]
                child = self._crossover(parent1, parent2)
                self.population[i] = child
            elif i not in parents:
                parent1 = self.population[choice(parents)]
                parent2 = self.population[choice(parents)]
                child = self._crossover(parent1, parent2)
                self.population[i] = child


        #Random immigration - replace proportion with random newcomers
        #each generation.
        self.population = self._random_immigration(self.population)

        #Evaluate fitness for all
        self.population_with_fitness = [(chrom, self._evaluate_fitness(chrom, current_scale)) for chrom in self.population]
        self.population = [chrom for chrom, _ in self.population_with_fitness]
        fitnesses = [x[1] for x in self.population_with_fitness]

        best_fit = sorted(self.population_with_fitness, key=lambda x: x[1], reverse=True)[0][1]
        worst_idx = min(range(len(fitnesses)), key=fitnesses.__getitem__)
        #If the subpopulation no longer contains the worst chromosome, its done its job - it can 
        #be merged with the rest of the population, and a new subpopulation made. 
        if worst_idx not in self.subpop:
            self.subpop = []

        avg_fit = sum(fitnesses) / len(fitnesses)

        return self.population[queen_idx], {"Best fit": best_fit, "Avg fit": avg_fit}
    
    def create_random_chromosome(self) -> SolarSystemChromosome:
        planet_genes = []        

        for _ in range(self.number_of_planets):
            root = randrange(12)
            chord_type = choice(CHORD_TYPES)
            chord = ChordData(root, chord_type)
            planet_genes.append(PlanetGene(chord))
        
        return SolarSystemChromosome(planet_genes)

    def _crossover(self, p1: SolarSystemChromosome, p2: SolarSystemChromosome) -> SolarSystemChromosome:
        """
        Crossover two parents. This is a simple single-point crossover,
        as the chromosomes are simple and small.
        """
        crossover_point = randrange(self.number_of_planets)
        p1_genes = p1.planet_genes[:crossover_point]
        p2_genes = p2.planet_genes[crossover_point:]
        child = SolarSystemChromosome((p1_genes + p2_genes))

        return child 

    def _random_immigration(self, population):
        """Replace proportion of population with newcomers"""
        new_population = []
        for chrom in population:
            if random() < self.random_immigration_prop:
                chrom = self.create_random_chromosome()
            new_population.append(chrom)
        return new_population

    def _evaluate_fitness(self, chrom: SolarSystemChromosome,
                          current_scale: ScaleData) -> float:
        return self.fitness_evaluator.evaluate(chrom, current_scale)

def stats():
    """
    For getting stats on the performance of the model, and its ability
    to reach its target scale. Simulates 5 key changes for 100 runs. 
    """
    
    #First key change is from random to C, which is much easier than the 
    #others. Once the population converges on a scale it is much harder to 
    #shift. 
    scales = [ScaleData("CMajor"),
              ScaleData("GMajor"),
              ScaleData("FMinor"),
              ScaleData("BMajor")]
    max_runs = 100
    stats = []
    print(f"Running model {max_runs} times through {len(scales)+1} key changes.")

    #Runs the model over all the scales, then gets a new model to start fresh.
    for _ in range(max_runs):
        generator = GeneticSolarSystemGenerator()
        run_stats = []

        for current_scale in scales:
            gen = 0
            avg_fit = 0

            best_fit_trend = []
            avg_fit_trend = []

            #Main generation loop
            while avg_fit < generator.threshold and gen < generator.max_gens:
                _, step_stats = generator._step(current_scale)
                avg_fit = step_stats["Avg fit"]
                best_fit_trend.append(step_stats["Best fit"])
                avg_fit_trend.append(avg_fit) 
                
                gen += 1
            
            resolved = False if gen == generator.max_gens else True
            new_stats = {"Length": gen, "Resolved": resolved, 
                    "Trends": {"Avg": avg_fit_trend, "Best": best_fit_trend}}
            run_stats.append(new_stats)
        stats.append(run_stats)

    plt.figure(1, figsize=(12, 6))
    previous_scale = None
    for i, current_scale in enumerate(scales):
        scale_stats = [run[i] for run in stats]
        avg_len = 0
        max_len = 0
        unresolved = 0

        for j, entry in enumerate(scale_stats):
            if j < 4:
                plt.subplot(len(scales), 4, ((i*4) + (j+1)))
                plt.title(f"Run {j+1}: {previous_scale}->{current_scale.name}")
                plt.plot(np.arange(entry["Length"]), entry["Trends"]["Best"], label='Best', color='red')
                plt.plot(np.arange(entry["Length"]), entry["Trends"]["Avg"], label='Avg', color='blue')
                plt.xlim(0, generator.max_gens)
                plt.ylim(0, 1)
                plt.legend()
                

            avg_len += entry["Length"]
            if entry["Length"] > max_len: max_len = entry["Length"]
            unresolved += (entry["Resolved"] != True)

        avg_len /= max_runs

        print(f"{previous_scale}->{current_scale.name}")
        print(f"Avg length: {avg_len}, max len: {max_len}.")
        print(f"{unresolved} didn't resolve in {generator.max_gens} gens.")
        previous_scale = current_scale.name
    
    plt.tight_layout()
    plt.show()

def main():
    stats()

if __name__ == "__main__":
    main()