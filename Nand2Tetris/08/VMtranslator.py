import sys
import os
from Parser import Parser
from codeWriter import codeWriter

NOT_FOUND = -1
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

def findVMFiles(dir):
    files = []
    if dir.endswith(".vm"): # directory is of a asm file
        files.append(dir)
        outputFileName = dir[:-2] + 'asm'  # name of output file
    else: # search asm files in directory
        for file in os.listdir(dir):
            if file.endswith(".vm"):
                files.append(dir+"//"+file)
        outputFileName = dir +"//"+ os.path.basename(dir)+'.asm'
    return files, outputFileName



def fileTranslate(file, outputFileName, isBootstrap):
    fileParser = Parser(file)
    codeWrite = codeWriter(outputFileName,isBootstrap, file)
    while fileParser.hasMoreCommands():
        fileParser.advance()
        command = fileParser.commandType()
        if (command == C_RETURN):
            codeWrite.writeReturn()
            continue
        arg1 = fileParser.arg1()
        if (command == C_PUSH or command == C_POP
            or command == C_FUNCTION or command ==C_CALL):#only in this cases they are arg2
            arg2 = fileParser.arg2()

        if (command == C_ARITHMETIC):# we have an aritmetic option
            codeWrite.writeArithmetic(arg1)
        elif (command == C_PUSH or command == C_POP):#we have a pop or push
            codeWrite.writePushPop(command,arg1,arg2)
        elif (command == C_LABEL):
            codeWrite.writeLabel(arg1)
        elif (command == C_GOTO):
            codeWrite.writeGoto(arg1)
        elif (command == C_IF):
            codeWrite.writeIf(arg1)
        elif (command == C_FUNCTION):
            codeWrite.writeFunction(arg1,arg2)
        elif (command == C_CALL):
            codeWrite.writeCall(arg1,arg2)

    codeWrite.f.close()



def main():
    dir = sys.argv[1]
    files, outputFileName = findVMFiles(dir) #finds all vm type files in directory
    isBootstrap = True
    for file in files:
        fileTranslate(file, outputFileName, isBootstrap)
        isBootstrap = False
    return 0


if __name__ == "__main__":
    main()