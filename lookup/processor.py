from enum import Enum
import pathlib
import os.path
from threading import Thread
import time
import sys

# todo global
#  use distutils in setup to creat proper script
#  add changeLog file and redo readme
#  add cython compiled version
#  add bash and shell launch scripts


MAX_THREAD_COUNT = 8


class SortByWhat(Enum):
    NAME = 0
    TYPE = 1
    SIZE = 2
    MAX = 3

sortNames = {SortByWhat.NAME.value: "Name",
             SortByWhat.TYPE.value: "Type",
             SortByWhat.SIZE.value: "Size"}


class sizeScales(Enum):
    B = 0
    KB = 1
    MB = 2
    GB = 3
    MAX = 4


sizeScalesVals = {sizeScales.B.value: 1,
                  sizeScales.KB.value: 1024,
                  sizeScales.MB.value: 1024 << 10,
                  sizeScales.GB.value: 1024 << 20}


sizeScaleNames = {sizeScales.B.value: "Bytes",
                  sizeScales.KB.value: "KBytes",
                  sizeScales.MB.value: "MBytes",
                  sizeScales.GB.value: "GBytes"}

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
    def __init__(self):
        self.maxIndex = 0
        self.currentIndex = 0
        self.currentProgress = ''
        self.processedElemCount = 0

    def init(self, maxIndex):
        self.maxIndex = maxIndex
        self.currentProgress = ProgressBar.getProgressStr(0)
        self.printCurrentProgress()

    def updateProgressBar(self):
        self.currentIndex += 1
        self.currentProgress = self.getProgressStr(self.currentIndex / self.maxIndex)
        self.printCurrentProgress()
        sys.stdout.write(self.getCurrentElemCountStr())
        sys.stdout.flush()
        time.sleep(0.1)

    def updateProcessedElems(self):
        self.processedElemCount += 1
        updatePeriod = 100
        if self.processedElemCount % updatePeriod == 0:
            self.printCurrentProgress()
            sys.stdout.write(self.getCurrentElemCountStr())
            sys.stdout.flush()

    def printCurrentProgress(self):
        sys.stdout.write('\r')
        sys.stdout.write(self.currentProgress)


    def getCurrentElemCountStr(self):
        return f" | Elements processed total: {self.processedElemCount}"

    @staticmethod
    def getProgressStr(index):
        return "Progress: [%-30s] %d%%" % ('=' * int(30 * index), 100 * index)


class ProcessorBase(object):
    def __init__(self, reqs=None):
        self.reqs = DefaultReqs.copy() if reqs is None else reqs
        self.interrupted = False
        self.progress = ProgressBar()

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
        if Name != DefaultReqs["nameFilter"] and \
                self.reqs["nameFilter"] != DefaultReqs["nameFilter"] and \
                self.reqs["nameFilter"] not in Name:
            return False
        if self.reqs["typeFilter"] != DefaultReqs["typeFilter"] and \
                self.reqs["typeFilter"] not in Type:
            return False
        if Size != DefaultReqs["minSize"] and \
                self.reqs["minSize"] != DefaultReqs["minSize"] and \
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
            if self.interrupted:
                return
            if file.is_dir():
                self.dirScan(Sum, Dir / file.name)
            else:
                Sum[0] += file.stat().st_size
                self.progress.updateProcessedElems()

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
        except BaseException as e:
            if type(e) == OSError:
                print(f"\nError: {sys.exc_info()[1]}\n"
                    "This element won't be included in the results")
            if type(e) == KeyboardInterrupt:
                self.interrupted = True
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
        self.progress.init(len(rootDirNames))
        while index < len(rootDirNames):
            if not self.applyFilter(Name=rootDirNames[index].name):
                index += 1
                self.progress.updateProgressBar()
                continue
            threadCount = 0
            while threadCount < MAX_THREAD_COUNT:
                if self.applyFilter(Name=rootDirNames[index].name):
                    threadPool.append(Thread(name=f"thread_{threadCount}",
                        target=self.dirScanMT, args=(data, rootDirNames[index])))
                    threadCount += 1
                else:
                    self.progress.updateProgressBar()
                index += 1
                if index >= len(rootDirNames) - 1:
                    break
            if self.interrupted:  # cancel if keybr interrupted
                return []
            for thread in threadPool:
                thread.start()
            try:
                for thread in threadPool:
                    thread.join()
                    self.progress.updateProgressBar()
            except KeyboardInterrupt as e:
                self.interrupted = True
                return
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
        except BaseException as e:
            if type(e) == OSError:
                print(f"\nError: {sys.exc_info()[1]}\n"
                      "This element won't be included in the results")
            if type(e) == KeyboardInterrupt:
                self.interrupted = True
            return

    def fileScanMT(self, data, rootDir):
        rootDirs = []
        threadPool = []
        index = 0
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
                self.progress.updateProcessedElems()

        self.progress.init(len(rootDirs))
        while index < len(rootDirs):
            for i in range(0, MAX_THREAD_COUNT):
                threadPool.append(Thread(name=f"thread_{i}",
                    target=self.fileScan, args=(data, rootDirs[index])))
                index += 1
                if index >= len(rootDirs) - 1:
                    break
            if self.interrupted:  # cancel if keybr interrupted
                break
            for thread in threadPool:
                thread.start()
            try:
                for thread in threadPool:
                    thread.join()
                    self.progress.updateProgressBar()
            except KeyboardInterrupt as e:
                self.interrupted = True
                return
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
                if self.interrupted:
                    return
                if file.is_dir():
                    self.fileScan(data, Dir / file.name)
                else:
                    self.proccesFile(data, file)
                    self.progress.updateProcessedElems()
        except BaseException as e:
            if type(e) == OSError:
                print(f"\nError: {sys.exc_info()[1]}\n"
                      "All elements and it's sub elements won't "
                      "be included in the results")
            if type(e) == KeyboardInterrupt:
                self.interrupted = True
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
        if self.interrupted:  # cancel if keybr interrupted
            return []
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
