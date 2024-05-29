import sys
import os

C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2
C_LABEL = 3
C_GOTO = 4
C_IF = 5
C_FUNCTION = 6
C_RETURN = 7
C_CALL = 8


commandDict = {"add": C_ARITHMETIC, "sub":C_ARITHMETIC, "neg":C_ARITHMETIC,
"eq":C_ARITHMETIC, "gt": C_ARITHMETIC, "lt":C_ARITHMETIC, "and":C_ARITHMETIC,
"or":C_ARITHMETIC, "not":C_ARITHMETIC, "push":C_PUSH, "pop":C_POP,
"label":C_LABEL, "goto":C_GOTO, "if-goto":C_IF, "function":C_FUNCTION,
"call":C_CALL, "return":C_RETURN
}



class Parser:

    def _readFile(self, file):
        f = open(file, "r")
        content = f.readlines()
        f.close()
        return content


    def _cleanFile(self, fList):
        #fList = [x.replace(' ', '') for x in fList]
        fList = [x.strip() for x in fList]
        for i in range(len(fList)):
            while ("//" in fList[i]):
                fList[i] = fList[i].rsplit('//', 1)[0]
        fList = [x for x in fList if x != '']
        return fList


    def _prepareFile(self, file):
        fileList = self._readFile(file)
        fileList = self._cleanFile(fileList)
        return fileList


    def hasMoreCommands(self):
        if (self.lineCount == len(self.fileList)-1):
            return False
        return True

    def advance(self):
        if (self.hasMoreCommands()): # this verification can be deleted
            self.lineCount+=1
            self.curLine = self.fileList[self.lineCount]

    def commandType(self):
        self.curLine = " ".join(self.curLine.split())
        command = self.curLine.rsplit(' ', -1)[0]
        return commandDict[command]



    def arg1(self):
        if (self.commandType()==C_ARITHMETIC):
            return self.curLine.rsplit(' ', -1)[0]
        else:
            return self.curLine.rsplit(' ', -1)[1]


    def arg2(self):
        return int(self.curLine.rsplit(' ', -1)[2])


    def __init__(self,file):
        self.lineCount = -1  # the number of the line we are on
        self.fileList = []  # the vm file in a list
        self.curLine = ""  # the current line in the file according to lineCount
        self.fileName = file
        self.fileList = self._prepareFile(file)



