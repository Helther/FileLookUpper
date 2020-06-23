#!/usr/bin/env python
################
#   Copyright [2020] [Anton]
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

from lookup import processor
import argparse


def displayTable(data, maxColLength=60, maxTableSize=100):
    """
    outputs to console processed list of data in table format
    :param maxColLength:
    :param data: list of tuples
    :param maxTableSize:
    """
    if len(data) == 0:
        print("No elements were found")
        return
    continChar = '...'
    tableSize = min(len(data), maxTableSize)
    row = 0
    fileColumnNumber = 3
    dirColumnNumber = 2
    colNameNum = "№"
    colNameName = "Name"
    colNameType = "Type"
    colNameSize = "Size in Mbytes"
    if len(data[row]) == dirColumnNumber:
        print('\n', colNameNum, ' ' * (len(str(maxTableSize)) -
              len(colNameNum) - 1), colNameName, ' ' * (maxColLength -
              len(colNameName) + 2), colNameSize, end='')
    if len(data[row]) == fileColumnNumber:
        print('\n', colNameNum, ' ' * (len(str(maxTableSize)) -
              len(colNameNum) - 1), colNameName, ' ' * (maxColLength -
              len(colNameName) + 2), colNameType, ' ' * (maxColLength
              - len(colNameType) + 2), colNameSize, end='')
    while row < tableSize:
        print('\n', row + 1, ' ' * (len(str(maxTableSize)) -
                                    len(str(row+1))), end='')
        isName = True
        for col in range(0, len(data[row])):
            spareSpace = maxColLength - len(str(data[row][col]))
            if col == len(data[row]) - 1:
                Str = str(int(data[row][col] / (10 ** 6)))
            else:
                Str = str(data[row][col])[-maxColLength:]
            if isName and spareSpace < 0:
                print("{}{} {}".format(continChar, Str, ' ' *
                                       max(0, spareSpace)), end='')
            else:
                print("{} {}".format(Str, ' ' * (max(0, spareSpace) +
                                                 len(continChar))), end='')
            isName = False
        row += 1
    # todo expand path by hiding parent folders as "../"
    #  from a certain depth(length)
    # todo way to set col size scale


def parseArgs():
    """
    Handles argument parsing
    :return: map of user defined params, bool
    """
    parser = argparse.ArgumentParser()
    parser.prog = "lookup"
    exclusiveGroup = parser.add_mutually_exclusive_group()
    exclusiveGroup.add_argument("-d", "--directory", action="store_true",
                                help="process directories instead of files")
    exclusiveGroup.add_argument("-t", "--typeFilter", action="store", type=str,
                                nargs=1, help="given argument, filter whether "
                                "element type contains it. Off by default")
    parser.add_argument("-s", "--sortBy", action="store", type=int, nargs=1,
                        choices=list(range(0, processor.SortByWhat.MAX.value)),
                        help="choose with which key to sort:"
                             " 0 - NAME, 1 - TYPE, 2 - SIZE. Default by size")
    parser.add_argument("-m", "--minSize", action="store", type=int, nargs=1,
                        help="filter elements with size less than given"
                             " argument (in bytes). Zero by default")
    parser.add_argument("-n", "--nameFilter", action="store", type=str, nargs=1,
                        help="given argument, filter whether element name"
                             " contains it. Off by default")

    parser.add_argument("-r", "--rootDir", action="store", type=str, nargs=1,
                        help="specify root directory path. Working folder"
                             " by default")
    parser.add_argument("-e", "--elemMaxNumber", action="store", type=int,
                        nargs=1,
                        help="choose a max number of elements to display")
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
    if args.elemMaxNumber:
        if args.elemMaxNumber[0] <= 0:
            parser.error("not valid argument value: e > 0")
        reqs["maxElemNumber"] = args.elemMaxNumber[0]
    return reqs, isDir


def main():
    reqs, isDir = parseArgs()
    if isDir:
        looker = processor.DirProc(reqs)
    else:
        looker = processor.FileProc(reqs)
    resultData = looker.process()
    displayTable(resultData, maxTableSize=reqs["maxElemNumber"])


if __name__ == '__main__':
    main()
