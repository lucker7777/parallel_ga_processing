from geneticAlgorithms.masterSlave import MasterSlave
from scoop import logger


def master_slave_runner(population_size, chromosome_size,
                      number_of_generations):
    ins = MasterSlave(population_size=population_size, chromosome_size=chromosome_size,
                      number_of_generations=number_of_generations)
    solution, sol_vec = ins(None, None)
    logger.info("FINAL RESULT: weight: " + str(solution) + " vector: " + str(sol_vec))
    return solution, sol_vec
