#!/usr/bin/env python
################
#Copyright [2020] [Anton]
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
################

from  lookup import processor
import sys
import argparse

##############################################
#todo global
"""
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
    continChar = '...'
    tableSize = min(len(data),maxTableSize)
    row = 0
    while row < tableSize:
        print('\n',row + 1, ' '*(len(str(maxTableSize))-len(str(row+1))),end='')
        for col in data[row]:
            isName = True
            spareSpace = maxColLength - len(str(col))
            Str = str(col)[0:maxColLength]
            if isName and spareSpace < 0:
                print("{}{} {}".format(Str, continChar, ' ' * max(0, spareSpace)), end='')
            else:
                print("{} {}".format(Str, ' ' * (max(0, spareSpace) + len(continChar))), end='')
            isName = False
        row+=1
    #todo add column names
    #todo expand path

def parseArgs():
    """
    Handles argument parsing
    :return: map of user defined params, bool
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d","--directory", action="store_true",help="process directories instead of files")
    parser.add_argument("-s", "--sortBy", action="store",type=int,nargs=1,
                        choices=list(range(0,processor.SortByWhat.MAX.value)),
                        help="choose with which key to sort: 0 - NAME, 1 - TYPE, 2- SIZE. Default by size")
    parser.add_argument("-m", "--minSize", action="store",type=int,nargs=1,
                        help="filter elements with size less than given argument. Zero by default")
    parser.add_argument("-n", "--nameFilter", action="store",type=str,nargs=1,
                        help="given argument, filter whether element name contains it. Off by default")
    parser.add_argument("-t", "--typeFilter", action="store",type=str,nargs=1,
                        help="given argument, filter whether element type contains it. Off by default")
    parser.add_argument("-r", "--rootDir", action="store",type=str,nargs=1,
                        help="specify root directory path. Working folder by default")
    args = parser.parse_args()
    reqs = processor.DefaultReqs
    isDir = False

    if args.directory:
        isDir = True
    if args.sortBy:
        reqs["sortBy"] = args.sortBy[0]
    if args.minSize:
        if not args.minSize[0] > 0:
            parser.error('Minimum size supposed to be more than zero')
        reqs["minSize"] = args.minSize[0]
    if args.nameFilter:
        reqs["nameFilter"] = args.nameFilter[0]
    if args.typeFilter:
        reqs["typeFilter"] = args.typeFilter[0]
    if args.rootDir:
        root = args.rootDir[0]
        if not processor.ProcessorBase.isPathValid(root):
            parser.error(f" {root} is not valid path")
        reqs["rootDir"] = root

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
    reqs,isDir = parseArgs()

    looker = processor.FileProc(reqs)
    if isDir:
        looker = processor.DirProc(reqs)
    resultData = looker.process()
    displayTable(resultData)
    #testMenu()

#######main
if __name__ == '__main__':
    main(sys.argv)