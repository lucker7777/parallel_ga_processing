import numpy
import random
import abc
from scoop import logger


class GeneticAlgorithmBase(metaclass=abc.ABCMeta):
    def __init__(self, population_size, chromosome_size, number_of_generations):
        self._population_size = population_size
        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations

    def initialize_population(self):
        """
        Generate the population
        :return: population
        """
        population = []
        for i in range(0, self._population_size):
            population.append(self._gen_individual())
        return population

    def initialize_topology(self):
        pass

    def _gen_individual(self):
        """
        Generate binary array
        """
        return list(map(int,
                        numpy.random.randint(
                            2,
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

    def _mutation(self, chromosome):
        """
        Invert one random bit based on probability
        :param chromosome
        """
        if numpy.random.choice([True, False], p=[0.1, 0.9]):
            rnd = random.randint(0, self._chromosome_size - 1)
            chromosome[rnd] = abs(chromosome[rnd] - 1)

