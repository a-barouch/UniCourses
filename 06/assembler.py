import sys
import os

NOT_FOUND = -1

compDict = {'0': '0101010', '1': '0111111', '-1': '0111010', 'D': '0001100',
'A': '0110000', '!D': '0001101', '!A': '0110001', '-D': '0001111',
'-A': '0110011', 'D+1': '0011111', 'A+1': '0110111', 'D-1': '0001110',
'A-1': '0110010', 'D+A': '0000010', 'D-A': '0010011', 'A-D': '0000111',
'D&A': '0000000', 'D|A': '0010101', 'M': '1110000', '!M': '1110001',
'-M': '1110011', 'M+1': '1110111', 'M-1': '1110010', 'D+M': '1000010',
'D-M': '1010011', 'M-D': '1000111', 'D&M': '1000000', 'D|M': '1010101'}
destDict = {'':'000', 'M':'001','D':'010','MD':'011','A':'100','AM':'101',
'AD':'110','AMD':'111'}
jumpDict = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100',
'JNE': '101', 'JLE': '110', 'JMP': '111'}
shiftDect = {'D<<':'101011', 'A<<':'101010', 'M<<': '101110', 'D>>':'101001',
            'A>>':'101000','M>>':'101100'}


def createSymbolTable():
    symbolTable = {"SCREEN":16384,
                   "KBD":24576,
                   "SP":0,
                   "LCL":1,
                   "ARG":2,
                   "THIS":3,
                   "THAT":4}
    for i in range(16):
        symbolTable['R'+str(i)] = i
    return symbolTable


def findAsmFiles(dir):
    files = []
    if dir.endswith(".asm"): # directory is of a asm file
        files.append(dir)
    else: # search asm files in directory
        for file in os.listdir(dir):
            if file.endswith(".asm"):
                files.append(dir+"//"+file)
    return files


def readFile(file):
    f = open(file, "r")
    content = f.readlines()
    f.close()
    return content

def parse(fList, symbolsTable, fileName):
    fList = cleanFile(fList)
    fList, symbolsTable = translateSymbols(fList, symbolsTable)
    outputList = recognizeInstruction(fList)
    createOutputFile(outputList, fileName)


def cleanFile(fList):
    fList = [x.replace(' ', '') for x in fList]
    fList = [x.strip() for x in fList]
    for i in range (len(fList)):
        while("//" in fList[i]):
            fList[i] = fList[i].rsplit('//', 1)[0]
    fList = [x for x in fList if x != '']
    return fList

def recognizeInstruction(fList):
    outputList = []
    for line in fList:
        if (line[0] == '@'):
            outputList.append(aInstruction(line))
        else:
            outputList.append(cInstruction(line))
    return outputList

def aInstruction(line):
    line = line[1:] # remove @
    binVal =str(bin(int(line))[2:])
    lenVal = len(binVal)
    toAdd = 15-lenVal
    res = '0'+toAdd*'0'+binVal
    return res

def cInstruction(line):
    isShift = False
    if (line.find('<<')!= NOT_FOUND or line.find('>>') != NOT_FOUND):
        isShift = True
    if (line.find('=') != NOT_FOUND):  # the line contains '=', has dest value
        dest = line.rsplit('=', 1)[0]
        compAndJump = line.rsplit('=', 1)[1]
        comp = compAndJump.rsplit(';', 1)[0]
        if (len(compAndJump) > len(comp)):  # the line contains ';',
                                            #and has jump value
            jump = compAndJump.rsplit(';', 1)[1]
        else:
            jump = ''
    else:  # the line does not contain dest value
        comp = line.rsplit(';', 1)[0]
        jump = line.rsplit(';', 1)[1]
        dest = ''

    destBin = destDict[dest]
    jumpBin = jumpDict[jump]
    if isShift:
        compBin = shiftDect[comp]
        return compBin+'0000'+destBin+jumpBin
    compBin = compDict[comp]
    return '111'+compBin+destBin+jumpBin


def createOutputFile(outputList, inputFileName):
    outputFileName = inputFileName[:-3]+'hack'
    f = open(outputFileName, "w+")
    for line in outputList:
        f.write(line + '\n')


def translateSymbols(fList, symbolsTable):
    fList, symbolsTable = translateLabelSymbols(fList, symbolsTable)
    fList, symbolsTable = translateVariableSymbols(fList, symbolsTable)
    return fList, symbolsTable


def translateLabelSymbols(fList, symbolsTable):
    toDeleteArray = []
    labelCount = 0
    for i,line in enumerate(fList):
        if (line.find('(')!= NOT_FOUND):
            symbolsTable[line[1:-1]] = i-labelCount
            toDeleteArray.append(line)
            labelCount+=1
    for obj in toDeleteArray:
        fList.remove(obj)
    return fList, symbolsTable


def translateVariableSymbols(fList,symbolsTable):
    n = 16
    for i, line in enumerate(fList):
        if (line.find('@')!= NOT_FOUND and (not line[1:].isdigit())):
            if (not(line[1:] in symbolsTable)):
                symbolsTable[line[1:]] = n
                n+=1
            fList[i] = "@"+str(symbolsTable[line[1:]])
    return fList, symbolsTable

def main():
    symbolTable = createSymbolTable()
    dir = sys.argv[1]
    files = findAsmFiles(dir) #finds all asm type files in directory
    for file in files:
        fileList = readFile(file) #create an array of all lines in the file
        parse(fileList, symbolTable, file)
    return 0


if __name__ == "__main__":
    main()