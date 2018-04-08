from parallel_ga_processing.geneticAlgorithms import geneticBase
import random
from scoop import logger, futures


class MasterSlaveBase(geneticBase.GeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, fitness):
        super().__init__(population_size, chromosome_size, number_of_generations, fitness)
        self._population = self.initialize_population()

    def _process(self):
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
        results = list(futures.map(self._fitness, self._population))
        neighbours = self._Individuals()
        for i in range(0, self._population_size):
            fit_val = results.pop(0)
            chromosome = self._population[i]
            neighbours.append_object(self._Individual(fit_val, chromosome))

        chromosomes_reproducing = self._choose_individuals_based_on_fitness(
            neighbours).sort_objects()
        best_individual = chromosomes_reproducing.pop(0)

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
            "Actual popul is " + str(chromosomes_reproducing) + " with length " + str(
                len(chromosomes_reproducing)))
        logger.info("best indiv " + str(best_individual))
        if len(chromosomes_reproducing) % 2 == 0:
            self._population.append(best_individual.chromosome)
        else:
            # put the best individual to max index in order to not rewrite existing
            chromosomes_reproducing.append(best_individual)
        # randomly choose pairs for crossover
        # then mutate new individuals and put them to new population
        while bool(chromosomes_reproducing):
            father = chromosomes_reproducing.pop(random.randrange(len(
                chromosomes_reproducing))).chromosome
            mother = chromosomes_reproducing.pop(random.randrange(len(
                chromosomes_reproducing))).chromosome
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
            to_return = self._process()
        return to_return
