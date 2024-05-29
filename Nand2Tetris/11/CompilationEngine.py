
from SymbolTable import SymbolTable
statementsList = ["let", "if", "while", "do", "return"]
operationList=["+","-","*","/","&","|","<",">","="]

keywordConstList=["true","false","null","this"]

operationDict = {"+": "ADD", "-": "SUB", "&": "AND", "|": "OR", "<": "LT",
                 ">": "GT","=":"EQ"}
unaryOperationDict = {"-":"NEG", "~":"NOT"}


segmentsDict = {"constant": "CONST", "argument": "ARG", "local": "VAR",
                    "static": "STATIC", "this":"THIS", "that": "THAT",
                    "pointer": "POINTER", "temp": "TEMP", "field":"FIELD"}

class CompilationEngine:
    def compileExpressionList(self):
        numOfArgs = 0
        if (not self.tkn.getToken()== ")" ):
            self.CompileExpression()
            numOfArgs+=1
            while (self.tkn.getToken() == ","):
                numOfArgs +=1
                self.nextToken()  # ,
                self.CompileExpression()
        return numOfArgs

    def _compileSubroutineCall(self):
        beforDot = self.tkn.getToken()
        self.nextToken()  # varName / subroutineName /className
        numOfArgs = 0
        if (self.tkn.getToken() == "("): # was subroutineName that is method
            self.nextToken()  # (
            self.vmWriter.writePush("POINTER", 0)
            numOfArgs = self.compileExpressionList()
            numOfArgs+=1 # for a method todo check if need change
            self.nextToken()  # )
            subroutineName = self.curClassName + "." + beforDot
        else:
            self.nextToken()  # .
            afterDot = self.tkn.getToken()
            if (self.symbolTable.kindOf(beforDot) == None): # is a class, does not appear in the symbol table
                subroutineName = beforDot + "." + afterDot
            else:   # varName
                varKind = self.symbolTable.kindOf(beforDot)
                varType = self.symbolTable.typeOf(beforDot)
                varIndex = self.symbolTable.indexOf(beforDot)
                if (varKind == "FIELD"):
                    varKind = "THIS"
                self.vmWriter.writePush(varKind, varIndex)
                subroutineName = varType + "." + afterDot
                numOfArgs+=1 # this is a method therefor arguments include this
            self.nextToken()  # subroutineName
            self.nextToken()  # (
            numOfArgs += self.compileExpressionList()
            self.nextToken()  # )
        self.vmWriter.writeCall(subroutineName, numOfArgs)



    def compileTerm(self):
        # if term is integer const or keyword const
        if (self.tkn.curTokenType == "integerConstant"):
            curConstant =  self.tkn.getToken()
            self.vmWriter.writePush("CONST", curConstant)
            self.nextToken()  # int or keyword

        elif (self.tkn.getToken() in keywordConstList):
            curConstant =  self.tkn.getToken()
            if (curConstant == "this"):
                self.vmWriter.writePush("POINTER", 0)
            else:
                self.vmWriter.writePush("CONST", 0)
            if (curConstant == "true"):
                self.vmWriter.writeArithmetic("NOT")
            self.nextToken()  # int or keyword


        # if term is string const
        elif (self.tkn.curTokenType == "stringConstant"):
                self.tkn.curToken = self.tkn.curToken[1:-1]
                self.tkn.curTokenType = "stringConstant"
                curString = self.tkn.getToken()
                self.vmWriter.writePush("CONST", len(curString))
                self.vmWriter.writeCall("String.new", 1)

                for i in curString:
                    self.vmWriter.writePush("CONST", ord(i))
                    self.vmWriter.writeCall("String.appendChar",2)

                self.nextToken()  # string

        # if term is unary operation
        elif (self.tkn.getToken() == "-" or self.tkn.getToken() == "~"):
            curUnaryOp =  self.tkn.getToken()
            self.nextToken() # - or ~
            self.compileTerm()
            self.vmWriter.writeArithmetic(unaryOperationDict[curUnaryOp])

        # (expression)
        elif (self.tkn.getToken() == "("):
            self.nextToken() # (
            self.CompileExpression()
            self.nextToken() #)

        #
        elif (self.tkn.tokenType() == "identifier"):
            nextToken = self.tkn.tokenList[self.tkn.curIndex]
            if (nextToken == "." or nextToken == "("):
                self._compileSubroutineCall()
            elif (nextToken == "["):
                arrKind = self.symbolTable.kindOf(self.tkn.getToken())
                arrIndex = self.symbolTable.indexOf(self.tkn.getToken())
                self.nextToken()  # varName
                self.nextToken()  # [
                self.CompileExpression()
                self.nextToken()  # ]
                self.vmWriter.writePush(arrKind, arrIndex)
                self.vmWriter.writeArithmetic(operationDict["+"])
                self.vmWriter.writePop("POINTER", 1)
                self.vmWriter.writePush("THAT", 0)

            else:
                varName = self.tkn.getToken()
                varKind = self.symbolTable.kindOf(varName)
                varIndex = self.symbolTable.indexOf(varName)
                if (varKind == "FIELD"):
                    varKind = "THIS"
                self.vmWriter.writePush(varKind,varIndex)
                self.nextToken()  # varName

        else:
            self._compileSubroutineCall()




    def CompileExpression(self):
        self.compileTerm()
        while (self.tkn.getToken() in operationList):
            curOperation = self.tkn.getToken()
            self.nextToken()  # operation
            self.compileTerm()
            if (curOperation == "*"):
                self.vmWriter.writeCall("Math.multiply", 2)
            elif (curOperation == "/"):
                self.vmWriter.writeCall("Math.divide", 2)
            else:
                self.vmWriter.writeArithmetic(operationDict[curOperation])

    def compileLet(self):
        self.nextToken() # let
        varName = self.tkn.getToken()
        varKind = self.symbolTable.kindOf(varName)
        varIndex = self.symbolTable.indexOf(varName)
        if (varKind == "FIELD"):
            varKind = "THIS"
        self.nextToken()  # varName
        wasInArray = False
        if (self.tkn.getToken() =="["):
            wasInArray = True
            self.nextToken() # [
            self.CompileExpression()
            self.nextToken() # ]
            self.vmWriter.writePush(varKind, varIndex)
            self.vmWriter.writeArithmetic(operationDict["+"])
        self.nextToken()  # =
        self.CompileExpression()
        self.nextToken()  # ;
        if (wasInArray):
            self.vmWriter.writePop("TEMP",0)
            self.vmWriter.writePop("POINTER",1)
            self.vmWriter.writePush("TEMP",0)
            self.vmWriter.writePop("THAT",0)
        else:
            self.vmWriter.writePop(varKind,varIndex)

    def compileDo(self):
        self.nextToken()  # do
        self._compileSubroutineCall()
        self.vmWriter.writePop("TEMP",0)
        self.nextToken()  # ;

    def compileIf(self):
        self.ifCount +=1
        curIfIndex = self.ifCount
        self.nextToken()  # if
        self.nextToken()  # (
        self.CompileExpression()
        self.vmWriter.writeIf("IF_TRUE" + str(curIfIndex))
        self.vmWriter.writeGoto("IF_FALSE" + str(curIfIndex))
        self.vmWriter.writeLabel("IF_TRUE" + str(curIfIndex))
        self.nextToken()  # )
        self.nextToken()  # {
        self.compileStatements()
        self.nextToken()  # }
        if (self.tkn.getToken() == "else"):
            self.vmWriter.writeGoto("IF_END" + str(curIfIndex))
        self.vmWriter.writeLabel("IF_FALSE" + str(curIfIndex))
        if (self.tkn.getToken() == "else"):
            self.nextToken()  # else
            self.nextToken()  # {
            self.compileStatements()
            self.nextToken()  # }
            self.vmWriter.writeLabel("IF_END" + str(curIfIndex))



    def compileWhile(self):
        self.whileCount+=1
        curWhileCount = self.whileCount
        self.vmWriter.writeLabel("WHILE_EXP"+str(curWhileCount))
        self.nextToken()  # while
        self.nextToken()  # (
        self.CompileExpression()
        self.vmWriter.writeArithmetic("NOT")
        self.nextToken()  # )
        self.vmWriter.writeIf("WHILE_END" + str(curWhileCount))
        self.nextToken()  # {
        self.compileStatements()
        self.nextToken()  # }
        self.vmWriter.writeGoto("WHILE_EXP"+str(curWhileCount))
        self.vmWriter.writeLabel("WHILE_END" + str(curWhileCount))


    def compileReturn(self):
        self.nextToken()  # return
        if (not self.tkn.getToken() == ";"):
            self.CompileExpression()
        else:
            self.vmWriter.writePush("CONST",0) #in case of void function
        self.nextToken()  # ;
        self.vmWriter.writeReturn()

    def compileStatements(self):
        while(self.tkn.getToken() in statementsList):
            if (self.tkn.getToken() =="let"):
                self.compileLet()
            if (self.tkn.getToken() =="do"):
                self.compileDo()
            if (self.tkn.getToken() =="if"):
                self.compileIf()
            if (self.tkn.getToken() =="return"):
                self.compileReturn()
            if (self.tkn.getToken() =="while"):
                self.compileWhile()



    def CompileParameterList(self):
        if (not self.tkn.getToken() ==")"): # check if there are parameters
            varType = self.tkn.getToken()
            self.nextToken()  # type (int/boolean etc)
            varName = self.tkn.getToken()
            self.nextToken()  # varName
            self.symbolTable.define(varName,varType,"ARG")
            while (self.tkn.getToken() == ","):
                self.nextToken()  # ,
                varType = self.tkn.getToken()
                self.nextToken()  # type
                varName = self.tkn.getToken()
                self.nextToken()  # varName
                self.symbolTable.define(varName, varType, "ARG")



    def compileVarDec(self):
        varCount = 0
        self.nextToken()  # var

        varType = self.tkn.getToken()
        self.nextToken()  # type

        varName = self.tkn.getToken()
        self.nextToken()  # varName

        varCount += 1
        self.symbolTable.define(varName,varType,"VAR")
        while (self.tkn.getToken() == ","):
            varCount+=1
            self.nextToken()  # ,
            varName = self.tkn.getToken()
            self.nextToken()  # varName
            self.symbolTable.define(varName, varType, "VAR")
        self.nextToken()  # ;
        return varCount


    def CompileClassVarDec(self):
        varKind = self.tkn.getToken()
        if (varKind == "field"):
            self.fieldsCount+=1
        self.nextToken() # field or static

        varType = self.tkn.getToken()
        self.nextToken() # type (int/boolean etc)

        varName = self.tkn.getToken()
        self.nextToken() #varName

        self.symbolTable.define(varName, varType, segmentsDict[varKind])
        while (self.tkn.getToken() == ","):
            self.nextToken() # ,
            varName = self.tkn.getToken()
            self.nextToken() # varName
            self.symbolTable.define(varName, varType, segmentsDict[varKind])
            if (varKind == "field"):
                self.fieldsCount += 1
        self.nextToken() # ;

    def CompileSubroutine(self):
        self.whileCount = -1
        self.ifCount = -1
        subroutineType = self.tkn.getToken()
        self.nextToken() #constructor, function or method
        self.nextToken() #void or type
        subroutineName = self.curClassName + "." + self.tkn.getToken()
        self.nextToken() #subroutine name
        self.nextToken() #(
        # adds this argument to a method of a class
        if (subroutineType == "method"):
            self.symbolTable.define("this", self.curClassName, 'ARG')
        self.CompileParameterList()
        self.nextToken()  # )

        # handles subroutine variables declerations
        self.nextToken()  # {
        subroutineLocalCount = 0

        # while a variable is declared
        while (self.tkn.getToken() == "var"):
            subroutineLocalCount += self.compileVarDec()
        self.vmWriter.writeFunction(subroutineName,subroutineLocalCount)

        if (subroutineType == "constructor"):
            self.vmWriter.writePush("CONST", self.fieldsCount)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("POINTER", 0)
        elif (subroutineType == "method"):
            self.vmWriter.writePush("ARG",0 )
            self.vmWriter.writePop("POINTER", 0)
        #handles the rest of the subroutine
        self.compileStatements()
        self.nextToken()  # }
        self.symbolTable.startSubroutine()




    def CompileClass(self):
        self.nextToken() # class
        self.curClassName = self.tkn.getToken() #get className into curClassName
        self.nextToken() # className
        self.nextToken() # {

        while (self.tkn.getToken() == "static" or self.tkn.getToken() == "field"):
            self.CompileClassVarDec()

        while (self.tkn.getToken() == "constructor" or
               self.tkn.getToken() == "function" or
                self.tkn.getToken() == "method"):
            self.CompileSubroutine()
        self.nextToken()  # }
        self.vmWriter.close()


    def nextToken(self):

        # todo probably to delete all lines
        toWrite = self.tkn.getToken()
        if (self.tkn.getToken() == "&"):
            toWrite = "&amp;"
        elif (self.tkn.getToken() == "<"):
            toWrite = "&lt;"
        elif (self.tkn.getToken() == ">"):
            toWrite = "&gt;"
        elif (self.tkn.getToken() == '\\"'):
            toWrite = "&quot;"
        self.tkn.advance()

    def __init__(self, tokenizer, vmWriter):
        self.symbolTable = SymbolTable()
        self.tkn = tokenizer
        self.vmWriter = vmWriter
        self.whileCount = -1
        self.ifCount = -1
        self.fieldsCount = 0