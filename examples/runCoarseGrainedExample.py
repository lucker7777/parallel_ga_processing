from parallel_ga_processing.algorithmRunners import run_coarse_grained_ga
import math


def fitness(chromosome):
    return 10 - sum(gene*gene for gene in chromosome)


if __name__ == '__main__':
    run_coarse_grained_ga(population_size=(6, 6), chromosome_size=4,
                          number_of_generations=100,
                          neighbourhood_size=1, server_ip_addr="127.0.0.1", num_of_migrants=1,
                          fitness=fitness)
