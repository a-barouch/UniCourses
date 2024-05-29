import os

GEN_REG = "@R13"
START_TEMP_SEG = 5
C_ARITHMETIC = 0
C_PUSH = 1
C_POP = 2
C_LABEL = 3
C_GOTO = 4
C_IF = 5
C_FUNCTION = 6
C_RETURN = 7
C_CALL = 8

segmentDict={"local": "LCL","argument":"ARG","this":"THIS","that":"THAT"}

arithmeticDict={"add":"+","sub":"-","and":"&","or":"|", "neg":"-", "not":"!",
                "eq":"JEQ","gt":"JGT","lt":"JLT"}

pointerDict = {0:"THIS",1:"THAT"}

class codeWriter:


    def _pop_LCL_ARG_TEMP_THIS_THAT(self, index, segment):
        """
        the pop operation for local, argument, temp, this and that
        """
        self.gen_reg_EQ_seg_plus_i(index, segment)
        self._decrementSP()
        self._p_addr_EQ_p_SP()


    def _push_LCL_ARG_TEMP_THIS_THAT(self, index, segment):
        """
        the push operation for local, argument, temp, this and that
        """
        self.gen_reg_EQ_seg_plus_i(index,segment)
        self._p_SP_EQ_p_addr()
        self._incrementSP()

    def _push_const(self, index):
        """
        the push operation for constant
        """
        self.f.write("@" + str(index) + "\n")
        self.f.write("D=A\n")
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("M=D\n")
        self._incrementSP()


    def _push_pointer(self,index):
        """
        the push operation for pointer
        """
        arg = pointerDict[index] # if index = 0 arg = THIS otherwise arg = THAT
        self.f.write("@" + arg + "\n")
        self.f.write("D=M\n")
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("M=D\n")
        self._incrementSP()

    def _pop_pointer(self,index):
        """
        the pop operation for pointer
        """
        arg = pointerDict[index] # if index = 0 arg = THIS otherwise arg = THAT
        self._decrementSP()
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("D=M\n")
        self.f.write("@"+arg+"\n")
        self.f.write("M=D\n")

    def _pop_static(self, index):
        """
        the pop operation for static
        """
        fileName = self.extractFileName()
        arg = fileName + str(index)
        self._decrementSP()
        self.f.write("A=M\n")
        self.f.write("D=M\n")
        self.f.write("@" + arg + "\n")
        self.f.write("M=D\n")

    def _push_static(self, index):
        """
        the push operation for static
        """
        fileName = self.extractFileName()
        arg = fileName + str(index)
        self.f.write("@" + arg + "\n")
        self.f.write("D=M\n")
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("M=D\n")
        self._incrementSP()

    def gen_reg_EQ_seg_plus_i(self, index, segment):
        # @13=segment+i
        if (segment =="temp"):
            index = index + START_TEMP_SEG # index = index +5
            self.f.write("@" + str(index) + "\n")
            self.f.write("D=A\n")
        else:
            val = segmentDict[segment]
            self.f.write("@"+val + "\n")
            self.f.write("D=M\n")
            self.f.write("@" + str(index) + "\n")
            self.f.write("D=D+A\n")
        self.f.write(GEN_REG + "\n")
        self.f.write("M=D\n")




    def _p_addr_EQ_p_SP(self):
        #*addr = *SP
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("D=M\n")
        self.f.write(GEN_REG + "\n")
        self.f.write("A=M\n")
        self.f.write("M=D\n")

    def _p_SP_EQ_p_addr(self):
        #*SP=*addr
        self.f.write(GEN_REG + "\n")
        self.f.write("A=M\n")
        self.f.write("D=M\n")
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("M=D\n")

    def _decrementSP(self):
        #SP--
        self.f.write("@SP\n")
        self.f.write("M=M-1\n")

    def _incrementSP(self):
        #SP++
        self.f.write("@SP\n")
        self.f.write("M=M+1\n")


    def _calc_binary_operation(self, sign):
        # uses two number from the stack and calculates
        # the sign operation on them
        self._decrementSP()
        self.f.write("A=M\n")
        self.f.write("D=M\n")
        self.f.write("@SP\n")
        self.f.write("M=M-1\n")
        self.f.write("A=M\n")
        self.f.write("M=M"+sign+"D\n")
        self._incrementSP()

    def _calc_unary_operation(self,sign):
        """
        calculates unary operations: not and neg
        """
        self.f.write("@SP\n")
        self.f.write("A=M-1\n")
        self.f.write("M="+sign+"M\n")

    def _calc_comparison_operation(self,command, label):
        """
        calculates comparison operations: eq, lt and gt
        """
        sign = arithmeticDict[command]
        if (command == "eq"):
            self._decrementSP()
            self.compare2Numbers(label, sign)
            return

        self._decrementSP()
        self.f.write("A=M\n")
        self.f.write("D=M\n")

        self.f.write("@"+"POS_Y"+label+"\n")
        self.f.write("D;JGT\n") # Y>0
        self.f.write("@" + "NEG_Y" + label + "\n")
        self.f.write("D;JLE\n") # Y<=0

        self.f.write("(POS_Y"+label+")\n")
        self.f.write("@SP\n")
        self.f.write("A=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@"+"POS_X_Y"+label+"\n")
        self.f.write("D;JGT\n") #Y>0 & X>0
        self.f.write("@" + "POS_Y_NEG_X" + label + "\n")
        self.f.write("D;JLE\n") #Y>0 & X<=0

        self.f.write("(NEG_Y" + label + ")\n")
        self.f.write("@SP\n")
        self.f.write("A=M-1\n")
        self.f.write("D=M\n")
        self.f.write("@" + "NEG_Y_POS_X" + label + "\n")
        self.f.write("D;JGT\n")  # X>0 & Y<0
        self.f.write("@" + "NEG_X_Y" + label + "\n")
        self.f.write("D;JLE\n")  # Y<=0 & X<=0

        self.f.write("(POS_X_Y" + label + ")\n")
        self.compare2Numbers(label, sign)
        self.f.write("@END" + label + "\n")
        self.f.write("0;JMP\n")

        self.f.write("(NEG_X_Y" + label + ")\n")
        self.compare2Numbers(label, sign)
        self.f.write("@END" + label + "\n")
        self.f.write("0;JMP\n")

        self.f.write("(NEG_Y_POS_X" + label + ")\n")
        if (command== "gt"):
            self.f.write("@SP\n")
            self.f.write("A=M-1\n")
            self.f.write("M=-1\n")
            self.f.write("@END" + label + "\n")
            self.f.write("0;JMP\n")

        elif (command == "lt"):
            self.f.write("@SP\n")
            self.f.write("A=M-1\n")
            self.f.write("M=0\n")
            self.f.write("@END" + label + "\n")
            self.f.write("0;JMP\n")

        self.f.write("(POS_Y_NEG_X" + label + ")\n")
        if (command== "gt"):
            self.f.write("@SP\n")
            self.f.write("A=M-1\n")
            self.f.write("M=0\n")
            self.f.write("@END" + label + "\n")
            self.f.write("0;JMP\n")

        elif (command == "lt"):
            self.f.write("@SP\n")
            self.f.write("A=M-1\n")
            self.f.write("M=-1\n")
            self.f.write("@END" + label + "\n")
            self.f.write("0;JMP\n")

        self.f.write("(END" + label + ")\n")

    def compare2Numbers(self, label, sign):
        """
        does the sign comparison between x and y from the stack
        """
        self.f.write("@SP\n")
        self.f.write("A=M\n")
        self.f.write("D=M\n")
        self.f.write("@SP\n")
        self.f.write("A=M-1\n")
        self.f.write("D=M-D\n")
        self.f.write("M=-1\n")  # we assign true to the last place in the stack
        self.f.write("@" + label + "\n")
        self.f.write("D;" + sign + "\n")  # jump operation according to
                                            # compare type
        self.f.write("@SP\n")
        self.f.write("A=M-1\n")
        self.f.write("M=0\n")  # comparison is false
        self.f.write("(" + label + ")\n")

    def writeArithmetic(self, command):
        """
        calls the right arithmetic operation to translate to assembly
        """
        if (command == "add" or command == "sub" or command == "and"
         or command == "or"):
            self._calc_binary_operation(arithmeticDict[command])

        elif (command == "not" or command == "neg"):
            self._calc_unary_operation(arithmeticDict[command])

        else:
            label = "label" + str(self.curLabel)
            self._calc_comparison_operation(command, label)
            self.curLabel +=1



    def writePushPop(self, command, segment, index):
        """
        calls the right push\pop operation to translate to assembly
        """
        if (command == C_PUSH):
            if (segment == "static"):
                self._push_static(index)
            elif (segment == "constant"):
                self._push_const(index)
            elif(segment == "pointer"):
                self._push_pointer(index)
            else:
                self._push_LCL_ARG_TEMP_THIS_THAT(index, segment)
        elif (command == C_POP):
            if (segment == "static"):
                self._pop_static(index)
            elif(segment == "pointer"):
                self._pop_pointer(index)
            else:
                self._pop_LCL_ARG_TEMP_THIS_THAT(index, segment)


    def extractFileName(self):
        """
        extracts name out of file directory
        """
        return os.path.basename(self.curReadingFile)[:-2]



    def __init__(self,file, curReadingFile):
        self.curReadingFile = curReadingFile
        self.outputFileDir = file
        self.f = open(self.outputFileDir, "a")
        self.curLabel = 0



