import time
import pika
import json
import numpy as np
from scoop import logger
from .decorator import log_method
from .decorator import timeout
from .geneticBase import GeneticAlgorithmBase
import random


class GrainedGeneticAlgorithmBase(GeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, server_ip_addr,
                 neighbourhood_size, fitness):

        self._population_size_x, self._population_size_y = population_size
        super().__init__(population_size=self._population_size_x * self._population_size_y,
                         chromosome_size=chromosome_size,
                         number_of_generations=number_of_generations, fitness=fitness)
        self._num_of_neighbours = pow((2 * neighbourhood_size) + 1, 2) - 1
        self._neighbourhood_size = neighbourhood_size
        # self._check_population_size(self._population_size_x, self._neighbourhood_size)
        # self._check_population_size(self._population_size_y, self._neighbourhood_size)

        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations

        self._server_ip_addr = server_ip_addr
        self._data_channel = None
        self._confirmation_channel = None
        self._connection = None

        self._confirmation_routing_key = 'confirmation'

    @staticmethod
    def _check_population_size(dimension_size, neighbourhood_size):
        neighbourhood_diameter = ((neighbourhood_size * 2) + 1)
        if dimension_size < neighbourhood_diameter * 2:
            raise ValueError("Population size should be double the size of neighbourhood")

    @log_method()
    def _find_solution(self, population, num_of_best_chromosomes):
        """
        Find the best solution
        :param population
        :return: best_weight, chromosome
        """
        data = self._Individuals()
        for i in range(0, self._population_size):
            curr_fit = self._fitness(population[i])
            data.append_object(self._Individual(curr_fit, population[i]))
        return data.sort_objects()[:num_of_best_chromosomes]

    @log_method()
    def _start_MPI(self, channels):
        queue_to_produce = str(channels.pop(0))
        queues_to_consume = list(map(str, channels.pop(0)))
        logger.info("starting processing to queue: " + queue_to_produce
                    + " and consuming from: " + str(queues_to_consume))
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self._server_ip_addr, heartbeat=600,
                                      blocked_connection_timeout=300,
                                      credentials=pika.PlainCredentials("genetic1", "genetic1")))

        channel = connection.channel()
        self._connection = connection

        channel.exchange_declare(exchange='direct_logs',
                                 exchange_type='direct')
        # channel.basic_qos(prefetch_count=len(queues_to_consume))

        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        for queue in queues_to_consume:
            channel.queue_bind(exchange='direct_logs',
                               queue=queue_name,
                               routing_key=queue)

        channel.queue_bind(exchange='direct_logs',
                           queue=queue_name,
                           routing_key=self._confirmation_routing_key)

        self._data_channel = self._Channel(connection=connection, queue_name=queue_name
                                           , channel=channel, exchange='direct_logs',
                                           exchange_type='direct', routing_key=queue_to_produce)

        self._confirmation_channel = self._Channel(connection=connection, queue_name=queue_name
                                                   , channel=channel, exchange='direct_logs',
                                                   exchange_type='direct',
                                                   routing_key=self._confirmation_routing_key)
        time.sleep(5)

    @log_method()
    def _process(self):
        raise NotImplementedError

    @log_method()
    def _finish_processing(self, received_data):
        raise NotImplementedError

    @log_method()
    def _stop_MPI(self):
        self._connection.close()

    @staticmethod
    def _neighbours(mat, row, col, rows, cols, radius):
        current_element = mat[row][col]
        row_shift = 0
        col_shift = 0
        if row - radius < 0:
            row_shift = abs(row - radius)
            mat = np.roll(mat, row_shift, axis=1)
        elif row + radius >= rows:
            row_shift = (rows - 1) - (row + radius)
            mat = np.roll(mat, row_shift, axis=1)

        if col - radius < 0:
            col_shift = abs(col - radius)
            mat = np.roll(mat, col_shift, axis=0)
        elif col + radius >= cols:
            col_shift = (cols - 1) - (col + radius)
            mat = np.roll(mat, col_shift, axis=0)

        kx = np.arange(row - radius + row_shift, row + radius + row_shift + 1)
        ky = np.arange(col - radius + col_shift, col + radius + col_shift + 1)

        channels = np.take(np.take(mat, ky, axis=1), kx, axis=0)
        channels = channels.ravel()
        channels = np.unique(channels)
        return list(map(int, np.delete(channels, np.argwhere(channels == current_element))))

    @log_method()
    def initialize_topology(self):
        channels_to_return = []
        radius = self._neighbourhood_size
        mat = np.arange(self._population_size).reshape(self._population_size_x,
                                                       self._population_size_y)
        for x in range(self._population_size_x):
            for z in range(self._population_size_y):
                channels = [int(mat[x][z]), self._neighbours(mat, x, z, self._population_size_x,
                                                             self._population_size_y, radius)]
                channels_to_return.append(channels)
        return channels_to_return

    @log_method()
    def _send_data(self, channel, data):
        """
        Sends chosen individuals to neighbouring demes
        """
        channel.channel.basic_publish(exchange=channel.exchange,
                                      routing_key=channel.routing_key,
                                      body=json.dumps(data))

    @log_method()
    @timeout(60)
    def _collect_data(self, generation):
        """
        Collects individual's data from neighbouring demes
        :returns best individual from neighbouring demes
        """
        cnt_neighbour_ack = 0
        neighbours = self._Individuals()
        confirmation_sent = False
        while neighbours.size_of_col() != self._num_of_neighbours\
                and cnt_neighbour_ack != self._population_size:
            method_frame, header_frame, body = self._data_channel.channel.basic_get(queue=str(
                self._data_channel.queue_name),
                no_ack=True)
            if body:
                received = json.loads(body)
                logger.info("RECEIVED " + str(received) + " expect " + str(generation))
                if isinstance(received, int):
                    if received == generation:
                        cnt_neighbour_ack = cnt_neighbour_ack + 1
                        continue
                    else:
                        continue
                # logger.info(self._queue_to_produce + " Received the data: " + str(received))
                self._parse_received_data(neighbours, received)
                # self._data_channel.channel.basic_ack(method_frame.delivery_tag)
            else:
                time.sleep(0.2)
            if neighbours.size_of_col() == self._num_of_neighbours and not confirmation_sent:
                self._send_data(self._confirmation_channel, generation)
                confirmation_sent = True
        return neighbours

    @log_method()
    def _parse_received_data(self, body, neighbours):
        raise NotImplementedError

    @log_method()
    def _store_initial_data(self, initial_data):
        raise NotImplementedError

    @log_method()
    @timeout(60)
    def _synchronize_with_neighbours(self, generation):
        self._send_data(self._confirmation_channel, str(generation))
        cnt = 0
        while cnt != self._population_size:
            method_frame, header_frame, body = self._confirmation_channel.channel.basic_get(
                queue=str(
                    self._confirmation_channel.queue_name),
                no_ack=True)
            if body:
                received = json.loads(body)
                logger.info("Received " + str(body))
                if str(received) != str(generation):
                    continue
                logger.info("curr " + str(cnt) + " needed " + str(self._population_size))

                # self._confirmation_channel.channel.basic_ack(method_frame.delivery_tag)
                cnt = cnt + 1
            else:
                logger.info("Not received")
                time.sleep(0.2)

    def __call__(self, initial_data, channels):
        to_return = []
        self._store_initial_data(initial_data)
        logger.info("Process started with initial data " + str(initial_data) +
                    " and channels " + str(channels))

        self._start_MPI(channels)

        for generation in range(0, self._number_of_generations):
            logger.info("NUM " + str(self._number_of_generations))
            logger.info("GENERATION " + str(generation))
            data = self._process()
            self._send_data(self._data_channel, data)
            received_data = self._collect_data(generation)
            #self._synchronize_with_neighbours(generation)
            chosen_individuals_from_neighbours = self._choose_individuals_based_on_fitness(
                received_data)
            to_return = self._finish_processing(chosen_individuals_from_neighbours)
        return to_return

    class _Channel(object):
        def __init__(self, connection, channel, queue_name, exchange, exchange_type, routing_key):
            self._connection = connection
            self._channel = channel
            self._queue_name = queue_name
            self._exchange = exchange
            self._exchange_type = exchange_type
            self._routing_key = routing_key

        @property
        def connection(self):
            return self._connection

        @property
        def channel(self):
            return self._channel

        @property
        def queue_name(self):
            return self._queue_name

        @property
        def exchange(self):
            return self._exchange

        @property
        def exchange_type(self):
            return self._exchange_type

        @property
        def routing_key(self):
            return self._routing_key
