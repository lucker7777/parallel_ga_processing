from geneticAlgorithms.fineGrained import FineGrained
from scoop import futures, logger


if __name__ == '__main__':
    ins = FineGrained(population_size=10, chromosome_size=4,
                      number_of_generations=100, server_ip_addr="127.0.0.1",
                      num_of_neighbours=3, neighbourhood_size=3)
    popula = ins.initialize_population()
    channels = ins.initialize_topology()
    logger.info("SIZE " + str(len(popula))+str(len(channels)))
    result = list(futures.map(ins, popula, channels))
    dct = {}
    logger.info("fuuu")
    while len(result):
        fitness_val, vector = result.pop(0)
        dct[fitness_val] = vector
    logger.info("END RESULTTTTTT " + str(sorted(dct.items()).pop()))
