import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from VMWriter import VMWriter

def findJackFiles(dir):
    files = []
    if dir.endswith(".jack"): # directory is of a jack file
        files.append(dir)
    else: # search asm files in directory
        for file in os.listdir(dir):
            if file.endswith(".jack"):
                files.append(dir+"//"+file) # todo change in linux
    return files

def readFile(file):
    f = open(file, "r")
    content = f.readlines()
    f.close()
    return content

def compilationProcess(file, OutputFileName):
    tokenizer = JackTokenizer(file)
    vmWriter = VMWriter(OutputFileName)
    compilation = CompilationEngine(tokenizer, vmWriter)
    tokenizer.advance()
    compilation.CompileClass()



def main():
    dir = sys.argv[1]
    files = findJackFiles(dir) #finds all jack type files in directory
    for file in files:
        fileList = readFile(file) #create an array of all lines in the file
        outputFileName = file[:-4] + 'vm'
        compilationProcess(fileList, outputFileName)
    return 0


if __name__ == "__main__":
    main()