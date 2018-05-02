from parallel_ga_processing.geneticAlgorithms import MasterSlaveBase
import math


class MasterSlave(MasterSlaveBase):

    def fitness(chromosome):
        return sum(gene * gene for gene in chromosome)
