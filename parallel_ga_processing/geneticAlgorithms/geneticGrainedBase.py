import uuid
import time
import numpy as np
from scoop import logger
from .decorator import log_method
from .decorator import timeout
from .geneticBase import GeneticAlgorithmBase
from enum import Enum
from .messenger import Messenger
from .messenger import ProductionQueue


class GrainedGeneticAlgorithmBase(GeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations,
                 neighbourhood_size, server_ip_addr, server_user,
                 server_password,
                 fitness):
        self._population_size_x, self._population_size_y = population_size
        super().__init__(population_size=self._population_size_x * self._population_size_y,
                         chromosome_size=chromosome_size,
                         number_of_generations=number_of_generations, fitness=fitness)
        self._num_of_neighbours = pow((2 * neighbourhood_size) + 1, 2) - 1
        self._neighbourhood_size = neighbourhood_size
        self._check_population_size(self._population_size_x, self._neighbourhood_size)
        self._check_population_size(self._population_size_y, self._neighbourhood_size)

        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations

        self._server_ip_addr = server_ip_addr
        self._data_channel = None
        self._confirmation_channel = None
        self._connection = None
        self._server_user = server_user
        self._server_password = server_password
        self._producing_queue = ProductionQueue()
        self._data_consuming_queue = ProductionQueue()

        self._queues_to_consume = None
        self._queue_to_produce = None

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
        for x in population:
            curr_fit = self._fitness(x)
            data.append_object(self._Individual(curr_fit, x))
        return data.sort_objects()[:num_of_best_chromosomes]

    @log_method()
    def _start_MPI(self, channels):
        self._queue_to_produce = str(channels.pop(0))
        self._queues_to_consume = list(map(str, channels.pop(0)))
        logger.info("starting processing to queue: " + self._queue_to_produce
                    + " and consuming from: " + str(self._queues_to_consume))
        msg = Messenger(server_user=self._server_user, server_password=self._server_password,
                        server_ip_addr=self._server_ip_addr,
                        exchange="data",
                        exchange_type="direct",
                        queue=str(uuid.uuid4()),
                        subscription_routing_keys=list(self._queues_to_consume),
                        produced_messages=self._producing_queue,
                        consumed_messages=self._data_consuming_queue)
        self._messenger = msg
        self._messenger.start()
        time.sleep(1)

    @log_method()
    def _process(self):
        raise NotImplementedError

    @log_method()
    def _finish_processing(self, received_data):
        raise NotImplementedError

    @log_method()
    def _stop_MPI(self):
        self._messenger.stop_consuming()

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
        logger.info(str(mat))
        for x in range(self._population_size_x):
            for z in range(self._population_size_y):
                channels = [int(mat[x][z]), self._neighbours(mat, x, z, self._population_size_x,
                                                             self._population_size_y, radius)]
                channels_to_return.append(channels)
        logger.info(str(channels_to_return))
        return channels_to_return

    @log_method()
    def _collect_data(self, current_generation):
        """
        Collects individual's data from neighbouring demes
        :returns best individual from neighbouring demes
        """
        neighbours = self._Individuals()
        while True:

            if self._check_collected_data(neighbours):
                break
            if not self._data_consuming_queue.is_ready(current_generation):
                continue
            data = self._data_consuming_queue.consume_message(current_generation)
            if current_generation != data.generation:
                continue

            self._parse_received_data(neighbours, int(data.source), data.data)

            logger.info("RECEIVED data" + str(data.data) + str(data.source))

        return neighbours

    def _send_data(self, data, generation):
        self._producing_queue.add_message(generation, Data(generation,
                                                           self._queue_to_produce,
                                                           self._queue_to_produce, data))

    def _check_collected_data(self, neighbours):
        raise NotImplementedError

    @log_method()
    def _parse_received_data(self, neighbours, source, body):
        raise NotImplementedError

    def _parse_confirmation_data(self, neighbours, source, received_data):
        neighbours.append_object(self._Individual(fit=None, chromosome=None, value=received_data),
                                 source)

    @log_method()
    def _store_initial_data(self, initial_data):
        raise NotImplementedError

    def __call__(self, initial_data, channels):
        to_return = []
        self._store_initial_data(initial_data)
        self._start_MPI(channels)
        for generation in range(0, self._number_of_generations):
            logger.info("GENERATION " + str(generation))
            data = self._process()
            self._send_data(data, generation)

            received_data = self._collect_data(generation)
            chosen_individuals_from_neighbours = self._choose_individuals_based_on_fitness(
                received_data)
            to_return = self._finish_processing(chosen_individuals_from_neighbours)
        self._stop_MPI()
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


class Data(object):
    def __init__(self, generation, source, routing_key, data):
        self._generation = generation
        self._source = source
        self._routing_key = routing_key
        self._data = data

    @property
    def generation(self):
        return self._generation

    @property
    def source(self):
        return self._source

    @property
    def routing_key(self):
        return self._routing_key

    @property
    def data(self):
        return self._data
