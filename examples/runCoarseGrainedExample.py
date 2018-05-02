from parallel_ga_processing import algorithmRunners
import math


def fitness(chromosome):
    return sum(gene * gene for gene in chromosome)


if __name__ == '__main__':
    algorithmRunners.run_coarse_grained_ga(population_size=(5, 4), chromosome_size=50,
                          number_of_generations=100,
                          neighbourhood_size=1, server_user="genetic1",
                          server_password="genetic1",
                          server_ip_addr="127.0.0.1", num_of_migrants=1,
                          fitness=fitness)
