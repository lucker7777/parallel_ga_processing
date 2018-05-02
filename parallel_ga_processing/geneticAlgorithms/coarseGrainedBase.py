import random
from scoop import logger
from .decorator import log_method
from parallel_ga_processing.geneticAlgorithms import geneticGrainedBase


class CoarseGrainedBase(geneticGrainedBase.GrainedGeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations,
                 neighbourhood_size, server_ip_addr, server_user,
                 server_password, num_of_migrants,
                 fitness):
        super().__init__(population_size, chromosome_size,
                         number_of_generations,
                         neighbourhood_size, server_ip_addr, server_user,
                         server_password,
                         fitness)
        self._num_of_migrants = num_of_migrants
        self._population = None

    @log_method()
    def initialize_population(self):
        """
        Generate random populations for every deme
        :returns array of binary chromosomes
        """
        populations = []
        for i in range(0, self._population_size):
            populations.append(super().initialize_population())
        return populations

    @log_method()
    def _store_initial_data(self, initial_data):
        self._population = initial_data

    def _process(self):
        """
        Processes genetic algorithm
        :param population
        :returns best individual's data parsed in a way to send it
        to neighbouring demes
        """
        self._send_individuals_reproduce()
        data_to_send = []
        for x in self._find_solution(self._population, self._num_of_migrants):
            data_to_send.append((float(x.fit), x.chromosome))
        return data_to_send

    @log_method()
    def _send_individuals_reproduce(self):
        """
        Select individuals for reproduction with probability
        based on fitness value. Weak individuals are removed
        and replaced with newly generated ones.
        """

        # retrieve best fitness of population
        evaluation_data = self._evaluate_population()
        # choose individuals for reproduction based on probability
        chosen_individuals = self._choose_individuals_based_on_fitness(
            evaluation_data)
        chromosomes_reproducing = chosen_individuals.sort_objects()
        best_individual = chosen_individuals.best_individual

        # it is sure that this is the right result
        # but the algorithm needs to continue because of other demes
        if best_individual is not None:
            logger.info("Ultimate best individual was found.")
            while len(self._population) <= self._population_size:
                self._population.append(best_individual.chromosome)
            return
        else:
            best_individual = chromosomes_reproducing.pop(0)

        # remove old population
        del self._population[:]
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
        logger.info(
            "Number of individuals chosen for reproduction is " + str(len(chromosomes_reproducing)))
        # randomly choose pairs for crossover
        # then mutate new individuals and put them to new population
        while len(chromosomes_reproducing) >= 2:
            father = chromosomes_reproducing.pop(random.randrange(len(
                chromosomes_reproducing))).chromosome
            mother = chromosomes_reproducing.pop(random.randrange(len(
                chromosomes_reproducing))).chromosome

            self._crossover(father, mother)
            self._mutation(father)
            self._mutation(mother)

            self._population.append(father)
            self._population.append(mother)

        # Generate new individuals in order to make new population the same size
        while len(self._population) <= self._population_size:
            self._population.append(self._gen_individual())

    def _evaluate_population(self):
        """
        Processes fitness function on every individual
        :returns best individual
        """
        evaluation_data = self._Individuals()
        for i in range(self._population_size):
            fit_val = self._fitness(self._population[i])
            evaluation_data.append_object(
                self._Individual(fit_val, self._population[i]))
        return evaluation_data

    def _check_collected_data(self, neighbours):
        if len(neighbours.objects) >= self._num_of_neighbours:
            for x in neighbours.objects.keys():
                if neighbours.size_of_col(x) < self._num_of_migrants:
                    return False
            return True
        return False

    def _parse_received_data(self, neighbours, source, received):
        for data in received:
            fit_val, vector = data
            neighbours.append_object(self._Individual(float(fit_val), list(map(int, vector))),
                                     source=source)

    def _finish_processing(self, neighbouring_individuals):
        """
        Select individuals for reproduction with probability
        based on fitness value. Weak individuals are removed
        and replaced with individuals from neighbouring demes.
        :param neighbouring_individuals randomly chosen neighbouring individuals
        """
        for x in neighbouring_individuals.individuals:
            self._replace_old_individuals_with_new(x.chromosome)
        return self._find_solution(self._population, 1)

    def _replace_old_individuals_with_new(self, neighbouring_individual):
        new_chromosome = list(map(int, neighbouring_individual))
        random_old_chromosome = random.randint(0, len(self._population) - 1)
        self._population[random_old_chromosome] = new_chromosome
