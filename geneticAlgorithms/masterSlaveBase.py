from geneticAlgorithms import geneticBase
import random
import numpy
from scoop import logger, futures
import abc


class MasterSlaveBase(geneticBase.GeneticAlgorithmBase, metaclass=abc.ABCMeta):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations):
        super().__init__(population_size, chromosome_size, number_of_generations)
        self._population = self.initialize_population()

    @abc.abstractmethod
    def fitness(self, chromosome):
        pass

    def _process(self, data):
        """
        Exchange the random number of bits
        between father and mother
        :param data this argument is not used here
        """
        self._send_individuals_reproduce()
        return self._find_solution(self._population)

    def _send_individuals_reproduce(self):
        """
        Select individuals for reproduction with probability
        based on fitness value. Weak individuals are removed
        and replaced with newly generated ones.
        """

        # retrieve best fitness of population
        best_individual = None
        chromosomes_reproducing = {}
        results = list(futures.map(self.fitness, self._population))
        neighbours = self._Collect()
        while neighbours.size_of_col() != self._population_size:
            fit_val, chromosome = results.pop(0)
            neighbours.append_object(self._Snt(fit_val, chromosome))
        sorted_x = neighbours.sort_objects()
        fit_values = list(futures.map(self.fitness, self._population))
        best_chromosome = sorted_x.pop(0)
        fitness_max = best_chromosome.fit
        best_individual = best_chromosome.chromosome
        logger.info("fit values " + str(fit_values) + " max " + str(fitness_max))
        # choose individuals for reproduction based on probability
        for i in range(1, self._population_size):
            # best individual has 100% probability to reproduce
            # others probability is relative to his
            # weak individuals are replaced with new ones
            snt = sorted_x.pop(0)
            prob = snt.fit / fitness_max
            # retrieve best individual, others are randomly selected
            if int(prob) == 1 and best_individual is None:
                pass
            elif numpy.random.choice([True, False], p=[prob, 1 - prob]):
                chromosomes_reproducing[i] = snt.chromosome

        # if none of individuals were selected
        # try it once again
        if len(chromosomes_reproducing) == 0:
            return
        # remove old population
        del self._population[:]

        # Reproducing requires two individuals.
        # If number of selected individuals is even
        # put the best individual to the new population.
        # Otherwise, put him to individuals dedicated
        # for reproduction
        logger.info(
            "Actual popul is " + str(chromosomes_reproducing) + " with length " + str(len(chromosomes_reproducing)))
        logger.info("best indiv " + str(best_individual))
        if len(chromosomes_reproducing) % 2 == 0:
            self._population.append(best_individual)
        else:
            # put the best individual to max index in order to not rewrite existing
            chromosomes_reproducing[self._population_size] = best_individual
        # randomly choose pairs for crossover
        # then mutate new individuals and put them to new population
        while bool(chromosomes_reproducing):
            father_index = random.choice(list(chromosomes_reproducing.keys()))
            father = chromosomes_reproducing.pop(father_index)
            mother_index = random.choice(list(chromosomes_reproducing.keys()))
            mother = chromosomes_reproducing.pop(mother_index)
            logger.info("father " + str(father) + " mother " + str(mother))
            self._crossover(father, mother)
            # mutate
            self._mutation(father)
            self._mutation(mother)
            self._population.append(father)
            self._population.append(mother)

        # Generate new individuals in order to make new population the same size
        while len(self._population) != self._population_size:
            self._population.append(self._gen_individual())

    def _find_solution(self, population):
        """
        Find the best solution
        :param population
        :return: best_weight, chromosome
        """
        results = list(futures.map(self.fitness, population))
        neighbours = self._Collect()
        while neighbours.size_of_col() != self._population_size:
            fit_val, chromosome = results.pop(0)
            neighbours.append_object(self._Snt(fit_val, chromosome))
        sorted_max = neighbours.sort_objects().pop(0)
        return sorted_max.fit, sorted_max.chromosome

    def __call__(self):
        toReturn = []

        logger.info("Process started")
        for i in range(0, self._number_of_generations):
            toReturn = self._process(None)
        return toReturn

