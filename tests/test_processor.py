from unittest import TestCase,TestResult
import os
from lookup.processor import ProcessorBase, DirProc, FileProc, SortByWhat

# static consts for setup
testDir = "pathValidityTest"
filterPairs = [((0, "", ""), (0, "", "")),
               ((0, "", ""), (1, "name", "txt")),
               ((1, "", ""), (0, "", "")),
               ((0, "name", ""), (0, "@", "@")),
               ((0, "", "txt"), (0, "@", "@")),
               ((0, "name", ""), (0, "name", "")),
               ((0, "", "txt"), (0, "", "txt")),
               ((0, "name", ""), (0, "name1", "")),
               ((0, "", "tx"), (0, "", "txt"))
               ]
filterResults = [True,
                 True,
                 False,
                 False,
                 False,
                 True,
                 True,
                 True,
                 True
                 ]


class TestProcessorBase(TestCase):

    def setUp(self) -> None:
        os.mkdir(testDir)

    def test_is_path_valid(self):
        self.assertTrue(ProcessorBase.isPathValid("./" + testDir))
        
    # todo: figure out how to report errors in big tests
    def test_apply_filter(self):
        for i in range(len(filterPairs)):
            reqs = {"sortBy": SortByWhat.SIZE,
                    "rootDir": '.',
                    "minSize": filterPairs[i][0][0],
                    "nameFilter": filterPairs[i][0][1],
                    "typeFilter": filterPairs[i][0][2]}
            testObject = ProcessorBase(reqs)
            self.assertEqual(testObject.applyFilter(
                Name=filterPairs[i][1][1],
                Type=filterPairs[i][1][2],
                Size=filterPairs[i][1][0]), filterResults[i])

    def tearDown(self) -> None:
        os.rmdir(testDir)



class TestDirProc(TestCase):
    def test_dir_scan(self):
        pass

    def test_process(self):
        pass


class TestFileProc(TestCase):
    def test_file_scan(self):
        pass

    def test_process(self):
        pass
