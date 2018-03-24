from geneticAlgorithms import geneticGrainedBase
import time
import pika
import json
from scoop import logger
import abc


class FineGrainedBase(geneticGrainedBase.GrainedGeneticAlgorithmBase, metaclass=abc.ABCMeta):
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
        self._server_ip_addr = server_ip_addr

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

    def _stop_MPI(self):
        self._connection.close()

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

    def _process(self, chromosome):
        fit = self.fitness(chromosome)
        to_send = [float(fit)]
        to_send.extend(list(map(float, chromosome)))
        return to_send

    def _send_data(self, data):
        self._channel.basic_publish(exchange='direct_logs',
                                    routing_key=self._queue_to_produce,
                                    body=json.dumps(data))

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

    def _finish_processing(self, chromosome, mother):
        logger.info("father " + str(chromosome) + " mother " + str(mother))
        mother.pop(0)
        self._crossover(chromosome, mother)
        # mother
        self._mutation(chromosome)
        return self.fitness(chromosome), list(map(float, chromosome))
