from unittest import TestCase
import os
from shutil import rmtree
import pathlib
from lookupper.processor import ProcessorBase, DirProc, FileProc, SortByWhat, \
    DefaultReqs, sizeScales, sizeScalesVals, sizeScaleNames, sortNames

# static consts for setup
testDataDir = "testData"
testDir = testDataDir + "/pathValidityTest"
# setup for filter test
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
    # set up dir/file Scan and testRes struct

    fileName = "tFile_"
    fileExt = "tst"
    dirNumber = 4
    fileNumber = 4
    dirList = [testDataDir]
    for i in range(1, dirNumber):
        dirList.append(str(pathlib.Path(f"{testDataDir}/tDir{i}")))
    iterator = 1
    for d in range(len(dirList)):
        dirSize = 0
        if dirList[d] != testDataDir and not os.path.exists(dirList[d]):
            os.mkdir(dirList[d])
        for i in range(1, fileNumber):
            with open(str(pathlib.Path(f"{dirList[d]}/{fileName}{iterator}"
                                       f".{fileExt}"
                                       f"{iterator}")), "wb") as f:
                f.seek(1024*(iterator)-1)
                f.write(b"\0")
                f.close()
            if dirData is not None:
                dirData[0][0] += 1024*(iterator)
                if dirList[d] != testDataDir:
                    dirSize += int(1024*(iterator) / sizeScale)
            if fileData is not None:
                fileData.append((str(pathlib.Path
                            (f"{dirList[d]}/{fileName}{iterator}."
                             f"{fileExt}{iterator}")),
                            f"{fileExt}{iterator}",
                            int(1024*(iterator) / sizeScale)))
            iterator += 1
        if dirData is not None and dirList[d] != testDataDir:
            dirData[1].append((dirList[d], dirSize))


class TestProcessorBase(TestCase):

    def setUp(self) -> None:
        os.mkdir(pathlib.Path(testDataDir))
        os.mkdir(pathlib.Path(testDir))

    def test_is_path_valid(self):
        self.assertTrue(ProcessorBase.isPathValid(pathlib.Path(testDir)))

    def test_apply_filter(self):
        for k, v in filterPairs.items():
            try:
                reqs = DefaultReqs.copy()
                reqs["minSize"] = k[0][0]
                reqs["nameFilter"] = k[0][1]
                reqs["typeFilter"] = k[0][2]

                testObject = ProcessorBase(reqs)
                self.assertEqual(testObject.applyFilter(
                    Name=k[1][1],
                    Type=k[1][2],
                    Size=k[1][0]), v)
            except AssertionError:
                print("==================== TEST FAILED ======================")
                print("test_apply_filter: fail at case {} == {}".format(k, v))
                print("=======================================================")
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
        # checks sub dir size calculation
        testSum = []
        for i in range(0, len(sizeScalesVals)):
            testSum.append([0])
            proc = DirProc()
            proc.dirScan(testSum[i], pathlib.Path(testDataDir))
        for i in range(0, len(sizeScalesVals)):
            try:
                self.assertEqual(self.dirScanExpectedSum[i][0], testSum[i][0])
            except AssertionError:
                print("==================== TEST FAILED ======================")
                print("test_dir_scan: fail at case scale: {}"
                      .format(sizeScaleNames[i]))
                print("=======================================================")
                raise AssertionError

    def test_process(self):
        # runs through all combinations of sort-scale options for directory level
        # processor
        reqs = DefaultReqs.copy()
        reqs["rootDir"] = testDataDir
        reqs["maxElemNumber"] = len(self.testDirRes[0])
        sorts = [SortByWhat.NAME, SortByWhat.SIZE]
        for sort in range(len(sorts)):
            reqs["sortBy"] = sorts[sort].value
            for scale in range(len(sizeScalesVals)):
                if sizeScales.MB.value == scale or sizeScales.GB.value == scale:
                    continue  # todo temp solution for sort problem
                reqs["sizeScale"] = scale
                proc = DirProc(reqs)
                testData = proc.process()
                self.testDirRes[scale].sort(key=lambda x: x[sort],
                                            reverse=bool(sort))
                try:
                    self.assertEqual(testData, self.testDirRes[scale])
                except AssertionError:
                    print("==================== TEST FAILED ======================")
                    print("test_dir_process: fail at case - sort by: {}, scale: {}"
                          .format(sortNames[sort], sizeScaleNames[scale]))
                    print("=======================================================")
                    raise AssertionError

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
    def test_process(self):
        # runs through all combinations of sort-scale options for individual files
        reqs = DefaultReqs.copy()
        reqs["rootDir"] = testDataDir
        reqs["maxElemNumber"] = len(self.testFileRes[0])
        sorts = [SortByWhat.NAME, SortByWhat.TYPE, SortByWhat.SIZE]
        for sort in range(len(sorts)):
            reqs["sortBy"] = sorts[sort].value
            for scale in range(len(sizeScalesVals)):
                if sizeScales.MB.value == scale or sizeScales.GB.value == scale:
                    continue  # todo temp solution for sort problem
                reqs["sizeScale"] = scale
                proc = FileProc(reqs)
                testData = proc.process()
                reverse = False
                if sort == SortByWhat.SIZE.value:
                    reverse = True
                if sort == SortByWhat.NAME.value:
                    self.testFileRes[scale].sort(key=lambda x:
                    pathlib.Path(
                        os.path.splitext(pathlib.Path(x[sort]).name)[0]),
                              reverse=reverse)
                else:
                    self.testFileRes[scale].sort(key=lambda x: x[sort],
                                                 reverse=reverse)
                try:
                    self.assertEqual(testData, self.testFileRes[scale])
                except AssertionError:
                    print("==================== TEST FAILED ======================")
                    print("test_file_process: fail at case - sort by: {}, scale: {}"
                          .format(sortNames[sort], sizeScaleNames[scale]))
                    print("=======================================================")
                    raise AssertionError

    def tearDown(self) -> None:
        rmtree(testDataDir)
