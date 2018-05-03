import numpy as np
import random
from .decorator import log_method
from scoop import logger


class GeneticAlgorithmBase(object):
    def __init__(self, population_size, chromosome_size, number_of_generations, fitness):
        self._population_size = population_size
        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations
        self._fitness = fitness

    @log_method()
    def initialize_population(self):
        """
        Generate the population
        :return: population
        """
        population = []
        for i in range(0, self._population_size):
            population.append(self._gen_individual())
        return population

    def _gen_individual(self):
        """
        Generate binary array
        """
        return list(map(int,
                        np.random.randint(2,
                            size=self._chromosome_size)))

    def _crossover(self, father, mother):
        """
        Exchange the random number of bits
        between father and mother
        :param father
        :param mother
        """
        cross = random.randint(0, self._chromosome_size - 1)
        for i in range(0, cross):
            mother[i] = father[i]
        for i in range(cross, self._chromosome_size):
            father[i] = mother[i]
        return father, mother

    def _mutation(self, chromosome):
        """
        Invert one random bit based on probability
        :param chromosome
        """
        if np.random.choice([True, False], p=[0.1, 0.9]):
            rnd = random.randint(0, self._chromosome_size - 1)
            chromosome[rnd] = abs(chromosome[rnd] - 1)
        return chromosome

    @staticmethod
    def is_ultimate_solution(fit_val):
        ultimate_min = 0
        return fit_val == ultimate_min

    def _choose_individuals_based_on_fitness(self, evaluation_data):

        ultimate_prob = 1
        individuals_to_choose_from = evaluation_data.sort_objects()
        best_individual = individuals_to_choose_from.pop(0)
        fitness_min = best_individual.fit
        chromosomes_reproducing = self._Individuals()
        chromosomes_reproducing.append_object(best_individual)

        if self.is_ultimate_solution(best_individual.fit):
            chromosomes_reproducing.best_individual = best_individual
            return chromosomes_reproducing
        # at least two individuals are required to reproduce
        for chromosome_data in individuals_to_choose_from:
            # best individual has 100% probability to reproduce
            # others probability is relative to his
            # weak individuals are replaced with new ones

            # this is because of division by zero
            if self.is_ultimate_solution(chromosome_data.fit):
                prob = ultimate_prob
            else:
                prob = fitness_min / chromosome_data.fit

            if np.random.choice([True, False], p=[prob, 1 - prob]):
                chromosomes_reproducing.append_object(self._Individual(chromosome_data.fit,
                                                                       chromosome_data.chromosome))
        logger.info("LEN is " + str(len(chromosomes_reproducing.individuals)))
        return chromosomes_reproducing

    class _Individual(object):
        def __init__(self, fit, chromosome, value=''):
            self._fit = fit
            self._chromosome = chromosome
            self._value = value

        @property
        def fit(self):
            return self._fit

        @property
        def chromosome(self):
            return self._chromosome

        @property
        def value(self):
            return self._value

        def __str__(self):
            return "Fitness is " + str(self._fit) + " chromosome is " + str(self.chromosome)

        def __repr__(self):
            return self.__str__()

    class _Individuals(object):
        def __init__(self):
            self._objects = {}
            self._individuals = []
            self._best_individual = None

        @property
        def best_individual(self):
            return self._best_individual

        @best_individual.setter
        def best_individual(self, individual):
            self._best_individual = individual

        @property
        def individuals(self):
            return self._individuals

        @property
        def objects(self):
            return self._objects

        def append_object(self, individual, source=None):
            self._individuals.append(individual)
            if source is None:
                return
            if source not in self._objects:
                self._objects[source] = self._NeighbourIndividuals(source)
            self._objects[source].add_individual(individual)

        def sort_objects(self):
            return sorted(self._individuals, key=lambda x: x.fit, reverse=False)

        def size_of_col(self, source):
            if int(source) not in self._objects:
                return 0
            return self._objects[int(source)].size()

        class _NeighbourIndividuals(object):
            def __init__(self, source):
                self._source = source
                self._individuals_per_source = []

            def add_individual(self, individual):
                self._individuals_per_source.append(individual)

            @property
            def individuals_per_source(self):
                return self._individuals_per_source

            @property
            def source(self):
                return self._source

            def size(self):
                return len(self._individuals_per_source)

            def __str__(self):
                return str(self._source) + " " + str(self._individuals_per_source)
