from scoop import futures, logger
from parallel_ga_processing.geneticAlgorithms import FineGrainedBase


def run_fine_grained_ga(population_size, chromosome_size,
                        number_of_generations,
                        neighbourhood_size, server_ip_addr, fitness,
                        server_user, server_password,
                        mate_best_neighbouring_individual=True):
    ins = FineGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                          number_of_generations=number_of_generations,
                          neighbourhood_size=neighbourhood_size, server_ip_addr=server_ip_addr,
                          fitness=fitness,
                          mate_best_neighbouring_individual=mate_best_neighbouring_individual,
                          server_user=server_user, server_password=server_password)
    populations = ins.initialize_population(None)
    channels = ins.initialize_topology()
    result = list(futures.map(ins, populations, channels))
    dct = {}

    while len(result):
        fitness_val, vector = result.pop(0)
        dct[fitness_val] = vector
    logger.info("END RESULT " + str(sorted(dct.items()).pop()))


def run_fine_grained_ga_remote(population_size, chromosome_size,
                        number_of_generations,
                        neighbourhood_size, server_ip_addr, fitness,
                        server_user, server_password,
                        mate_best_neighbouring_individual=True):
    ins = FineGrainedBase(population_size=population_size, chromosome_size=chromosome_size,
                          number_of_generations=number_of_generations,
                          neighbourhood_size=neighbourhood_size, server_ip_addr=server_ip_addr,
                          fitness=fitness,
                          mate_best_neighbouring_individual=mate_best_neighbouring_individual,
                          server_user=server_user, server_password=server_password)
