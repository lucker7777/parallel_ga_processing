import random
from scoop import logger
from .decorator import log_method
from parallel_ga_processing.geneticAlgorithms import geneticGrainedBase


class FineGrainedBase(geneticGrainedBase.GrainedGeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, server_ip_addr, server_user, server_password,
                 neighbourhood_size, fitness, mate_best_neighbouring_individual=True):

        super().__init__(population_size, chromosome_size,
                         number_of_generations, neighbourhood_size, server_ip_addr, server_user,
                         server_password,
                         fitness)
        self._chromosome = None
        self._fitness_val = None
        self.mate_best_neighbouring_individual = mate_best_neighbouring_individual
        self._best_found = False

    @log_method()
    def _store_initial_data(self, chromosome):
        self._chromosome = chromosome

    @log_method()
    def _process(self):
        if not self._best_found:
            self._fitness_val = self._fitness(self._chromosome)

        to_send = [float(self._fitness_val)]
        to_send.extend(list(map(float, self._chromosome)))
        return to_send

    def _check_collected_data(self, neighbours):

        for x in self._queues_to_consume:
            if neighbours.size_of_col(x) != 1:
                return False
        return True

    def _parse_received_data(self, neighbours, source, received_data):
        received = list(map(float, received_data))
        fit_val = received.pop(0)
        vector = list(map(int, received))
        logger.info("aa" + str(fit_val) + " chr " + str(vector))
        neighbours.append_object(self._Individual(fit_val, vector), source)

    @log_method()
    def _finish_processing(self, neighbouring_chromosomes):
        if self._best_found:
            return self._fitness_val, list(map(float, self._chromosome))

        best_individual = neighbouring_chromosomes.best_individual
        if len(neighbouring_chromosomes.individuals) == 1 and best_individual is not None:
            self._fitness_val = float(best_individual.fit)
            self._chromosome = list(map(float, best_individual.chromosome))
            self._best_found = True
            return best_individual.fit, best_individual.chromosome

        chromosomes = neighbouring_chromosomes.sort_objects()
        if len(chromosomes) < 1:
            logger.warning("No individuals were chosen from other neighbours."+
                           "Maybe it is the fitness function that is wrong.")
            chromosomes = [self._gen_individual()]
        if self.mate_best_neighbouring_individual:
            self._mate_chromosomes_with_current(chromosomes.pop(0))
        else:
            # choose one random individual
            self._mate_chromosomes_with_current(random.choice(chromosomes))

        self._fitness_val = self._fitness(self._chromosome)
        if self.is_ultimate_solution(self._fitness_val):
            self._best_found = True
        return self._fitness_val, list(map(float, self._chromosome))

    def _mate_chromosomes_with_current(self, neighbouring_individual):
        father = neighbouring_individual.chromosome
        logger.info("father " + str(father) + " mother " + str(self._chromosome))
        self._crossover(father, self._chromosome)
        # mother
        self._mutation(self._chromosome)
