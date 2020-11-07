from enum import Enum
import pathlib
import os.path
import threading
import time
from sys import stdout

# todo global
#  fix elide path
#  add thread excepts handling
#  remove recursivness
#  use sorted container for data without additional sort
#  add test decriptions

MAX_THREAD_COUNT = 8


class SortByWhat(Enum):
    NAME = 0
    TYPE = 1
    SIZE = 2
    MAX = 3


class sizeScales(Enum):
    B = 0
    KB = 1
    MB = 2
    MAX = 3


sizeScalesVals = {sizeScales.B.value: 1,
                  sizeScales.KB.value: 1024,
                  sizeScales.MB.value: 1024 << 10}


sizeScaleNames = {sizeScales.B.value: "Bytes",
                  sizeScales.KB.value: "KBytes",
                  sizeScales.MB.value: "MBytes"}

# table of arguments default values
DefaultReqs = {"sortBy": SortByWhat.SIZE.value,
               "minSize": -1,
               "sizeScale": sizeScales.MB.value,
               "nameFilter": "",
               "typeFilter": "",
               "rootDir": '.',
               "maxElemNumber": 100}


class ProgressBar(object):
    """
    class for displaying udpating progress bar
    """
    def __init__(self, maxIndex):
        self.maxIndex = maxIndex
        self.currentIndex = 0

    @staticmethod
    def init():
        stdout.write('\r')
        stdout.write(ProgressBar.getProgressStr(0))
        stdout.flush()

    def update(self):
        self.currentIndex += 1
        stdout.write('\r')
        stdout.write(self.getProgressStr(self.currentIndex / self.maxIndex))
        stdout.flush()
        time.sleep(0.1)

    @staticmethod
    def getProgressStr(index):
        return "Progress: [%-30s] %d%%" % ('=' * int(30 * index), 100 * index)


class ProcessorBase(object):
    def __init__(self, reqs=None):
        self.reqs = DefaultReqs.copy() if reqs is None else reqs

    def process(self):
        pass

    def applyFilter(self, Name=DefaultReqs["nameFilter"],
                    Size=DefaultReqs["minSize"],
                    Type=DefaultReqs["typeFilter"]):
        """
        checks if elem passes the filter in reqs, if argument is defaulted
        then skips check
        :param Name string
        :param Type string
        :param Size int
        :return: bool
        """
        if self.reqs["nameFilter"] != DefaultReqs["nameFilter"] and \
                self.reqs["nameFilter"] not in Name:
            return False
        if self.reqs["typeFilter"] != DefaultReqs["typeFilter"] and \
                self.reqs["typeFilter"] not in Type:
            return False
        if self.reqs["minSize"] != DefaultReqs["minSize"] and \
                Size < self.reqs["minSize"]:
            return False
        return True

    @staticmethod
    def isPathValid(Path):
        return os.path.exists(Path) and os.path.isdir(Path)


class DirProc(ProcessorBase):
    def __init__(self, reqs=None):
        super(DirProc, self).__init__(reqs)

    def dirScan(self, Sum, Dir):
        """
        goes through all elements in a given Directory
        and adds sums of all files in them
        :param Sum: list of ints ref
        :param Dir: Path object
        :return: None
        """
        for file in Dir.iterdir():
            if file.is_dir():
                self.dirScan(Sum, Dir / file.name)
            else:
                Sum[0] += file.stat().st_size

    def dirScanMT(self, data, rootDir):
        Sum = [0]
        self.dirScan(Sum, rootDir)
        scaledSize = int(Sum[0] / sizeScalesVals[self.reqs["sizeScale"]])
        if self.applyFilter(Size=scaledSize):
            data.append((str(rootDir), scaledSize))

    def process(self):
        """
        recursivly looks through sub files in a list of root Dir
        and returns a list of Dirs names and it's sizes,
        apllying filter, then sorts the resulting list
        :return data: list<string,int>
        """
        rootP = pathlib.Path(self.reqs["rootDir"])
        rootDirNames = []
        for Dir in rootP.iterdir():
            if Dir.is_dir():
                rootDirNames.append(Dir)
        data = []
        threadPool = []
        start_time = time.time()
        index = 0
        progress = ProgressBar(len(rootDirNames))
        ProgressBar.init()
        while index < len(rootDirNames):
            if not self.applyFilter(Name=rootDirNames[index].name):
                continue
            for i in range(0, MAX_THREAD_COUNT):
                threadPool.append(threading.Thread(name=f"thread_{i}",
                    target=self.dirScanMT, args=(data, rootDirNames[index])))
                index += 1
                if index >= len(rootDirNames) - 1:
                    break
            for thread in threadPool:
                thread.start()
            for thread in threadPool:
                thread.join()
                progress.update()
            threadPool.clear()
        duration = time.time() - start_time
        print(f"\nScanned {len(rootDirNames)} elements in {duration} seconds")
        # todo: reformat this sorting and make custom predicats
        sortKey = int(self.reqs["sortBy"])
        reverseOrder = False
        if sortKey == SortByWhat.SIZE.value:  # todo ugly
            sortKey -= 1
            reverseOrder = True
        data.sort(key=lambda x: x[sortKey], reverse=reverseOrder)
        return data


class FileProc(ProcessorBase):
    def __init__(self, reqs=None):
        super(FileProc, self).__init__(reqs)

    def fileScanMT(self, data, rootDir):
        rootDirs = []
        threadPool = []
        index = 0
        progress = 0
        for rDir in rootDir.iterdir():
            if rDir.is_dir():
                rootDirs.append(rDir)
            else:
                fileName = str(rDir)
                fileExt = os.path.splitext(rDir.name)[1][1:]
                scaledSize = int(rDir.stat().st_size / \
                                 int(sizeScalesVals[self.reqs["sizeScale"]]))
                if self.applyFilter(fileName, scaledSize, fileExt):
                    data.append((fileName, fileExt, scaledSize))
            progress = ProgressBar(len(rootDirs))
            ProgressBar.init()
        while index < len(rootDirs):
            for i in range(0, MAX_THREAD_COUNT):
                threadPool.append(threading.Thread(name=f"thread_{i}",
                    target=self.fileScan, args=(data, rootDirs[index])))
                index += 1
                if index >= len(rootDirs) - 1:
                    break
            for thread in threadPool:
                thread.start()
            for thread in threadPool:
                thread.join()
                progress.update()
            threadPool.clear()

    def fileScan(self, data, Dir):
        """
        goes through all elements in a given Directory
        and adds them to a return list after applying filter
        :param data: list<string,string,int>
        :param Dir: Path object
        :return: None
        """
        for file in Dir.iterdir():
            if file.is_dir():
                self.fileScan(data, Dir / file.name)
            else:
                fileName = str(file)
                fileExt = os.path.splitext(file.name)[1][1:]
                scaledSize = int(file.stat().st_size / \
                             int(sizeScalesVals[self.reqs["sizeScale"]]))
                if self.applyFilter(fileName, scaledSize, fileExt):
                    data.append((fileName, fileExt, scaledSize))

    def process(self):
        """
        recursivly looks through sub files in a root Dir
        and returns a list of files, then sorts the resulting list
        :return data: list<string,string,int>
        """
        data = []
        rootP = pathlib.Path(self.reqs["rootDir"])
        start_time = time.time()
        self.fileScanMT(data, rootP)
        duration = time.time() - start_time
        print(f"\nScanned {len(data)} elements in {duration} seconds")
        sortKey = int(self.reqs["sortBy"])
        reverseOrder = False
        if sortKey == SortByWhat.SIZE.value:  # todo ugly
            reverseOrder = True
        if sortKey == SortByWhat.NAME.value:
            data.sort(key=lambda x: pathlib.Path(os.path.splitext(
                pathlib.Path(x[sortKey]).name)[0]),
                reverse=reverseOrder)
        else:
            data.sort(key=lambda x: x[sortKey], reverse=reverseOrder)
        return data
