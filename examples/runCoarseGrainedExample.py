from parallel_ga_processing import algorithmRunners
import math


def fitness(chromosome):
    return sum(gene * gene for gene in chromosome)


if __name__ == '__main__':
    algorithmRunners.run_coarse_grained_ga(population_size=(6, 6), deme_size=10, chromosome_size=4,
                          number_of_generations=10,
                          neighbourhood_size=1, server_user="genetic1",
                          server_password="genetic1",
                          server_ip_addr="127.0.0.1", num_of_migrants=1,
                          fitness=fitness)
