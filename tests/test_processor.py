from unittest import TestCase, TestResult
import os
from shutil import rmtree
import pathlib
from lookup.processor import ProcessorBase, DirProc, FileProc, SortByWhat, \
    DefaultReqs

# static consts for setup
testDataDir = "testData"
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


# todo add finally for testdata clean up
# todo fix pathlib pathes for cross platform
def setDirStruct(dirData=None, fileData=None):  # would be bad if out of memory
    # set up dir/file Scan and testRes

    fileName = "tFile_"
    fileExt = "tst"
    dirNumber = 4
    fileNumber = 4
    dirList = [testDataDir]
    for i in range(1, dirNumber):
        dirList.append(str(pathlib.Path(f"{testDataDir}/tDir{i}")))
    for d in range(len(dirList)):
        dirSize = 0
        if dirList[d] != testDataDir:
            os.mkdir(dirList[d])
        for i in range(1, fileNumber):
            f = open(f"{dirList[d]}/{fileName}{i+d}.{fileExt}{i+d}", "wb")
            f.seek(1024*(i+d)-1)
            f.write(b"\0")
            f.close()
            if dirData is not None:
                dirData[0][0] += 1024*(i+d)
                if dirList[d] != testDataDir:
                    dirSize += 1024*(i+d)
            if fileData is not None:
                fileData.append((f"{fileName}{i+d}", f"{fileExt}{i+d}", 1024*(i+d)))
        if dirData is not None and dirList[d] != testDataDir:
            dirData[1].append((dirList[d], dirSize))


class TestProcessorBase(TestCase):

    def setUp(self) -> None:
        os.mkdir(testDataDir)
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

    def tearDown(self) -> None:
        rmtree(testDataDir)


class TestDirProc(TestCase):

    def setUp(self) -> None:
        # init testData folder
        if not os.path.exists(testDataDir):
            os.mkdir(testDataDir)
        # sum of file sizes in dir Scan
        self.dirScanExpectedSum = [0]
        # list of all test dirNames and its sizes
        self.testDirRes = []
        # dir scan init
        setDirStruct(dirData=[self.dirScanExpectedSum, self.testDirRes])

    def test_dir_scan(self):
        testSum = [0]
        proc = DirProc()
        proc.dirScan(testSum, pathlib.Path(testDataDir))
        self.assertEqual(self.dirScanExpectedSum[0], testSum[0])

    def test_process(self):
        reqs = DefaultReqs
        reqs["rootDir"] = testDataDir
        sorts = [SortByWhat.NAME, SortByWhat.SIZE]
        for i in range(len(sorts)):
            reqs["sortBy"] = sorts[i]
            proc = DirProc(reqs)
            testData = proc.process()
            self.testDirRes.sort(key=lambda x: x[i], reverse=i)
            self.assertEqual(testData, self.testDirRes)

    def tearDown(self) -> None:
        rmtree(testDataDir)


class TestFileProc(TestCase):

    def setUp(self) -> None:
        # init testData folder
        if not os.path.exists(testDataDir):
            os.mkdir(testDataDir)
        # list of all test FileNames, exts and its sizes
        self.testFileRes = []
        # dir scan init
        setDirStruct(fileData=self.testFileRes)

# todo: having troubles with sort when text elems are equal or have symbols
    def test_process(self):
        reqs = DefaultReqs
        reqs["rootDir"] = testDataDir
        sorts = [SortByWhat.NAME, SortByWhat.TYPE, SortByWhat.SIZE]
        for i in range(len(sorts)):
            reqs["sortBy"] = sorts[i]
            proc = FileProc(reqs)
            testData = proc.process()
            reverse = False
            if sorts[i] == SortByWhat.SIZE:
                reverse = True
            self.testFileRes.sort(key=lambda x: x[i], reverse=reverse)
            self.assertEqual(testData, self.testFileRes)

    def tearDown(self) -> None:
        rmtree(testDataDir)
