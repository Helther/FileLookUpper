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

    def applyFilter(self,name,typo,size):
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

    def Sort(self,elems):
        """
        sorts final list of elemts accoring to reqs
        :param elems: list of file or dirs info
        :return: sorted list
        """
        ##sorting by elem of tuple with index = enum
        elems.sort(key= lambda x:x[self.reqs["sortBy"]])
        return elems

class DirProc(ProcessorBase):
    def __init__(self, reqs):
        super(DirProc,self).__init__(reqs)

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
        data = []
        # data.append((name,size))
        return data

class FileProc(ProcessorBase):
    def __init__(self,reqs):
        super(FileProc,self).__init__(reqs)

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
        rootDirs = []
        for file in rootP.iterdir():
            if file.is_dir():
                rootDirs.append(file.name)
            else:
                fileName = os.path.splitext(file.name)[0]
                fileExt = os.path.splitext(file.name)[1]
                if self.applyFilter(fileName,fileExt,file.stat().st_size):
                    data.append([fileName,fileExt,file.stat().st_size])
        print(data)
        print(rootDirs)
        # p = Path("D:\Dev\Py\FileLookUpper\\venv\Scripts\python.exe")
        # print(p.is_dir(), p.stat().st_size)
        #data_folder = Path("source_data/text_files/")
        #file_to_open = data_folder / "raw_data.txt"

        #self.Sort(data)
        return data