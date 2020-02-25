import DirProccessor
import sys, getopt


def displayTable(data, maxColLength=10,maxTableSize=500):
    """
    outputs to console processed list of data in table format
    :param maxColLength:
    :param data: list of tuples
    :param maxTableSize:
    """
    tableSize = min(len(data),maxTableSize)
    row = 0
    while row < tableSize:
        print('\n',row + 1, " ",end=' ')
        for col in data[row]:
            Str = str(col)[0:maxColLength]
            print(Str,' '*(maxColLength-len(Str)),end=' ')
        row+=1
    #todo add column names
    #todo add continuation if string longer than max

def parseArgs():
    longArgs = ["help","directory","sortBy","minSize","nameFilter","typeFilter","rootDir"]
    try:
        options, args = getopt.getopt(sys.argv[1:],"hds:m:n:t:r:",[longArgs])
    except getopt.GetoptError:
        print("arg error placeholder for proper usage")
        sys.exit(1)
    isDir = False
    reqs = {}
    for opt,arg in options:
        if opt in ("-h","--help"):
            #TODO add help
            print("There will be usage help")
        if opt in ("-d","--directory"):
            isDir = True
        if opt in ("-s","--sortBy"):
            reqs["sortByName"] = arg
            ##TODO add assert
        else:
            reqs["sortByName"] = DirProccessor.DefaultReqs["sortByName"]
        if opt in ("-m","--minSize"):
            reqs["minSize"] = arg
        else:
            reqs["minSize"] = DirProccessor.DefaultReqs["minSize"]
        if opt in ("-n","--nameFilter"):
            reqs["nameFilter"] = arg
        else:
            reqs["nameFilter"] = DirProccessor.DefaultReqs["nameFilter"]
        if opt in ("-t","--typeFilter"):
            reqs["typeFilter"] = arg
        else:
            reqs["typeFilter"] = DirProccessor.DefaultReqs["typeFilter"]
        if opt in ("r","--rootDir"):
            reqs["rootDir"] = arg
        else:
            reqs["rootDir"] = DirProccessor.DefaultReqs["rootDir"]
    return reqs,isDir
def main():pass
# todo check path validity

def testMenu():
    testIsDir = True
    defP = False
    testReqs = {"sortBy" : DirProccessor.SortByWhat.NAME,
				"minSize" :  0,
				"nameFilter" : "",
				"typeFilter" : "",
                "rootDir" : "."}
    if testIsDir:
        processor = DirProccessor.DirProc(testReqs)
        if defP:
            defProcessor =  DirProccessor.DirProc(None)
    else:
        processor = DirProccessor.FileProc(testReqs)
        if defP:
            defProcessor = DirProccessor.FileProc(None)
    resultData = processor.process()
    displayTable(resultData)
    if defP:
        resultData = defProcessor.process()
        displayTable(resultData)

#######main
testMenu()
#if __name__ == '__main__':
#main(sys.argv)
