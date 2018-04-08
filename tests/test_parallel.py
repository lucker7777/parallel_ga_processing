from unittest import TestCase
from parallel_ga_processing.algorithmRunners import launch

path = "/home/martin/parallel_ga_processing/examples"


class TestParallel(TestCase):
    def testFineGrained(self):
        executable = "runFineGrainedExample.py"
        launch(["localhost"], 36, path, executable)

    def testCoarseGrained(self):
        executable = "runCoarseGrainedExample.py"
        launch(["localhost"], 36, path, executable)

    def testMasterSlaveGrained(self):
        executable = "runMasterSlaveExample.py"
        launch(["localhost"], 10, path, executable)
