from scoop import logger
from geneticAlgorithms import MasterSlaveBase


def run_master_slave_ga(genetic_algorithm):
    if not isinstance(genetic_algorithm, MasterSlaveBase):
        logger.info("Wrong instance")
        raise TypeError("Wrong instance of genetic algorithm class.")

    solution, sol_vec = genetic_algorithm()
    logger.info("FINAL RESULT: weight: " + str(solution) + " vector: " + str(sol_vec))
    return solution, sol_vec
