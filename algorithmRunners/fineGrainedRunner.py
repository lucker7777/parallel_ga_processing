from geneticAlgorithms.fineGrained import FineGrained
from scoop import futures, logger


def fine_grained_runner(population_size, chromosome_size, number_of_generations, num_of_neighbours,
    neighbourhood_size, server_ip_addr):
    ins = FineGrained(population_size=population_size, chromosome_size=chromosome_size,
                      number_of_generations=number_of_generations, server_ip_addr=server_ip_addr,
                      num_of_neighbours=num_of_neighbours, neighbourhood_size=neighbourhood_size)
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
