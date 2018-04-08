from parallel_ga_processing.algorithmRunners import run_master_slave_ga
import math
from scoop import logger


def fitness(chromosome):
    logger.info("REMOTE")
    first_sum = 0.0
    second_sum = 0.0
    for c in chromosome:
        first_sum += c ** 2.0
        second_sum += math.cos(2.0 * math.pi * c)
    n = float(len(chromosome))
    return 10 - (-20.0 * math.exp(-0.2 * math.sqrt(first_sum / n)) - math.exp(
        second_sum / n) + 20 + math.e)


if __name__ == '__main__':
    run_master_slave_ga(population_size=10, chromosome_size=4,
                        number_of_generations=100, fitness=fitness)
