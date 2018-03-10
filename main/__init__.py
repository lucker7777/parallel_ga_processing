from helpers import launcher

if __name__ == '__main__':
    path = "/home/martin/PycharmProjects/parallelGA/geneticAlgorithms/"
    executable = "__init__.py"
    launcher.parallel(["localhost"], 10, path, executable)
