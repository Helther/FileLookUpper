from enum import Enum
import pathlib
import os.path


class SortByWhat(Enum):
    NAME = 0
    TYPE = 1
    SIZE = 2
    MAX = 3


# table of arguments default values
DefaultReqs = {"sortBy": SortByWhat.SIZE.value,
               "minSize": 0,
               "nameFilter": "",
               "typeFilter": "",
               "rootDir": '.',
               "maxElemNumber": 100}


class ProcessorBase(object):
    def __init__(self, reqs=None):
        self.reqs = DefaultReqs if reqs is None else reqs

    def process(self):
        pass

    def applyFilter(self, Name=DefaultReqs["nameFilter"],
                    Size=DefaultReqs["minSize"],
                    Type=DefaultReqs["typeFilter"]):
        """
        checks if elem passes the filter in reqs
        :param Name string
        :param Type string
        :param Size int
        :return: bool
        """
        if Name != DefaultReqs["nameFilter"] and self.reqs["nameFilter"] \
                not in Name:
            return False
        if Type != DefaultReqs["typeFilter"] and self.reqs["typeFilter"] \
                not in Type:
            return False
        if Size < self.reqs["minSize"]:
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

    def process(self):
        """
        recursivly looks through sub files in a list of root Dir
        and returns a list of Dirs names and it's sizes,
        apllying filter, then sorts the resulting list
        :return data: list<string,int>
        """
        rootP = pathlib.Path(self.reqs["rootDir"])
        rootDirNames = []
        rootDirNum = 0
        for Dir in rootP.iterdir():

            if Dir.is_dir():
                rootDirNames.append(Dir)
                rootDirNum += 1
                if rootDirNum >= self.reqs["maxElemNumber"]:
                    break
        data = []
        for rootDir in rootDirNames:
            if not self.applyFilter(Name=rootDir.name):
                continue
            Sum = [0]
            self.dirScan(Sum, rootDir)
            if self.applyFilter(Size=Sum[0]):
                data.append((str(rootDir), Sum[0]))
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
        self.currentElemNumber = 0

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
                fileName = os.path.splitext(file.name)[0]
                fileExt = os.path.splitext(file.name)[1][1:]
                if self.applyFilter(fileName, file.stat().st_size, fileExt):
                    if self.currentElemNumber >= self.reqs["maxElemNumber"]:
                        break
                    data.append((fileName, fileExt, file.stat().st_size))
                    self.currentElemNumber += 1

    def process(self):
        """
        recursivly looks through sub files in a root Dir
        and returns a list of files, then sorts the resulting list
        :return data: list<string,string,int>
        """
        data = []
        rootP = pathlib.Path(self.reqs["rootDir"])
        self.fileScan(data, rootP)

        sortKey = int(self.reqs["sortBy"])
        reverseOrder = False
        if sortKey == SortByWhat.SIZE.value:  # todo ugly
            reverseOrder = True
        data.sort(key=lambda x: x[sortKey], reverse=reverseOrder)
        return data
