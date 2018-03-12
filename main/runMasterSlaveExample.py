from algorithmRunners import masterSlaveRunner

if __name__ == '__main__':
    masterSlaveRunner.master_slave_runner(population_size=10, chromosome_size=4,
                      number_of_generations=100)