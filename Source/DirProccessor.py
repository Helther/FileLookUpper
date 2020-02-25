from enum import Enum
from pathlib import Path
import os.path
class SortByWhat(Enum):
	NAME = 0
	TYPE = 1
	SIZE = 2

DefaultReqs = 	{"sortBy" : SortByWhat.SIZE,
				"minSize" :  0,
				"nameFilter" : "",
				"typeFilter" : "",
                "rootDir" : '.'}

class ProcessorBase(object):
    def __init__(self,reqs = None):
        self.reqs = DefaultReqs if reqs is None else reqs

    separator = '\\'

    def process(self): pass

    def applyFilter(self,name,size, typo = DefaultReqs["typeFilter"]):
        """
        checks if elem passes the filter on reqs
        :param name string
        :param typo string
        :param size int
        :return: bool
        """
        if name != DefaultReqs["nameFilter"] and self.reqs["nameFilter"] not in name:
            return False
        if typo != DefaultReqs["typeFilter"] and self.reqs["typeFilter"] not in typo:
            return False
        if size < self.reqs["minSize"]:
            return False
        return True
        #todo test
        
    def Sort(self,elems):
        """
        sorts final list of elemts accoring to reqs
        :param elems: list of file or dirs info
        :return: sorted list
        """
        ##sorting by elem of tuple with index = enum.value
        elems.sort(key= lambda x:x[self.reqs["sortBy"].value])
        return elems

class DirProc(ProcessorBase):
    def __init__(self, reqs):
        super(DirProc,self).__init__(reqs)

    def dirScan(self,Sum,Dir):
        #todo add docs
        for file in Dir.iterdir():
            if file.is_dir():
                self.dirScan(Sum,Dir / file.name)
            else:
                Sum[0]+=file.stat().st_size
                
    def process(self):
        """
            проход черех все элементы в рут
            лист все диры(для рут применить nameFilter)
            проход по дирам
            если файл то сумм размера для данного дира
            иначе добавить сумм для дира и рекурс со 2 строчки
            когда прошел по всем рут дирам, сорт по sortBy(если ==1, то =0)
            вывод листа имен, размеров рут диров
        """
        rootP = Path(self.reqs["rootDir"])
        rootDirNames = []
        for dir in rootP.iterdir():
            if dir.is_dir():
                rootDirNames.append(rootP / dir)
        data = []
        for rootDir in rootDirNames:
            Sum = [0]
            self.dirScan(Sum,rootDir)
            data.append((rootDir,Sum[0]))
         
        self.Sort(data)
        return data

class FileProc(ProcessorBase):
    def __init__(self,reqs):
        super(FileProc,self).__init__(reqs)

    def fileScan(self,data,Dir):
        #todo add docs
        for file in Dir.iterdir():
            if file.is_dir():
                self.fileScan(data,Dir / file.name)
            else:
                fileName = os.path.splitext(file.name)[0]
                fileExt = os.path.splitext(file.name)[1]
                if self.applyFilter(fileName,file.stat().st_size,fileExt):
                    data.append((fileName,fileExt,file.stat().st_size))
                    
    def process(self):
        """
            проход черех все элементы в рут
            лист все диры
            добавить в вывод файлы(имя,тип,размер) с учетом фильтров
            проход по дирам
            добавить в вывод файлы(имя,тип,размер) с учетом фильтров
            рекурс с 4 строки по рут дирам
            когда прошел по всем рут дирам, сорт вывод по sortBy(если ==1, то =0)
            вывод листа имен,типов, размеров списка вывода
        """
        data = []
        rootP = Path(self.reqs["rootDir"])
        self.fileScan(data,rootP)
        

        # p = Path("D:\Dev\Py\FileLookUpper\\venv\Scripts\python.exe")
        # print(p.is_dir(), p.stat().st_size)
        #data_folder = Path("source_data/text_files/")
        #file_to_open = data_folder / "raw_data.txt"

        self.Sort(data)
        return data
