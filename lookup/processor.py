from enum import Enum
import pathlib
import os.path
from threading import Thread
import time
import sys

# todo global
#  add scanned elems count update
#  add keybr interrupt handle
#  add GB scale option
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
        sys.stdout.write('\r')
        sys.stdout.write(ProgressBar.getProgressStr(0))
        sys.stdout.flush()

    def update(self):
        self.currentIndex += 1
        sys.stdout.write('\r')
        sys.stdout.write(self.getProgressStr(self.currentIndex / self.maxIndex))
        sys.stdout.flush()
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
        """
        thread target
        :param data: list ref
        :param rootDir: Path object
        :return: None
        """
        Sum = [0]
        try:
            self.dirScan(Sum, rootDir)
        except OSError as e:
            print(f"\nError: {sys.exc_info()[1]}\n"
                 "This element won't be included in the results")
            return
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
        data = []
        try:
            rootDirNames = [Dir for Dir in rootP.iterdir() if os.path.isdir(Dir)]
        except OSError as e:
            print(f"\nRoot directory error: {sys.exc_info()[1]}\n"
                    "Seach cancelled")
            return []
        threadPool = []
        start_time = time.time()
        index = 0
        progress = ProgressBar(len(rootDirNames))
        ProgressBar.init()
        while index < len(rootDirNames):
            if not self.applyFilter(Name=rootDirNames[index].name):
                continue
            for i in range(0, MAX_THREAD_COUNT):
                threadPool.append(Thread(name=f"thread_{i}",
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
        # todo: reformat this sorting and make custom predicats
        sortKey = int(self.reqs["sortBy"])
        reverseOrder = False
        if sortKey == SortByWhat.SIZE.value:  # todo ugly
            sortKey -= 1
            reverseOrder = True
        data.sort(key=lambda x: x[sortKey], reverse=reverseOrder)

        duration = time.time() - start_time
        print(f"\nFound {len(rootDirNames)} element[s] in {'%.3f'%duration} seconds")
        return data


class FileProc(ProcessorBase):
    def __init__(self, reqs=None):
        super(FileProc, self).__init__(reqs)

    def proccesFile(self, data, File):
        """
        Adds given file info to the glbal data
        :param data: list ref
        :param File: Path
        """
        try:
            fileName = str(File)
            fileExt = os.path.splitext(File.name)[1][1:]
            scaledSize = int(File.stat().st_size / \
                             int(sizeScalesVals[self.reqs["sizeScale"]]))
            if self.applyFilter(fileName, scaledSize, fileExt):
                data.append((fileName, fileExt, scaledSize))
        except OSError as e:
            print(f"\nError: {sys.exc_info()[1]}\n"
                "This element won't be included in the results")
            return

    def fileScanMT(self, data, rootDir):
        rootDirs = []
        threadPool = []
        index = 0
        progress = 0
        try:
            rDirlist = [x for x in rootDir.iterdir()]
        except OSError as e:
            print(f"\nRoot directory error: {sys.exc_info()[1]}\n"
                 "Seach cancelled")
            return data

        for rDir in rDirlist:
            if rDir.is_dir():
                rootDirs.append(rDir)
            else:
                self.proccesFile(data, rDir)

        progress = ProgressBar(len(rootDirs))
        ProgressBar.init()
        while index < len(rootDirs):
            for i in range(0, MAX_THREAD_COUNT):
                threadPool.append(Thread(name=f"thread_{i}",
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
        try:
            for file in Dir.iterdir():
                    if file.is_dir():
                        self.fileScan(data, Dir / file.name)
                    else:
                        self.proccesFile(data, file)
        except OSError as e:
            print(f"\nError: {sys.exc_info()[1]}\n"
                 "All elements and it's sub elements won't "
                  "be included in the results")
            return

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
        if data:
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
            
            duration = time.time() - start_time
            print(f"\nFound {len(data)} element[s] in {'%.3f'%duration} seconds")
        return data
