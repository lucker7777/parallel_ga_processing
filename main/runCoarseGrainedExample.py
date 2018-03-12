from algorithmRunners import coarseGrainedRunner

if __name__ == '__main__':
    coarseGrainedRunner.coarse_grained_runner(population_size=10, chromosome_size=4,
                      number_of_generations=100, num_of_neighbours=3,
    neighbourhood_size=3, server_ip_addr="127.0.0.1")