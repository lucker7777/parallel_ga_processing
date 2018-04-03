from geneticAlgorithms import geneticGrainedBase
import time
import pika
import json
import random
import numpy
from scoop import logger
import numpy as np
from .decorator import log_method


class CoarseGrainedBase(geneticGrainedBase.GrainedGeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, server_ip_addr,
                 neighbourhood_size, fitness):

        super().__init__(population_size, chromosome_size,
                         number_of_generations, server_ip_addr,
                         neighbourhood_size, fitness)

    @log_method()
    def initialize_population(self):
        populations = []
        for i in range(0, self._population_size):
            populations.append(super().initialize_population())
        return populations

    @log_method()
    def _process(self, population):
        self._population = population
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
        best_individual = None
        chromosomes_reproducing = {}
        fit_values = [self._fitness(self._population[i]) for i in range(self._population_size)]
        fitness_max = max(fit_values)
        logger.info("fit values " + str(fit_values) + " max " + str(fitness_max))
        # choose individuals for reproduction based on probability
        for i in range(0, self._population_size):
            # best individual has 100% probability to reproduce
            # others probability is relative to his
            # weak individuals are replaced with new ones
            prob = fit_values[i] / fitness_max
            # retrieve best individual, others are randomly selected
            if int(prob) == 1 and best_individual is None:
                logger.info("BEST")
                best_individual = self._population[i]
            elif numpy.random.choice([True, False], p=[prob, 1 - prob]):
                chromosomes_reproducing[i] = self._population[i]

        # if none of individuals were selected
        # try it once again
        if len(chromosomes_reproducing) is 0:
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

    @log_method()
    def _send_data(self, data):
        sol_fit, sol_vector = data
        toSend = [sol_fit]
        toSend.extend(list(map(float, sol_vector)))
        self._channel.basic_publish(exchange='direct_logs',
                                    routing_key=self._queue_to_produce,
                                    body=json.dumps(toSend))

    @log_method()
    def _collect_data(self):
        neighbours = self._Collect()
        while neighbours.size_of_col() != self._num_of_neighbours:
            method_frame, header_frame, body = self._channel.basic_get(queue=str(self._queue_name),
                                                                       no_ack=False)
            if body:
                received = list(map(float, json.loads(body)))
                logger.info(self._queue_to_produce + " RECEIVED " + str(received))

                fit_val = received.pop(0)
                vector = list(map(int, received))
                neighbours.append_object(self._Snt(fit_val, vector))
                self._channel.basic_ack(method_frame.delivery_tag)

            else:
                logger.info(self._queue_to_produce + ' No message returned')
        sorted_x = neighbours.sort_objects()
        return sorted_x.pop(0).chromosome

    @log_method()
    def _finish_processing(self, received_data, data):
        received_chromosome = list(map(int, received_data))
        random_chromosome = random.randint(0, len(self._population) - 1)
        self._population[random_chromosome] = received_chromosome
        return self._find_solution(self._population)
