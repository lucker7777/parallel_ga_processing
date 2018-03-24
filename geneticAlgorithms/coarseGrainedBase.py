from geneticAlgorithms import geneticGrainedBase
import time
import pika
import json
import random
import numpy
from scoop import logger
import abc


class CoarseGrainedBase(geneticGrainedBase.GrainedGeneticAlgorithmBase, metaclass=abc.ABCMeta):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, server_ip_addr,
                 num_of_neighbours, neighbourhood_size):
        super().__init__(population_size, chromosome_size,
                         number_of_generations)
        self._channel = None
        self._queue_to_produce = None
        self._queues_to_consume = None
        self._num_of_neighbours = num_of_neighbours
        self._queue_name = None
        self._connection = None
        self._neighbourhood_size = neighbourhood_size
        self._population = []
        self._server_ip_addr = server_ip_addr

    def initialize_population(self):
        populations = []
        for i in range(0, self._population_size):
            populations.append(super().initialize_population())
        return populations

    def _start_MPI(self, channels):
        queue_to_produce = str(channels.pop(0))
        queues_to_consume = list(map(str, channels))
        logger.info("starting processing to queue: " + queue_to_produce
                    + " and consuming from: " + str(queues_to_consume))
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self._server_ip_addr,
                                      credentials=pika.PlainCredentials("genetic1", "genetic1")))

        channel = connection.channel()

        channel.exchange_declare(exchange='direct_logs',
                                 exchange_type='direct')
        channel.basic_qos(prefetch_count=len(queues_to_consume))

        result = channel.queue_declare(exclusive=True)
        self._queue_name = result.method.queue

        for queue in queues_to_consume:
            channel.queue_bind(exchange='direct_logs',
                               queue=self._queue_name,
                               routing_key=queue)
        self._queue_to_produce = queue_to_produce
        self._queues_to_consume = queues_to_consume
        self._channel = channel
        self._connection = connection
        time.sleep(5)

    def _process(self, population):
        self._population = population
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
        fit_values = [self.fitness(self._population[i]) for i in range(self._population_size)]
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

    def _send_data(self, data):
        sol_fit, sol_vector = data
        toSend = [sol_fit]
        toSend.extend(list(map(float, sol_vector)))
        self._channel.basic_publish(exchange='direct_logs',
                                    routing_key=self._queue_to_produce,
                                    body=json.dumps(toSend))

    def initialize_topology(self):
        channels_to_return = []
        quantity = self._population_size
        radius = self._neighbourhood_size
        for x in range(quantity):
            channels = [x]
            for z in range(1, radius + 1):
                if x + z > quantity - 1:
                    channels.append(abs(quantity - (x + z)))
                else:
                    channels.append(x + z)
                if x - z < 0:
                    channels.append(abs((x - z) + quantity))
                else:
                    channels.append(x - z)
            channels_to_return.append(channels)
        return channels_to_return

    def _collect_data(self):
        neighbours = self._Collect()
        while neighbours.size_of_col() != self._num_of_neighbours:
            method_frame, header_frame, body = self._channel.basic_get(queue=str(self._queue_name), no_ack=False)
            if body:
                received = list(map(float, json.loads(body)))
                logger.info(self._queue_to_produce + " RECEIVED " + str(received))

                fit_val = received.pop(0)
                vector = list(map(int, received))
                print("PARSED " + str(fit_val) + " " + str(vector))
                neighbours.append_object(self._Snt(fit_val, vector))
                self._channel.basic_ack(method_frame.delivery_tag)

            else:
                logger.info(self._queue_to_produce + ' No message returned')
        sorted_x = neighbours.sort_objects()
        return sorted_x.pop(0).chromosome

    def _finish_processing(self, received_data, data):
        received_chromosome = list(map(int, received_data))
        random_chromosome = random.randint(0, len(self._population) - 1)
        self._population[random_chromosome] = received_chromosome
        return self._find_solution(self._population)

    def _stop_MPI(self):
        self._connection.close()
