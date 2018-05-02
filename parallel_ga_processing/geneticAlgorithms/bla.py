from parallel_ga_processing.geneticAlgorithms import geneticBase
import random
import numpy as np

class MasterSlaveBase(object):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, fitness):
        self._population_size = population_size
        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations
        self._fitness = fitness
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
        results = []
        for x in self._population:
            results.append(self._fitness(x))
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
        print("Number of individuals chosen for reproduction is " +
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

    def _find_solution(self, population):
        """
        Find the best solution
        :param population
        :return: best_weight, chromosome
        """
        results = []
        for x in population:
            results.append(self._fitness(x))
        neighbours = self._Individuals()
        for i in range(0, self._population_size):
            fit_val = results.pop(0)
            chromosome = self._population[i]
            neighbours.append_object(self._Individual(fit_val, chromosome))

        sorted_max = neighbours.sort_objects().pop(0)
        return sorted_max.fit, sorted_max.chromosome

    def __call__(self):
        to_return = []

        print("Process started")
        for i in range(0, self._number_of_generations):
            print("GENERATION " + str(i))
            to_return = self._process()
        return to_return

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

    def _choose_individuals_based_on_fitness(self, evaluation_data):
        ultimate_min = 0
        ultimate_prob = 1
        individuals_to_choose_from = evaluation_data.sort_objects()
        best_individual = individuals_to_choose_from.pop(0)
        fitness_min = best_individual.fit
        chromosomes_reproducing = self._Individuals()
        chromosomes_reproducing.append_object(best_individual)

        if best_individual.fit == ultimate_min:
            chromosomes_reproducing.best_individual = best_individual
            return chromosomes_reproducing
        # at least two individuals are required to reproduce
        for chromosome_data in individuals_to_choose_from:
            # best individual has 100% probability to reproduce
            # others probability is relative to his
            # weak individuals are replaced with new ones

            # this is because of division by zero
            if chromosome_data.fit == ultimate_min:
                prob = ultimate_prob
            else:
                prob = fitness_min / chromosome_data.fit

            if np.random.choice([True, False], p=[prob, 1 - prob]):
                chromosomes_reproducing.append_object(self._Individual(chromosome_data.fit,
                                                                       chromosome_data.chromosome))
        print("LEN is " + str(len(chromosomes_reproducing.individuals)))
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


def fitness(chromosome):
    return sum(gene * gene for gene in chromosome)

if __name__ == '__main__':
    ins = MasterSlaveBase(population_size=100,
                          chromosome_size=100,
                          number_of_generations=100,
                          fitness=fitness)
    solution, sol_vec = ins()
    print("FINAL RESULT: fitness: " + str(solution) + " vector: " + str(sol_vec))
