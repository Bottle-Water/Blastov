from music_data import CHORD_TYPES, SCALE_TYPES, int_to_note, ChordData, ScaleData
from utils import PlanetGene, SolarSystemChromosome
from fitness import FitnessEvaluator
from dataclasses import dataclass
from typing import Tuple, List
from random import randrange, choice, random
from matplotlib import pyplot as plt
import numpy as np
import math

class GeneticSolarSystemGenerator:
    def __init__(self, system_size=5,
                 population_size=60,
                 mutation_rate=0,
                 injection_prop = 0.5,
                 random_immigration_prop = 0.01,
                 subpop_size = 10):
        
        self.system_size = system_size
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.injection_prop = injection_prop
        self.random_immigration_prop = random_immigration_prop
        self.subpop_size = subpop_size

        #Initialise random population
        self.population = []
        for _ in range(self.population_size):
            chromosome = self.create_random_chromosome()
            self.population.append(chromosome)
        self.population_with_fitness = [(chrom, 0) for chrom in self.population]

        self.fitness_evaluator = FitnessEvaluator()
        

    def run(self, max_gens, current_scale: ScaleData):
        gen = 0
        avg_fit = 0

        best_fit_trend = []
        avg_fit_trend = []
        injections = []
        inject = False
        subpop = []

        #Main generation loop
        while avg_fit < 0.825 and gen < max_gens:
            best_fit, avg_fit, subpop = self._step(current_scale, subpop, inject)
            best_fit_trend.append(best_fit)
            avg_fit_trend.append(avg_fit) 
            '''
            if gen > 3 and avg_fit == avg_fit_trend[gen-2]:
                inject = True
                injections.append(gen)
                subpop = []
            else:
                inject = False 
            '''

            gen += 1
        
        resolved = False if gen == max_gens else True
        stats = {"Length": gen, "Injections": {"Number": len(injections)}, "Resolved": resolved, 
                 "Trends": {"Avg": avg_fit_trend, "Best": best_fit_trend}}

        if len(injections) != 0:
            stats["Injections"]["Locations"] = injections
        return stats
    
    #Implements 'SORIGA' random immigration algorithm from here: 
    #https://link.springer.com/article/10.1007/s10710-007-9024-z
    def _step(self, current_scale: ScaleData, subpop: List, inject: bool):
        if inject:
            subpop_size = 20
        else:
            subpop_size = self.subpop_size

        if not subpop:
            worst_idx = np.argsort([x[1] for x in self.population_with_fitness])[0]
            start_idx = worst_idx + math.floor(-((subpop_size-1)/2))
            stop_idx  = worst_idx + math.floor(((subpop_size-1)/2))
            subpop = np.arange(start=start_idx, stop=stop_idx+1)
            subpop = [x % self.population_size for x in subpop]
            for i in subpop:
                self.population[i] = self.create_random_chromosome()

        #Selection - top 20%
        fitnesses = np.argsort([x[1] for x in self.population_with_fitness])
        superpop_fitnesses = [x for x in fitnesses if x not in subpop]
        parents = superpop_fitnesses[int(-0.2*self.population_size):]
        subpop_fitnesses = [x for x in fitnesses if x in subpop]
        #At the moment, we just choose the top 3 subpop as parents
        subpop_parents = subpop_fitnesses[-2:]
        # Reproduction (Crossover + Mutation)
        for i in range(self.population_size):
            #At the moment, this actually makes it slightly worse lol 
            if i in subpop and i not in subpop_parents:
                parent1 = self.population[choice(subpop_parents)]
                parent2 = self.population[choice(subpop_parents)]
                child = self._crossover(parent1, parent2)
                self.population[i] = child
            elif i not in parents:
                parent1 = self.population[choice(parents)]
                parent2 = self.population[choice(parents)]
                child = self._crossover(parent1, parent2)
                self.population[i] = child
            '''
            if i not in parents:
                parent1 = self.population[choice(parents)]
                parent2 = self.population[choice(parents)]
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                self.population[i] = child
            '''

        #Random immigration - replace proportion with random newcomers
        self.population = self._random_immigration(self.population)

        #Evaluate fitness for all
        self.population_with_fitness = [(chrom, self._evaluate_fitness(chrom, current_scale)) for chrom in self.population]
        self.population = [chrom for chrom, _ in self.population_with_fitness]
        fitnesses = [x[1] for x in self.population_with_fitness]

        best_fit = sorted(self.population_with_fitness, key=lambda x: x[1], reverse=True)[0][1]
        worst_idx = min(range(len(fitnesses)), key=fitnesses.__getitem__)
        if worst_idx not in subpop:
            subpop = []

        avg_fit = sum(fitnesses) / len(fitnesses)

        return (best_fit, avg_fit, subpop) 
    
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

        for gene in chrom.planet_genes:
            for i, note in enumerate(gene.chord.intervals[1:]):
                mutate_chance = random()
                #Either shift a note up or down at rando 
                if (self.mutation_rate/2) < mutate_chance < self.mutation_rate:
                    gene.chord.intervals[i+1] = (note + 1) % 12
                elif mutate_chance < (self.mutation_rate/2):
                    gene.chord.intervals[i+1] = (note - 1) % 12
        
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



def main():
    scales = [ScaleData("CMajor"),
              ScaleData("GMajor"),
              ScaleData("FMinor"),
              ScaleData("BMajor")]
    max_runs = 100
    max_steps = 50
    stats = []

    for _ in range(max_runs):
        generator = GeneticSolarSystemGenerator()
        run_stats = []
        for current_scale in scales:
            run_stats.append(generator.run(max_steps, current_scale))
        stats.append(run_stats)

    plt.figure(1, figsize=(12, 6))
    print(f"Completed {max_runs} runs.")
    previous_scale = None
    for i, current_scale in enumerate(scales):
        scale_stats = [run[i] for run in stats]
        avg_len = 0
        max_len = 0
        injected = 0
        unresolved = 0
        avg_injections = 0
        avg_injection_site = 0

        for j, entry in enumerate(scale_stats):
            if j < 4:
                plt.subplot(len(scales), 4, ((i*4) + (j+1)))
                plt.title(current_scale.name)
                plt.plot(np.arange(entry["Length"]), entry["Trends"]["Best"], label='Best', color='red')
                plt.plot(np.arange(entry["Length"]), entry["Trends"]["Avg"], label='Avg', color='blue')
                plt.xlim(0, max_steps)
                plt.ylim(0, 1)
                plt.legend()
                if entry["Injections"]["Number"] > 0:
                    plt.vlines(entry["Injections"]["Locations"], 0, 1)
                

            avg_len += entry["Length"]
            if entry["Length"] > max_len: max_len = entry["Length"]
            if entry["Injections"]["Number"] > 0: 
                injected += 1
                avg_injections += entry["Injections"]["Number"]
                avg_injection_site += (entry["Injections"]["Locations"][0] + 1)
            unresolved += (entry["Resolved"] != True)

        avg_len /= max_runs
        

        print(f"{previous_scale}->{current_scale.name}")
        print(f"Avg length: {avg_len}, max len: {max_len}.")
        if injected:
            avg_injections /= injected
            avg_injection_site /= injected
            print(f"{injected} needed on average {avg_injections:.2f} injections after {avg_injection_site:.2f} steps.")
        else:
            print(f"0 needed injections.")

        print(f"{unresolved} didn't resolve.")
        previous_scale = current_scale.name
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()