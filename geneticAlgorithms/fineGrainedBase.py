from geneticAlgorithms import geneticGrainedBase
import time
import pika
import json
from scoop import logger
from .decorator import log_method

class FineGrainedBase(geneticGrainedBase.GrainedGeneticAlgorithmBase):
    def __init__(self, population_size, chromosome_size,
                 number_of_generations, server_ip_addr,
                 neighbourhood_size, fitness):

        super().__init__(population_size, chromosome_size,
                         number_of_generations, server_ip_addr,
                         neighbourhood_size, fitness)

    @log_method()
    def _process(self, chromosome):
        fit = self._fitness(chromosome)
        to_send = [float(fit)]
        to_send.extend(list(map(float, chromosome)))
        return to_send

    @log_method()
    def _send_data(self, data):
        self._channel.basic_publish(exchange='direct_logs',
                                    routing_key=self._queue_to_produce,
                                    body=json.dumps(data))

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
                print("PARSED " + str(fit_val) + " " + str(vector))
                neighbours.append_object(self._Snt(fit_val, vector))
                self._channel.basic_ack(method_frame.delivery_tag)

            else:
                logger.info(self._queue_to_produce + ' No message returned')
        sorted_x = neighbours.sort_objects()
        return sorted_x.pop(0).chromosome

    @log_method()
    def _finish_processing(self, chromosome, mother):
        logger.info("father " + str(chromosome) + " mother " + str(mother))
        mother.pop(0)
        self._crossover(chromosome, mother)
        # mother
        self._mutation(chromosome)
        return self._fitness(chromosome), list(map(float, chromosome))
