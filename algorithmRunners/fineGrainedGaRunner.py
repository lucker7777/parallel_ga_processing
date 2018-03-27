from scoop import futures, logger
from geneticAlgorithms import FineGrainedBase


def run_fine_grained_ga(population_size, chromosome_size,
                        number_of_generations, num_of_neighbours,
                        neighbourhood_size, server_ip_addr, fitness):
    ins = FineGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                          number_of_generations=number_of_generations,
                          num_of_neighbours=num_of_neighbours,
                          neighbourhood_size=neighbourhood_size, server_ip_addr=server_ip_addr,
                          fitness=fitness)
    populations = ins.initialize_population()
    channels = ins.initialize_topology()
    result = list(futures.map(ins, populations, channels))
    dct = {}
    logger.info("fuuu")
    while len(result):
        fitness_val, vector = result.pop(0)
        dct[fitness_val] = vector
    logger.info("END RESULTTTTTT " + str(sorted(dct.items()).pop()))


def run_fine_grained_ga_remote(population_size, chromosome_size,
                               number_of_generations, num_of_neighbours,
                               neighbourhood_size, server_ip_addr, fitness):
    ins = FineGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                          number_of_generations=number_of_generations,
                          num_of_neighbours=num_of_neighbours,
                          neighbourhood_size=neighbourhood_size, server_ip_addr=server_ip_addr,
                          fitness=fitness)
