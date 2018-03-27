from algorithmRunners import run_coarse_grained_ga
import math


def fitness(chromosome):
    first_sum = 0.0
    second_sum = 0.0
    for c in chromosome:
        first_sum += c ** 2.0
        second_sum += math.cos(2.0 * math.pi * c)
    n = float(len(chromosome))
    return 10 - (-20.0 * math.exp(-0.2 * math.sqrt(first_sum / n)) - math.exp(
        second_sum / n) + 20 + math.e)


if __name__ == '__main__':
    run_coarse_grained_ga(population_size=10, chromosome_size=4,
                          number_of_generations=100, num_of_neighbours=3,
                          neighbourhood_size=3, server_ip_addr="127.0.0.1", fitness=fitness)
