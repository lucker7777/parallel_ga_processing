from geneticAlgorithms.coarseGrained import CoarseGrained
from scoop import futures, logger


if __name__ == '__main__':
    population_size = 10
    ins = CoarseGrained(population_size=population_size, chromosome_size=4,
                      number_of_generations=100, server_ip_addr="127.0.0.1",
                      num_of_neighbours=3, neighbourhood_size=3)
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
