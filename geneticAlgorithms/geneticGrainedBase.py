import abc
from scoop import logger
from .geneticBase import GeneticAlgorithmBase


class GrainedGeneticAlgorithmBase(GeneticAlgorithmBase, metaclass=abc.ABCMeta):
    def __init__(self, population_size, chromosome_size, number_of_generations):
        super().__init__(population_size, chromosome_size,
                         number_of_generations)
        self._population_size = population_size
        self._chromosome_size = chromosome_size
        self._number_of_generations = number_of_generations

    @abc.abstractmethod
    def fitness(self, chromosome):
        pass

    def _find_solution(self, population):
        """
        Find the best solution
        :param population
        :return: best_weight, chromosome
        """
        max_val = 0
        max_index = None
        for i in range(0, self._population_size):
            curr_fit = self.fitness(population[i])
            if curr_fit > max_val:
                max_val = curr_fit
                max_index = i
        return max_val, population[max_index]

    @abc.abstractmethod
    def _start_MPI(self, channels):
        pass

    @abc.abstractmethod
    def _process(self, chromosome):
        pass

    @abc.abstractmethod
    def _send_data(self, data):
        pass

    @abc.abstractmethod
    def _collect_data(self):
        pass

    @abc.abstractmethod
    def _finish_processing(self, received_data, data):
        pass

    @abc.abstractmethod
    def _stop_MPI(self):
        pass

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
