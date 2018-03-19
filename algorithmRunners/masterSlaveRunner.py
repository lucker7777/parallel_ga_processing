from geneticAlgorithms.masterSlave import MasterSlave
from scoop import logger


def master_slave_runner(ins):

    solution, sol_vec = ins()
    logger.info("FINAL RESULT: weight: " + str(solution) + " vector: " + str(sol_vec))
    return solution, sol_vec
