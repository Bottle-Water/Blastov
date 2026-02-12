from music.harmony import CHORD_TYPES, SCALE_TYPES, int_to_note, ChordData, ScaleData
from ai.utils import PlanetGene, SolarSystemChromosome
from ai.fitness import FitnessEvaluator
from dataclasses import dataclass
from typing import Tuple, List
from random import randrange, choice, random
from matplotlib import pyplot as plt
import numpy as np
import math

class GeneticSolarSystemGenerator:
    def __init__(self, system_size=5,
                 max_gens = 70,
                 population_size=200,
                 threshold = 0.875,
                 mutation_rate=0.05,
                 injection_prop = 0.5,
                 random_immigration_prop = 0.05,
                 subpop_size = 40):
        
        self.system_size = system_size
        self.max_gens = max_gens
        self.population_size = population_size
        self.threshold = threshold
        self.mutation_rate = mutation_rate
        self.injection_prop = injection_prop
        self.random_immigration_prop = random_immigration_prop
        self.subpop_size = subpop_size
        self.subpop = []

        #Initialise random population
        self.population = []
        for _ in range(self.population_size):
            chromosome = self.create_random_chromosome()
            self.population.append(chromosome)
        self.population_with_fitness = [(chrom, 0) for chrom in self.population]

        self.fitness_evaluator = FitnessEvaluator()
        self.current_scale_steps = 0
        self.previous_scale = None
    
    def run(self, current_scale: ScaleData) -> SolarSystemChromosome:
        resolved = False
        queen, stats = self._step(current_scale)
        
        if self.previous_scale and current_scale.name == self.previous_scale.name:
            self.current_scale_steps += 1
        else:
            self.current_scale_steps = 1

        if stats["Avg fit"] > self.threshold or self.current_scale_steps == self.max_gens:
            resolved = True
        
        self.previous_scale = current_scale
        return queen, resolved
    
    #Implements 'SORIGA' random immigration algorithm from here: 
    #https://link.springer.com/article/10.1007/s10710-007-9024-z
    def _step(self, current_scale: ScaleData):
        queen_idx = 0
        
        if not self.subpop:
            worst_idx = np.argsort([x[1] for x in self.population_with_fitness])[0]
            start_idx = worst_idx + math.floor(-((self.subpop_size-1)/2))
            stop_idx  = worst_idx + math.floor(((self.subpop_size-1)/2))
            self.subpop = np.arange(start=start_idx, stop=stop_idx+1)
            self.subpop = [x % self.population_size for x in self.subpop]
            for i in self.subpop:
                self.population[i] = self.create_random_chromosome()

        #Selection - top 20%
        fitnesses = np.argsort([x[1] for x in self.population_with_fitness])
        superpop_fitnesses = [x for x in fitnesses if x not in self.subpop]
        superpop_fitnesses = list(filter(lambda a: a != queen_idx, superpop_fitnesses))
        parents = superpop_fitnesses[int(-0.2*self.population_size):]
        subpop_fitnesses = [x for x in fitnesses if x in self.subpop]
        superpop_fitnesses = list(filter(lambda a: a != queen_idx, subpop_fitnesses))
        #At the moment, we just choose the top 3 subpop as parents
        subpop_parents = subpop_fitnesses[-int(self.subpop_size*0.1):]
        # Reproduction (Crossover + Mutation)
        for i in range(self.population_size):
            if i == queen_idx:
                king = self.population[choice(subpop_parents)]
                princess = self._crossover(self.population[queen_idx], king)
                self.population[i] = princess
            elif i in self.subpop and i not in subpop_parents:
                parent1 = self.population[choice(subpop_parents)]
                parent2 = self.population[choice(subpop_parents)]
                child = self._crossover(parent1, parent2)
                #child = self._mutate(child)
                self.population[i] = child
            elif i not in parents:
                parent1 = self.population[choice(parents)]
                parent2 = self.population[choice(parents)]
                child = self._crossover(parent1, parent2)
                self.population[i] = child


        #Random immigration - replace proportion with random newcomers
        #(I hate to admit it but I think this is the thread holding everything 
        #together lol)
        self.population = self._random_immigration(self.population)

        #Evaluate fitness for all
        self.population_with_fitness = [(chrom, self._evaluate_fitness(chrom, current_scale)) for chrom in self.population]
        self.population = [chrom for chrom, _ in self.population_with_fitness]
        fitnesses = [x[1] for x in self.population_with_fitness]

        best_fit = sorted(self.population_with_fitness, key=lambda x: x[1], reverse=True)[0][1]
        worst_idx = min(range(len(fitnesses)), key=fitnesses.__getitem__)
        if worst_idx not in self.subpop:
            self.subpop = []

        avg_fit = sum(fitnesses) / len(fitnesses)

        return self.population[queen_idx], {"Best fit": best_fit, "Avg fit": avg_fit}
    
    def create_random_chromosome(self) -> SolarSystemChromosome:
        planet_genes = []        

        for _ in range(self.system_size):
            root = randrange(12)
            chord_type = choice(CHORD_TYPES)
            chord = ChordData(root, chord_type)
            weight = (random() * 0.9) + 0.1
            planet_genes.append(PlanetGene(chord, weight))
        
        return SolarSystemChromosome(planet_genes)

    def _crossover(self, p1: SolarSystemChromosome, p2: SolarSystemChromosome) -> SolarSystemChromosome:
        """Crossover two parents"""

        #Just combine chord arrays with single point! Does the job
        crossover_point = randrange(self.system_size)
        p1_genes = p1.planet_genes[:crossover_point]
        p2_genes = p2.planet_genes[crossover_point:]
        child = SolarSystemChromosome((p1_genes + p2_genes))

        return child 
    
    def _mutate(self, chrom: SolarSystemChromosome) -> SolarSystemChromosome:
        """Mutate a chromosome by randomly changing some genes"""
        """ 
        for gene in chrom.planet_genes:
            for note in gene.chord.intervals:
                chance = random()
                if chance < self.mutation_rate/2:
                    note = (note + 1) % 12
                elif chance < self.mutation_rate:
                    note = (note - 1) % 12
         """
        for gene in chrom.planet_genes:
            if random() < self.mutation_rate:
                gene.chord.root = (gene.chord.root + 1) % 12
                gene.chord.update_name()

        return chrom

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
    scales = [ScaleData("CMajor"),
              ScaleData("GMajor"),
              ScaleData("FMinor"),
              ScaleData("BMajor")]
    max_runs = 100
    stats = []

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
    print(f"Completed {max_runs} runs.")
    previous_scale = None
    for i, current_scale in enumerate(scales):
        scale_stats = [run[i] for run in stats]
        avg_len = 0
        max_len = 0
        unresolved = 0

        for j, entry in enumerate(scale_stats):
            if j < 4:
                plt.subplot(len(scales), 4, ((i*4) + (j+1)))
                plt.title(current_scale.name)
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
        print(f"{unresolved} didn't resolve.")
        previous_scale = current_scale.name
    
    plt.tight_layout()
    plt.show()

def main():
    stats()


if __name__ == "__main__":
    main()