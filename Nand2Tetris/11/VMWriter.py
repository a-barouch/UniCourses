
segmentsDict = {"CONST": "constant", "ARG": "argument", "LOCAL": "local",
                    "STATIC": "static", "THIS":"this", "THAT": "that",
                    "POINTER": "pointer", "TEMP": "temp", "VAR":"local",
                    "FIELD":"field"}

commandDict = {"ADD":"add", "SUB":"sub", "NEG":"neg", "EQ": "eq", "GT":"gt",
               "LT":"lt","AND":"and", "OR":"or","NOT":"not"}

class VMWriter:

    def __init__(self, outputFileName):
        self.f = open(outputFileName, "a")


    def writePush(self, segment, index):
        self.f.write("push "+ segmentsDict[segment]+" " + str(index) + "\n")

    def writePop(self, segment, index):
        self.f.write("pop "+ segmentsDict[segment]+" " + str(index) + "\n")

    def writeArithmetic(self, command):
        self.f.write(commandDict[command] + "\n")

    def writeLabel(self, label):
        self.f.write("label " + label + "\n")

    def writeGoto(self, label):
        self.f.write("goto " + label + "\n")

    def writeIf(self, label):
        self.f.write("if-goto " + label + "\n")

    def writeCall(self,name,nArgs):
        self.f.write("call " + name + " " + str(nArgs) + "\n")

    def writeFunction(self,name,nLocals):
        self.f.write("function " + name + " " + str(nLocals) + "\n")

    def writeReturn(self):
        self.f.write("return\n")

    def close(self):
        self.f.close()

