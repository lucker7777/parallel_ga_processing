from scoop import logger
from .geneticBase import GeneticAlgorithmBase
import time
import pika
import numpy as np
from .decorator import log_method


class GrainedGeneticAlgorithmBase(GeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, server_ip_addr,
                 neighbourhood_size, fitness):
        super().__init__(population_size, chromosome_size,
                         number_of_generations, fitness)
        self._population_size_x, self._population_size_y = population_size
        self._population_size = self._population_size_x * self._population_size_y
        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations
        self._num_of_neighbours = pow((2 * neighbourhood_size) + 1, 2) - 1
        self._neighbourhood_size = neighbourhood_size
        self._server_ip_addr = server_ip_addr
        self._channel = None
        self._queue_to_produce = None
        self._queues_to_consume = None
        self._queue_name = None
        self._connection = None

    @log_method()
    def _find_solution(self, population, num_of_best_chromosomes):
        """
        Find the best solution
        :param population
        :return: best_weight, chromosome
        """
        data = self._Collect()
        for i in range(0, self._population_size):
            curr_fit = self._fitness(population[i])
            data.append_object(self._Snt(curr_fit, population[i]))
        return data.sort_objects()[:num_of_best_chromosomes]

    @log_method()
    def _start_MPI(self, channels):
        queue_to_produce = str(channels.pop(0))
        queues_to_consume = list(map(str, channels.pop(0)))
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

    @log_method()
    def _process(self, chromosome):
        pass

    @log_method()
    def _send_data(self, data):
        pass

    @log_method()
    def _collect_data(self):
        pass

    @log_method()
    def _finish_processing(self, received_data, data):
        pass

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

    def __call__(self, initial_data, channels):
        to_return = []

        logger.info("Process started with initial data " + str(initial_data) +
                    " and channels " + str(channels))
        self._start_MPI(channels)
        for i in range(0, self._number_of_generations):
            data = self._process(initial_data)
            self._send_data(data)
            received_data = self._collect_data()
            to_return = self._finish_processing(received_data, data)
        return to_return
