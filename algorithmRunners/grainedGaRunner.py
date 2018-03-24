from scoop import futures, logger
from geneticAlgorithms import GrainedGeneticAlgorithmBase


def run_grained_ga(genetic_algorithm):
    if not isinstance(genetic_algorithm, GrainedGeneticAlgorithmBase):
        logger.info("Wrong instance")
        raise TypeError("Wrong instance of genetic algorithm class.")

    populations = genetic_algorithm.initialize_population()
    channels = genetic_algorithm.initialize_topology()
    result = list(futures.map(genetic_algorithm, populations, channels))
    dct = {}
    logger.info("fuuu")
    while len(result):
        fitness_val, vector = result.pop(0)
        dct[fitness_val] = vector
    logger.info("END RESULTTTTTT " + str(sorted(dct.items()).pop()))
