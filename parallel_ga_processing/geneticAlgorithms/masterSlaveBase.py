from parallel_ga_processing.geneticAlgorithms import geneticBase
import random
from scoop import logger, futures
from .decorator import log_method


class MasterSlaveBase(geneticBase.GeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, fitness):
        super().__init__(population_size, chromosome_size, number_of_generations, fitness)
        self._population = self.initialize_population()

    @log_method()
    def _process(self):
        """
        Exchange the random number of bits
        between father and mother
        :param data this argument is not used here
        """
        self._send_individuals_reproduce()
        return self._find_solution(self._population)

    @log_method()
    def _send_individuals_reproduce(self):
        """
        Select individuals for reproduction with probability
        based on fitness value. Weak individuals are removed
        and replaced with newly generated ones.
        """

        # retrieve best fitness of population
        results = list(futures.map(self._fitness, self._population))
        neighbours = self._Individuals()
        for i in range(0, self._population_size):
            fit_val = results.pop(0)
            chromosome = self._population[i]
            neighbours.append_object(self._Individual(fit_val, chromosome))

        chosen_individuals = self._choose_individuals_based_on_fitness(
            neighbours)
        chromosomes_reproducing = chosen_individuals.sort_objects()
        best_individual = chosen_individuals.best_individual

        # it is sure that this is the right result
        # but the algorithm needs to continue because of other demes
        if best_individual is not None:
            while len(self._population) <= self._population_size:
                self._population.append(best_individual.chromosome)
            return

        best_individual = chromosomes_reproducing.pop(0)
        # remove old population
        del self._population[:]
        logger.info("Number of individuals chosen for reproduction is " +
                    str(len(chromosomes_reproducing))+ " while best individuals has fitness "+
                    str(best_individual.fit))
        # Reproducing requires two individuals.
        # If number of selected individuals is even
        # put the best individual to the new population.
        # Otherwise, put him to individuals dedicated
        # for reproduction
        if len(chromosomes_reproducing) % 2 == 0:
            self._population.append(best_individual.chromosome)
        else:
            # put the best individual to max index in order to not rewrite existing
            chromosomes_reproducing.append(best_individual)
        # randomly choose pairs for crossover
        # then mutate new individuals and put them to new population
        while len(chromosomes_reproducing) >= 2:
            father = chromosomes_reproducing.pop(random.randrange(len(
                chromosomes_reproducing))).chromosome
            mother = chromosomes_reproducing.pop(random.randrange(len(
                chromosomes_reproducing))).chromosome
            self._crossover(father, mother)
            # mutate
            self._mutation(father)
            self._mutation(mother)
            self._population.append(father)
            self._population.append(mother)

        # Generate new individuals in order to make new population the same size
        while len(self._population) != self._population_size:
            self._population.append(self._gen_individual())

    @log_method()
    def _find_solution(self, population):
        """
        Find the best solution
        :param population
        :return: best_weight, chromosome
        """
        results = list(futures.map(self._fitness, population))
        neighbours = self._Individuals()
        for i in range(0, self._population_size):
            fit_val = results.pop(0)
            chromosome = self._population[i]
            neighbours.append_object(self._Individual(fit_val, chromosome))

        sorted_max = neighbours.sort_objects().pop(0)
        return sorted_max.fit, sorted_max.chromosome

    def __call__(self):
        to_return = []

        logger.info("Process started")
        for i in range(0, self._number_of_generations):
            logger.info("GENERATION " + str(i))
            to_return = self._process()
        return to_return
