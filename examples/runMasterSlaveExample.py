from parallel_ga_processing import algorithmRunners
import math
from scoop import logger


def fitness(chromosome):
    return sum(gene * gene for gene in chromosome)


if __name__ == '__main__':
    algorithmRunners.run_master_slave_ga(population_size=20, chromosome_size=5,
                        number_of_generations=100, fitness=fitness)
