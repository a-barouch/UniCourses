
class SymbolTable:

    def __init__(self):
        self.classSymbolTable = {}
        self.subroutineSymbolTable  = {}
        self.fieldCount = 0
        self.staticCount = 0
        self.argCount = 0
        self.localCount = 0

    def startSubroutine(self):
        self.subroutineSymbolTable = {}
        self.argCount = 0
        self.localCount = 0

    def define(self, name, type, kind):
        if (kind == "FIELD" or kind == "STATIC"):
            if (kind == "FIELD"):
                self.classSymbolTable[name] = [type, kind, self.fieldCount]
                self.fieldCount +=1
            elif (kind == "STATIC"):
                self.classSymbolTable[name] = [type, kind, self.staticCount]
                self.staticCount +=1
        else:
            if (kind == "VAR"):
                self.subroutineSymbolTable[name] = [type, kind, self.localCount]
                self.localCount +=1
            elif (kind == "ARG"):
                self.subroutineSymbolTable[name] = [type, kind, self.argCount]
                self.argCount +=1

    def varCount(self, kind):
        if (kind == "STATIC"):
            return self.staticCount
        elif (kind == "FIELD"):
            return self.fieldCount
        elif (kind == "ARG"):
            return self.argCount
        elif (kind == "VAR"):
            return self.localCount
        return 0

    def kindOf(self, name): # field,static,local,arg
        if (name in self.subroutineSymbolTable):
            return self.subroutineSymbolTable[name][1]
        elif (name in self.classSymbolTable):
            return self.classSymbolTable[name][1]
        else:
            return None

    def typeOf(self, name): #int,className...
        if (name in self.subroutineSymbolTable):
            return self.subroutineSymbolTable[name][0]
        elif (name in self.classSymbolTable):
            return self.classSymbolTable[name][0]
        else:
            return None

    def indexOf(self, name):
        if (name in self.subroutineSymbolTable):
            return self.subroutineSymbolTable[name][2]
        elif (name in self.classSymbolTable):
            return self.classSymbolTable[name][2]
        else:
            return None