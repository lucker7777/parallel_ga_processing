from parallel_ga_processing import algorithmRunners
import math


def fitness(chromosome):
    return sum(gene * gene for gene in chromosome)


if __name__ == '__main__':
    algorithmRunners.run_fine_grained_ga(population_size=(6, 6), chromosome_size=5,
                        number_of_generations=5,
                        neighbourhood_size=1, server_ip_addr="127.0.0.1", fitness=fitness,
                        mate_best_neighbouring_individual=True, server_user="genetic1", server_password="genetic1")
