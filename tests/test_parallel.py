from unittest import TestCase
from algorithmRunners import launch

path = "/tmp/parallelGA/examples"


class TestParallel(TestCase):
    def testFineGrained(self):
        executable = "runFineGrainedExample.py"
        launch(["localhost", "remote1@remote1-VirtualBox"], 10, path, executable)

    def testCoarseGrained(self):
        executable = "runCoarseGrainedExample.py"
        launch(["localhost", "remote1@remote1-VirtualBox"], 10, path, executable)

    def testMasterSlaveGrained(self):
        executable = "runMasterSlaveExample.py"
        launch(["localhost", "remote1@remote1-VirtualBox"], 10, path, executable)
