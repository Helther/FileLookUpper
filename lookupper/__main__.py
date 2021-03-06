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

from enum import Enum
from lookupper import processor
import argparse
import os.path

programName = "FilelookUpper"
programVersion = "0.8"

class TableColumns(Enum):
    Num = 0,
    Name = 1,
    Type = 2,
    Size = 3

class ColSizeVals(Enum):
    Num = 6
    Name = 100
    Type = 10
    Size = 15


DirTableColSizes = {TableColumns.Num: ("№", ColSizeVals.Num.value),
                    TableColumns.Name: ("Name", ColSizeVals.Name.value),
                    TableColumns.Size: ("Size", ColSizeVals.Size.value)}

FileTableColSizes = {TableColumns.Num: ("№", ColSizeVals.Num.value),
                     TableColumns.Name: ("Name", ColSizeVals.Name.value),
                     TableColumns.Type: ("Type", ColSizeVals.Type.value),
                     TableColumns.Size: ("Size", ColSizeVals.Size.value)}

global NameColSizeArg
MaxThreadCountArg = 20
MaxColumnSizeArg = 1 << 10

def elidePath(Path, extraSpace):
    result = ''
    currentSpace = 0
    availableSpace = len(Path) + extraSpace
    brokenPath = os.path.split(Path)
    currentSpace += len(brokenPath[1])
    # check if filename can't fit, else continue
    if availableSpace < currentSpace:
        result += brokenPath[1][currentSpace - availableSpace:]
        return result
    else:
        result = brokenPath[1]
    while brokenPath[1] != '':  # break path until it can't fit or fits whole
        brokenPath = os.path.split(brokenPath[0])
        currentSpace += len(brokenPath[1]) + len(os.path.sep)
        if availableSpace < currentSpace:  # check if can't fit
            result = "{}{}".format(os.path.sep, result)
            break
        else:
            result = "{}{}{}".format(brokenPath[1], os.path.sep, result)
    return result


def elideColumn(value, columnMaxSize, elideRight):
    continChar = '...'
    spareSpace = columnMaxSize - len(value) - 1  # space for text excluding ws
    if spareSpace < 0:
        if elideRight:
            elidedVal = value[:spareSpace - len(continChar)]
            return "| {}{} {}".format(elidedVal, continChar, ' ' *
                                   max(0, spareSpace))
        else:
            elidedVal = elidePath(value, spareSpace - len(continChar) -
                                  len(os.path.sep) - 1)
            newSpareSpace = columnMaxSize - len(elidedVal) - len(continChar) - 1
            return "| {}{} {}".format(continChar, elidedVal, ' ' *
                                      max(0, newSpareSpace))
    else:
        return "| {}{}".format(value, ' ' * (columnMaxSize - len(value)))


def displayTable(data, sizeScale, maxTableRowCount=100):
    """
    outputs to console processed list of data in table format
    format of the table:
    +---+------+------------+
    | № | Name | Size in {} |
    +---+------+------------+
    |   |      |            |
    +---+------+------------+
    :param data: list of tuples
    :param maxTableRowCount:
    :param sizeScale: enum val
    """
    global NameColSizeArg
    if len(data) == 0:
        print("No elements were found")
        return
    row = 0
    if len(data[row]) == len(DirTableColSizes) - 1:
        tableColumns = DirTableColSizes.copy()
    elif len(data[row]) == len(FileTableColSizes) - 1:
        tableColumns = FileTableColSizes.copy()
    else:
        print("wrong data dimensions")
        return
    # table title and separator and row separator
    print(f"\n{programName} v{programVersion} Results Table")
    tableColumnsSize = 0
    rowSeparatorStr = ""
    for k, nameSize in tableColumns.items():
        if nameSize[0] == DirTableColSizes[TableColumns.Name][0]:
            tableColumnsSize += len(nameSize[0]) + NameColSizeArg
            rowSeparatorStr += "+{}".format('-' * (NameColSizeArg + 1))
        else:
            tableColumnsSize += len(nameSize[0]) + nameSize[1]
            rowSeparatorStr += "+{}".format('-' * (nameSize[1] + 1))
    print('=' * tableColumnsSize)
    print(rowSeparatorStr + '+/')
    # headers
    headersStr = ""
    for k, nameSize in tableColumns.items():
        if nameSize[0] == DirTableColSizes[TableColumns.Size][0]:
            colSizeName = f"{DirTableColSizes[TableColumns.Size][0]} in " \
                          f"{processor.sizeScaleNames[sizeScale]}"
            headersStr += "| {}{}".format(colSizeName, ' ' * (nameSize[1] -
                                                              len(colSizeName)))
        elif nameSize[0] == DirTableColSizes[TableColumns.Name][0]:
            headersStr += "| {}{}".format(nameSize[0], ' ' * (NameColSizeArg -
                                                              len(nameSize[0])))
        else:
            headersStr += "| {}{}".format(nameSize[0], ' ' * (nameSize[1] -
                                                              len(nameSize[0])))
    print(headersStr + '|')

    # rows display
    tableSize = min(len(data), maxTableRowCount)
    col = 0
    while row < tableSize:
        rowStr = ""
        for k, nameSize in tableColumns.items():
            if nameSize[0] == DirTableColSizes[TableColumns.Num][0]:
                elidedRowNum = elideColumn(str(row + 1), nameSize[1], True)
                rowStr += elidedRowNum
                continue
            currentEntry = data[row][col]
            if nameSize[0] == DirTableColSizes[TableColumns.Name][0]:
                elidedRowName = elideColumn(currentEntry, NameColSizeArg, False)
                rowStr += elidedRowName
                col += 1
                continue
            elidedEntry = elideColumn(str(currentEntry), nameSize[1], True)
            rowStr += elidedEntry
            col += 1
        rowStr += '|'
        print(rowSeparatorStr + '+')  # top of the row
        print(rowStr)
        row += 1
        col = 0
    print(rowSeparatorStr + '+')  # bottom of the table


def parseArgs():
    """
    Handles argument parsing
    :return: map of user defined params, bool
    """
    global NameColSizeArg
    parser = argparse.ArgumentParser()
    parser.prog = "lookupper"
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
                             " argument with a certain scale "
                             "(in Mbytes by default). Zero by default")
    parser.add_argument("-n", "--nameFilter", action="store", type=str, nargs=1,
                        help="given argument, filter whether element name"
                             " contains it. Off by default")
    parser.add_argument("-r", "--rootDir", action="store", type=str, nargs='+',
                        help="specify root directory path. Working folder"
                             " by default")
    parser.add_argument("-e", "--elemMaxNumber", action="store", type=int,
                        nargs=1,
                        help="choose a max number of elements to display")
    parser.add_argument("-c", "--sizeScale", action="store", type=int, nargs=1,
                        choices=list(range(0, processor.sizeScales.MAX.value)),
                        help="choose how to scale elements sizes: 0 - Bytes, "
                             "1 - KBytes, 2 - MBytes, 3 - GBytes. Default is Mbytes")
    parser.add_argument("-u", "--threadCount", action="store", type=int, nargs=1,
                        help="specify the maximum number of working threads")
    parser.add_argument("-i", "--nameSize", action="store", type=int, nargs=1,
                         help="specify the width of element "
                                                    "name column in characters")
    args = parser.parse_args()
    reqs = processor.DefaultReqs.copy()
    isDir = False

    if args.directory:
        isDir = True
    if args.sortBy:
        if not(isDir and args.sortBy[0] == processor.SortByWhat.TYPE.value):
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
        root = ' '.join(args.rootDir)
        if not processor.ProcessorBase.isPathValid(root):
            parser.error(f" {root} is not valid path")
        reqs["rootDir"] = root
    if args.elemMaxNumber:
        if args.elemMaxNumber[0] <= 0:
            parser.error("not valid argument value: e > 0")
        reqs["maxElemNumber"] = args.elemMaxNumber[0]
    if args.sizeScale:
        reqs["sizeScale"] = args.sizeScale[0]
    if args.threadCount:
        if 1 > args.threadCount[0] or args.threadCount[0] < MaxThreadCountArg + 1:
            parser.error(f"not valid argument value 1 <= u <= {MaxThreadCountArg + 1}")
        reqs["maxThreadCount"] = args.threadCount[0]
    if args.nameSize:
        if len(DirTableColSizes[TableColumns.Name][0]) > args.nameSize[0] or \
                             args.nameSize[0] > MaxColumnSizeArg:
            parser.error(f"not valid argument value: "
                         f"{len(DirTableColSizes[TableColumns.Name][0])} <= i <= "
                         f"{MaxColumnSizeArg}")
        NameColSizeArg = args.nameSize[0]
    else:
        NameColSizeArg = ColSizeVals.Name.value
    return reqs, isDir


def main():
    reqs, isDir = parseArgs()
    if isDir:
        looker = processor.DirProc(reqs)
    else:
        looker = processor.FileProc(reqs)
    resultData = looker.process()
    if looker.interrupted:
        print("\nProcedure was manually cancelled")
    else:
        displayTable(resultData, reqs["sizeScale"],
                     maxTableRowCount=reqs["maxElemNumber"])


if __name__ == '__main__':
    main()
