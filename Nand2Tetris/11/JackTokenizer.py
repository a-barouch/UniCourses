import re

keywordList = ["class", "method", "function", "constructor", "int", "boolean",
             "char", "void", "var", "static", "field", "let", "do", "if",
             "else", "while", "return", "true", "false", "null", "this"]

symbolList = ["{", "}", "[", "]", "(", ")", ".", ",", ";", "+", "-", "*", "/",
            "&", "|", "<", ">", "=", "~"]



class JackTokenizer:


    def tokenType(self):
        if (self.curToken in keywordList):
            self.curTokenType = "keyword"
            return "keyword"
        elif (self.curToken in symbolList):
            self.curTokenType = "symbol"
            return "symbol"
        elif (self.curToken.isdigit()):
            self.curTokenType = "integerConstant"
            return "integerConstant"
        elif (self.curToken.startswith('"')):
            self.curTokenType = "stringConstant"
            return "stringConstant"
        elif (not self.curToken[0].isdigit()):
            self.curTokenType = "identifier"
            return "identifier"


    def _createTokenList(self):
        stringReg = '[\\"][^\\"]+[\\"]'
        integerReg = '\d+'
        identifierReq = '\w+'
        keywordReg = 'class|method|function|constructor|int|boolean|char|' \
                     'void|var|static|field|let|do|if|else|while|return|true|' \
                     'false|null|this'
        symbolReg = '{|}|\[|\]|\(|\)|\.|,|;|\+|-|\*|\/|&|\||<|>|=|~'
        return re.findall(integerReg + "|" + identifierReq + "|" + keywordReg +
                          "|" + symbolReg + "|" +stringReg, self.file)

    def advance(self):
        if (self.hasMoreTokens()):
            self.curToken = self.tokenList[self.curIndex]
            self.tokenType()
            self.curIndex +=1

    def hasMoreTokens(self):
        if (self.curIndex == len(self.tokenList)-1):
            return False
        return True

    def _stripcomments(self, file):
        file =  re.sub('//.*?\n|/\*.*?\*/', '', file, flags=re.S).rstrip()
        file = file.splitlines()
        file = [x.strip() for x in file]
        file = [x.replace('\n', ' ') for x in file]
        file = [x for x in file if x != '']
        file = " ".join(file)
        return file

    def getToken(self):
        return self.curToken

    def __init__(self, file):
        self.file = self._stripcomments(" ".join(file))
        self.curIndex = 0
        self.curToken = ""
        self.curTokenType = ""
        self.tokenList = self._createTokenList()


