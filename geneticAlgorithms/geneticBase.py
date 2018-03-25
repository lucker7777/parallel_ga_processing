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

    class _Collect(object):
        def __init__(self):
            self._objects = []

        @property
        def objects(self):
            return self._objects

        def append_object(self, obj):
            return self._objects.append(obj)

        def sort_objects(self):
            return sorted(self._objects, key=lambda x: x.fit, reverse=True)

        def size_of_col(self):
            return len(self._objects)

    class _Snt(object):
        def __init__(self, fit, chromosome):
            self._fit = fit
            self._chromosome = chromosome

        @property
        def fit(self):
            return self._fit

        @property
        def chromosome(self):
            return self._chromosome

        def __str__(self):
            return "Fitness is " + str(self._fit) + " chromosome is " + str(self.chromosome)

        def __repr__(self):
            return self.__str__()
