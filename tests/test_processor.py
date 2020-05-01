from unittest import TestCase, TestResult
import os
import pathlib
from lookup.processor import ProcessorBase, DirProc, FileProc, SortByWhat, \
    DefaultReqs

# static consts for setup
testDataDir = DefaultReqs["rootDir"] + "/testData"
testDir = testDataDir + "/pathValidityTest"
filterPairs = {((0, "", ""), (0, "", "")): True,
               ((0, "", ""), (1, "name", "txt")): True,
               ((1, "", ""), (0, "", "")): False,
               ((0, "name", ""), (0, "@", "@")): False,
               ((0, "", "txt"), (0, "@", "@")): False,
               ((0, "name", ""), (0, "name", "")): True,
               ((0, "", "txt"), (0, "", "txt")): True,
               ((0, "name", ""), (0, "name1", "")): True,
               ((0, "", "tx"), (0, "", "txt")): True
               }

# list of all test dirNames and its sizes
testDirRes = []
# list of all test FileNames, exts and its sizes
testFileRes = []

# init testData folder
if not os.path.exists(testDataDir):
    os.mkdir(testDataDir)


def setDirStruct(dirData=None, fileData=None):  # would be bad if out of memory
    # set up dir/file Scan and testRes
    fileName = "tFile_"
    fileExt = "tst"
    for i in range(1, 4):
        f = open(f"{testDataDir}/{fileName}{i}.{fileExt}", "wb")
        f.seek(1024*i-1)
        f.write(b"\0")
        f.close()
        if dirData is not None:
            dirData[0] += 1024*i
        if fileData is not None:
            fileData.append((f"{fileName}{i}", fileExt, 1024*i))


def unSetDirStruct(): pass


class TestProcessorBase(TestCase):

    def setUp(self) -> None:
        os.mkdir(testDir)

    def test_is_path_valid(self):
        self.assertTrue(ProcessorBase.isPathValid(testDir))

    # todo: figure out how to report errors in big tests
    def test_apply_filter(self):
        for k, v in filterPairs.items():
            try:
                reqs = {"sortBy": SortByWhat.SIZE,
                        "rootDir": '.',
                        "minSize": k[0][0],
                        "nameFilter": k[0][1],
                        "typeFilter": k[0][2]}
                testObject = ProcessorBase(reqs)
                self.assertEqual(testObject.applyFilter(
                    Name=k[1][1],
                    Type=k[1][2],
                    Size=k[1][0]), v)
            except AssertionError:
                print("test_apply_filter: fail at case {} == {}".format(k, v))
                raise AssertionError

    def tearDown(self) -> None:  # Todo
        os.rmdir(testDir)


class TestDirProc(TestCase):

    def setUp(self) -> None:
        # sum of file sizes in dir Scan
        self.dirScanExpectedSum = [0]
        # dir scan init
        setDirStruct(dirData=self.dirScanExpectedSum)

    def test_dir_scan(self):
        testSum = [0]
        proc = DirProc()
        proc.dirScan(testSum, pathlib.Path(testDataDir))
        self.assertEqual(self.dirScanExpectedSum[0], testSum[0])

    def test_process(self):  # Todo
        proc = DirProc()
        self.assertEqual(testDirRes, proc.process())

    def tearDown(self) -> None:  # Todo
        unSetDirStruct()


class TestFileProc(TestCase):

    def setUp(self) -> None:
        # expected ist of all file names, exts, sizes
        self.fileScanRes = []
        # dir scan init
        setDirStruct(fileData=self.fileScanRes)

    def test_file_scan(self):
        testData = []
        proc = FileProc()
        proc.fileScan(testData, pathlib.Path(testDataDir))
        self.assertEqual(testData, self.fileScanRes)

    def test_process(self):  # Todo
        proc = FileProc()
        self.assertEqual(testFileRes, proc.process())

    def tearDown(self) -> None:  # Todo
        unSetDirStruct()
