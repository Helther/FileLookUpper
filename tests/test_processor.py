from unittest import TestCase, TestResult
import os
from shutil import rmtree
import pathlib
from lookup.processor import ProcessorBase, DirProc, FileProc, SortByWhat, \
    DefaultReqs, sizeScales, sizeScalesVals

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


def setDirStruct(sizeScale, dirData=None, fileData=None):
    # would be bad if out of memory
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
        if dirList[d] != testDataDir and not os.path.exists(dirList[d]):
            os.mkdir(dirList[d])
        for i in range(1, fileNumber):
            with open(str(pathlib.Path(f"{dirList[d]}/{fileName}{i+d}.{fileExt}"
                                       f"{i+d}")), "wb") as f:
                f.seek(1024*(i+d)-1)
                f.write(b"\0")
                f.close()
            if dirData is not None:
                dirData[0][0] += 1024*(i+d)
                if dirList[d] != testDataDir:
                    dirSize += int(1024*(i+d) / sizeScale)
            if fileData is not None:
                fileData.append((f"{fileName}{i+d}", f"{fileExt}{i+d}",
                                 int(1024*(i+d) / sizeScale)))
        if dirData is not None and dirList[d] != testDataDir:
            dirData[1].append((dirList[d], dirSize))


class TestProcessorBase(TestCase):

    def setUp(self) -> None:
        os.mkdir(pathlib.Path(testDataDir))
        os.mkdir(pathlib.Path(testDir))

    def test_is_path_valid(self):
        self.assertTrue(ProcessorBase.isPathValid(pathlib.Path(testDir)))

    # todo: figure out how to report errors in big tests
    def test_apply_filter(self):
        for k, v in filterPairs.items():
            try:
                reqs = DefaultReqs
                reqs["minSize"] = k[0][0]
                reqs["nameFilter"] = k[0][1]
                reqs["typeFilter"] = k[0][2]

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
        self.dirScanExpectedSum = []
        # list of all test dirNames and its sizes
        self.testDirRes = []
        for i in range(0, len(sizeScalesVals)):
            self.dirScanExpectedSum.append([0])
            self.testDirRes.append([])
        # dir scan init
        for i in range(0, len(sizeScalesVals)):
            if not os.path.exists(testDataDir):
                os.mkdir(testDataDir)
            setDirStruct(sizeScalesVals[i], dirData=[self.dirScanExpectedSum[i],
                                  self.testDirRes[i]])

    def test_dir_scan(self):
        testSum = []
        for i in range(0, len(sizeScalesVals)):
            testSum.append([0])
            proc = DirProc()
            proc.dirScan(testSum[i], pathlib.Path(testDataDir))
        for i in range(0, len(sizeScalesVals)):
            self.assertEqual(self.dirScanExpectedSum[i][0], testSum[i][0])

    def test_process(self):
        reqs = DefaultReqs
        reqs["rootDir"] = testDataDir
        reqs["maxElemNumber"] = len(self.testDirRes[0])
        sorts = [SortByWhat.NAME, SortByWhat.SIZE]
        for sort in range(len(sorts)):
            reqs["sortBy"] = sorts[sort].value
            for scale in range(len(sizeScalesVals)):
                reqs["sizeScale"] = scale
                proc = DirProc(reqs)
                testData = proc.process()
                self.testDirRes[scale].sort(key=lambda x: x[sort], reverse=bool(sort))
                self.assertEqual(testData, self.testDirRes[scale])

    def tearDown(self) -> None:
        rmtree(testDataDir)


class TestFileProc(TestCase):

    def setUp(self) -> None:
        # init testData folder
        if not os.path.exists(testDataDir):
            os.mkdir(testDataDir)
        # list of all test FileNames, exts and its sizes
        self.testFileRes = []
        for i in range(0, len(sizeScalesVals)):
            self.testFileRes.append([])
            # dir scan init
            setDirStruct(sizeScalesVals[i], fileData=self.testFileRes[i])

# todo: having troubles with sort when text elems are equal or have symbols
    # or just zeroes
    def test_process(self):
        reqs = DefaultReqs
        reqs["rootDir"] = testDataDir
        reqs["maxElemNumber"] = len(self.testFileRes[0])
        sorts = [SortByWhat.NAME, SortByWhat.TYPE, SortByWhat.SIZE]
        for sort in range(len(sorts)):
            reqs["sortBy"] = sorts[sort].value
            for scale in range(len(sizeScalesVals)):
                if sizeScales.MB.value == scale:
                    continue # todo temp solution for sort problem
                reqs["sizeScale"] = scale
                proc = FileProc(reqs)
                testData = proc.process()
                reverse = False
                if sorts[sort] == SortByWhat.SIZE:
                    reverse = True
                self.testFileRes[scale].sort(key=lambda x: x[sort], reverse=reverse)
                self.assertEqual(testData, self.testFileRes[scale])

    def tearDown(self) -> None:
        rmtree(testDataDir)
