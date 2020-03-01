from Source import processor
import sys
import argparse

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
    #todo add help
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--directory", action="store_true",help="process directories instead of files")
    parser.add_argument("-s", "--sortBy", action="store",type=int,nargs=1,
                        choices=list(range(0,processor.SortByWhat.MAX.value)),help="")
    parser.add_argument("-m", "--minSize", action="store",type=int,nargs=1,
                        help="")
    parser.add_argument("-n", "--nameFilter", action="store",type=str,nargs=1,
                        help="")
    parser.add_argument("-t", "--typeFilter", action="store",type=str,nargs=1,
                        help="")
    parser.add_argument("-r", "--rootDir", action="store",type=str,nargs=1,
                        help="")
    args = parser.parse_args()
    reqs = processor.DefaultReqs
    isDir = False

    if args.directory:
        isDir = True
    if args.sortBy:
        reqs["sortBy"] = args.sortBy[0]
    if args.minSize:
        reqs["minSize"] = args.minSize[0]
        #parser.error("oops")
        #todo add value check
    if args.nameFilter:
        reqs["nameFilter"] = args.nameFilter[0]
    if args.typeFilter:
        reqs["typeFilter"] = args.typeFilter[0]
    if args.rootDir:
        reqs["rootDir"] = args.rootDir[0]
        # todo check path validity

    return reqs,isDir

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
    parseArgs()
    testMenu()

#######main
if __name__ == '__main__':
    main(sys.argv)
