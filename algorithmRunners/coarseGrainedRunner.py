from geneticAlgorithms.coarseGrained import CoarseGrained
from scoop import futures, logger


def coarse_grained_runner(population_size, chromosome_size,
                      number_of_generations, server_ip_addr,
                      num_of_neighbours, neighbourhood_size):
    ins = CoarseGrained(population_size=population_size, chromosome_size=chromosome_size,
                      number_of_generations=number_of_generations, server_ip_addr=server_ip_addr,
                      num_of_neighbours=num_of_neighbours, neighbourhood_size=neighbourhood_size)
    populations = []
    for i in range(0, population_size):
        populations.append(ins.initialize_population())
    channels = ins.initialize_topology()
    result = list(futures.map(ins, populations, channels))
    dct = {}
    logger.info("fuuu")
    while len(result):
        fitness_val, vector = result.pop(0)
        dct[fitness_val] = vector
    logger.info("END RESULTTTTTT " + str(sorted(dct.items()).pop()))
