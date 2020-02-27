from Source import processor
import sys, getopt
##############################################
#todo global
"""
finish args parse
get script run properly
#add repo stcruct( license and readme)
make public
add tests"""
##########################

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
    #todo some docs
    #todo replace getopt with argparse
    shortArgs = "hds:m:n:t:r:"
    longArgs = ["help","directory","sortBy","minSize","nameFilter","typeFilter","rootDir"]
    helpInfo = """"""
    try:
        options, args = getopt.getopt(sys.argv[1:],shortArgs,[longArgs])
    except getopt.GetoptError as err:
        print(str(err))
        print(helpInfo)
        sys.exit(1)
    isDir = False
    reqs = {}
    for opt,arg in options:
        if opt in ("-h","--help"):
            #TODO add help
            print(helpInfo)
            sys.exit()
        if opt in ("-d","--directory"):
            isDir = True
        if opt in ("-s","--sortBy"):
            reqs["sortByName"] = arg
            ##TODO add assert
        else:
            reqs["sortByName"] = processor.DefaultReqs["sortByName"]
        if opt in ("-m","--minSize"):
            reqs["minSize"] = arg
        else:
            reqs["minSize"] = processor.DefaultReqs["minSize"]
        if opt in ("-n","--nameFilter"):
            reqs["nameFilter"] = arg
        else:
            reqs["nameFilter"] = processor.DefaultReqs["nameFilter"]
        if opt in ("-t","--typeFilter"):
            reqs["typeFilter"] = arg
        else:
            reqs["typeFilter"] = processor.DefaultReqs["typeFilter"]
        if opt in ("r","--rootDir"):
            reqs["rootDir"] = arg
        else:
            reqs["rootDir"] = processor.DefaultReqs["rootDir"]
    return reqs,isDir
# todo check path validity

def testMenu():
    testIsDir = True
    defP = False
    testReqs = {"sortBy" : processor.SortByWhat.NAME,
				"minSize" :  0,
				"nameFilter" : "",
				"typeFilter" : "",
                "rootDir" : "."}
    if testIsDir:
        processorTest = processor.DirProc(testReqs)
        if defP:
            defProcessor =  processorTest.DirProc(None)
    else:
        processorTest = processor.FileProc(testReqs)
        if defP:
            defProcessor = processorTest.FileProc(None)
    resultData = processorTest.process()
    displayTable(resultData)
    if defP:
        resultData = defProcessor.process()
        displayTable(resultData)


def main(Argv):
    testMenu()

#######main
if __name__ == '__main__':
    main(sys.argv)
