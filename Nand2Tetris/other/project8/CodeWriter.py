from Parser import Command
from os import path

# magic numbers
RET = "15"
FRAME = "14"
SP = '0'
NEW_LINE = '\n'

# translate symbols into their meanings
SYMBOLS_TABLE = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "temp": 5,
    "stack": 256,
}

# trasition keyword into right address
TRANSITION_TO_ADDRESS = {
    "local": 1,
    "argument": 2,
    "this": 3,
    "that": 4,
}


def create_function_return(function_name):
    """static function to create the name of asm function"""
    temp = function_name + '$' + "ret" + '.' + str(
        CodeWriter.function_global_counter)
    CodeWriter.function_global_counter += 1
    return temp


def find_temp_place_in_stack(arg2):
    """calculate temp"""
    place_in_stack = str(5 + int(arg2))
    return place_in_stack


class CodeWriter:
    # static vars
    function_global_counter = 0
    counter_for_lg_gt = 0

    def __init__(self, parser, output_file, bootstrap=False):
        """constructor, create the file"""
        self.out_file = output_file
        self.parser = parser
        self.file_name = path.basename(self.parser.file.name)
        self.file_name = self.file_name.split('.')[0]
        self.current_function = ""  # to know which function I'm currently in
        if bootstrap:
            self.write_line_to_file("@256")
            self.write_line_to_file("D=A")
            self.write_line_to_file("@0")
            self.write_line_to_file("M=D")
            self.create_call("BOOTSTRAP_RETURN_ADDRESS", "Sys.init", '0')

    def write_all(self):
        """main method, to be used from outside, write the whole code"""
        while not self.parser.EOF:
            if self.parser.command == Command.C_ARITHMETIC:
                self.write_arithmetic()
            elif self.parser.command == Command.C_PUSH or self.parser.command \
                    == Command.C_POP:
                self.write_push_pop(self.parser.get_command(),
                                    self.parser.get_arg1(),
                                    self.parser.get_arg2())
            elif self.parser.command == Command.C_LABEL:
                self.write_label()
            elif self.parser.command == Command.C_GOTO:
                self.write_goto()
            elif self.parser.command == Command.C_IF:
                self.write_if_goto()
            elif self.parser.command == Command.C_FUNCTION:
                self.write_function()
            elif self.parser.command == Command.C_CALL:
                self.write_line_to_file("// CALL")
                self.create_call(self.current_function, self.parser.get_arg1(
                ), self.parser.get_arg2())
            elif self.parser.command == Command.C_RETURN:
                self.write_return()
            self.parser.advance()

    def write_return(self):
        """write return asm code"""
        self.write_line_to_file("//  FRAME=LCL")
        # FRAME=LCL
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["LCL"]))
        self.write_line_to_file("D=M")
        self.write_line_to_file('@' + FRAME)
        self.write_line_to_file("M=D")
        # RET=*(FRAME-5)
        self.write_line_to_file("//  RET=*(FRAME-5))")
        self.write_line_to_file("@5")
        self.write_line_to_file("A=D-A")
        self.write_line_to_file("D=M")
        self.write_line_to_file('@' + RET)
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  *ARG=pop()")
        # *ARG=pop()
        self.decrease_sp_and_read_into_d()
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["ARG"]))
        self.write_line_to_file("A=M")
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  SP=ARG+1")
        # SP=ARG+1
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["ARG"]))
        self.write_line_to_file("D=M")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["SP"]))
        self.write_line_to_file("M=D+1")
        self.write_line_to_file("//  THAT=*(FRAME-1)")
        # THAT=*(FRAME-1)
        self.decrease_frame_by_one_and_load_into_d()
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["THAT"]))
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  THIS=*(FRAME-2)")
        # THIS=*(FRAME-2)
        self.decrease_frame_by_one_and_load_into_d()
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["THIS"]))
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  ARG=*(FRAME-3)")
        # ARG=*(FRAME-3)
        self.decrease_frame_by_one_and_load_into_d()
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["ARG"]))
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  LCL=*(FRAME-4)")
        # LCL=*(FRAME-4)
        self.decrease_frame_by_one_and_load_into_d()
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["LCL"]))
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  GOTO RET")
        # GOTO RET
        self.write_line_to_file('@' + RET)
        self.write_line_to_file("A=M")
        self.write_line_to_file("0;JMP")

    def write_function(self):
        """write function asm code"""
        self.write_line_to_file("// FUNCTION")
        self.current_function = self.parser.get_arg1()
        self.write_line_to_file('(' + self.current_function + ')')
        for x in range(int(self.parser.get_arg2())):
            self.write_line_to_file("@0")
            self.write_line_to_file("D=A")
            self.load_from_d()
            self.increment_stack_pointer()

    def write_if_goto(self):
        """write IF-GOTO asm code"""
        self.write_line_to_file("// IF")
        self.decrease_sp_and_read_into_d()
        label = self.create_label()
        self.write_line_to_file('@' + label)
        self.write_line_to_file("D;JNE")

    def write_goto(self):
        """write GOTO asm code"""
        self.write_line_to_file("// GOTO")
        label = self.create_label()
        self.write_line_to_file('@' + label)
        self.write_line_to_file("0;JMP")

    def create_call(self, curr_function, function_to_jump, n_args):
        """write CALL asm code"""
        ret_label = create_function_return(curr_function)
        self.write_line_to_file("//  push ret address")
        self.value_into_stack(ret_label)
        self.write_line_to_file("//  push LCL")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["LCL"]))
        self.add_to_stack()
        self.write_line_to_file("//  push ARG")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["ARG"]))
        self.add_to_stack()
        self.write_line_to_file("//  push THIS")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["THIS"]))
        self.add_to_stack()
        self.write_line_to_file("//  push THAT")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["THAT"]))
        self.add_to_stack()
        self.write_line_to_file("//  ARG = SP  -5 -nARGS")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["SP"]))
        self.write_line_to_file("D=M")
        self.write_line_to_file("@5")
        self.write_line_to_file("D=D-A")
        self.write_line_to_file("@" + n_args)
        self.write_line_to_file("D=D-A")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["ARG"]))
        self.write_line_to_file("M=D")
        self.write_line_to_file("//  LCL = SP")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["SP"]))
        self.write_line_to_file("D=M")
        self.write_line_to_file('@' + str(SYMBOLS_TABLE["LCL"]))
        self.write_line_to_file("M=D")
        self.write_line_to_file('@' + function_to_jump)
        self.write_line_to_file("0;JMP")
        self.write_line_to_file('(' + ret_label + ')')

    def decrease_frame_by_one_and_load_into_d(self):
        """decrease frame by one and load its value into D"""
        self.write_line_to_file('@' + FRAME)
        self.write_line_to_file("M=M-1")
        self.write_line_to_file("A=M")
        self.write_line_to_file("D=M")

    def write_label(self):
        """write LABEL asm code"""
        temp_str = self.create_label()
        self.write_line_to_file('(' + temp_str + ')')

    def create_label(self):
        """create label according to naming convections"""
        return self.current_function + '$' + self.parser.get_arg1()

    def write_arithmetic(self):
        """Writer for any arithmetic function"""
        if self.parser.get_arg1() == "add":
            self.write_add()
        if self.parser.get_arg1() == "sub":
            self.write_sub()
        if self.parser.get_arg1() == "neg":
            self.write_neg()
        if self.parser.get_arg1() == "not":
            self.write_not()
        if self.parser.get_arg1() == "and":
            self.write_and()
        if self.parser.get_arg1() == "eq":
            self.write_eq()
        if self.parser.get_arg1() == "or":
            self.write_or()
        if self.parser.get_arg1() == "gt":
            self.write_line_to_file("// gt")
            self.gt()
        if self.parser.get_arg1() == "lt":
            self.write_line_to_file("// lt")
            self.lt()

    def write_sub(self):
        """write sub arithmetic"""
        self.write_line_to_file("// sub")
        self.decrease_sp_and_read_into_d()
        self.decrease_stack_pointer_and_read_into_a()
        self.write_line_to_file("D=M-D")
        self.read_from_d_into_stack()

    def write_add(self):
        """write add arithmetic"""
        self.write_line_to_file("// add")
        self.decrease_sp_and_read_into_d()
        self.decrease_stack_pointer_and_read_into_a()
        self.write_line_to_file("D=D+M")
        self.read_from_d_into_stack()

    def write_neg(self):
        """write neg arithmetic"""
        self.write_line_to_file("// neg")
        self.decrease_sp_and_read_into_d()
        self.write_line_to_file("D=-D")
        self.read_from_d_into_stack()

    def write_not(self):
        """write not arithmetic"""
        self.write_line_to_file("// not")
        self.decrease_sp_and_read_into_d()
        self.write_line_to_file("D=!D")
        self.read_from_d_into_stack()

    def write_and(self):
        """write and arithmetic"""
        self.write_line_to_file("// and")
        self.decrease_sp_and_read_into_d()
        self.decrease_stack_pointer_and_read_into_a()
        self.write_line_to_file("D=D&M")
        self.read_from_d_into_stack()

    def write_eq(self):
        """write eq arithmetic"""
        self.write_line_to_file("// eq")
        self.decrease_sp_and_read_into_d()
        self.decrease_stack_pointer_and_read_into_a()
        self.write_line_to_file("A=M")
        self.write_line_to_file("D=D-A")
        self.print_with_counter_for_lg_gt("@TRUE")
        self.write_line_to_file("D;JEQ")
        self.if_false_code()

    def write_or(self):
        """write or arithmetic"""
        self.write_line_to_file("// or")
        self.decrease_sp_and_read_into_d()
        self.decrease_stack_pointer_and_read_into_a()
        self.write_line_to_file("D=D|M")
        self.read_from_d_into_stack()

    def gt(self):
        """for gt function (greater than)"""
        self.decrease_sp_and_read_into_d()
        self.print_with_counter_for_lg_gt("@YBIGGERTHANZERO")
        self.write_line_to_file("D;JGE")
        # y bigger than zero
        self.write_line_to_file("@R13")
        # y loaded into R13
        self.write_line_to_file("M=D")
        self.decrease_sp_and_read_into_d()
        # if x>=0 than it must be true
        self.print_with_counter_for_lg_gt("@TRUE")
        self.write_line_to_file("D;JGE")
        self.write_line_to_file("@R13")
        # d = x - y
        self.write_line_to_file("D=D-M")
        self.print_with_counter_for_lg_gt("@TRUE")
        self.write_line_to_file("D;JGT")
        # second part x >= 0
        self.print_label_with_counter_for_lg_gt("YBIGGERTHANZERO")
        self.write_line_to_file("@R13")
        # y loaded into R13
        self.write_line_to_file("M=D")
        self.decrease_sp_and_read_into_d()
        # if x<=0 than it must be false
        self.print_with_counter_for_lg_gt("@FALSE")
        self.write_line_to_file("D;JLE")
        # if y>0 and x<=0 than it must be false
        self.write_line_to_file("@R13")
        # d = x - y
        self.write_line_to_file("D=D-M")
        self.print_with_counter_for_lg_gt("@TRUE")
        self.write_line_to_file("D;JGT")
        # false
        self.if_false_helper()

    def if_false_helper(self):
        self.print_label_with_counter_for_lg_gt("FALSE")
        self.if_false_code()

    def if_false_code(self):
        self.write_line_to_file("@0")
        self.write_line_to_file("D=A")
        self.print_with_counter_for_lg_gt("@END")
        self.write_line_to_file("0;JMP")
        self.print_label_with_counter_for_lg_gt("TRUE")
        self.write_line_to_file("D=-1")
        self.print_label_with_counter_for_lg_gt("END")
        self.load_from_d()
        self.increment_stack_pointer()
        CodeWriter.counter_for_lg_gt += 1

    def lt(self):
        """for lt function (less than)"""
        self.decrease_sp_and_read_into_d()
        self.print_with_counter_for_lg_gt("@YBIGGERTHANZERO")
        self.write_line_to_file("D;JGE")
        # y bigger than zero
        self.write_line_to_file("@R13")
        # y loaded into R13
        self.write_line_to_file("M=D")
        self.decrease_sp_and_read_into_d()
        # if x>=0 than it must be false
        self.print_with_counter_for_lg_gt("@FALSE")
        self.write_line_to_file("D;JGE")
        self.write_line_to_file("@R13")
        # d = x - y
        self.write_line_to_file("D=D-M")
        self.print_with_counter_for_lg_gt("@FALSE")
        self.write_line_to_file("D;JGE")
        # second part x >= 0
        self.print_label_with_counter_for_lg_gt("YBIGGERTHANZERO")
        self.write_line_to_file("@R13")
        # y loaded into R13
        self.write_line_to_file("M=D")
        self.decrease_sp_and_read_into_d()
        # if x<=0 than it must be false
        self.print_with_counter_for_lg_gt("@TRUE")
        self.write_line_to_file("D;JLE")
        # if y>0 and x<=0 than it must be false
        self.write_line_to_file("@R13")
        # d = x - y
        self.write_line_to_file("D=D-M")
        self.print_with_counter_for_lg_gt("@TRUE")
        self.write_line_to_file("D;JLT")
        # false
        self.if_false_helper()

    def print_with_counter_for_lg_gt(self, string):
        """print with counter (so label from diffrent parts in the program
        wont have the smae label)"""
        self.write_line_to_file(string + str(CodeWriter.counter_for_lg_gt))

    def print_label_with_counter_for_lg_gt(self, label):
        """print with counter (so label from diffrent parts in the program
        wont have the smae label)"""
        self.write_line_to_file(
            "(" + label + str(CodeWriter.counter_for_lg_gt) + ")")

    def decrease_stack_pointer_and_read_into_a(self):
        """read into a vraialbe (and SP--)"""
        self.decrement_stack_pointer()
        self.write_line_to_file("@0")
        self.write_line_to_file("A=M")

    def read_from_d_into_stack(self):
        """read into d vraialbe (and SP--)"""
        self.write_line_to_file("@0")
        self.write_line_to_file("A=M")
        self.write_line_to_file("M=D")
        self.increment_stack_pointer()

    def write_push_pop(self, command, arg1, arg2):
        """write the code for any push or pop commands"""
        if command == command.C_PUSH:
            self.write_line_to_file("// push")
            self.write_push(arg1, arg2)
        if command == command.C_POP:
            self.write_line_to_file("// pop")
            if arg1 == "temp":
                place_in_stack = find_temp_place_in_stack(arg2)
                self.decrease_sp_and_read_into_d()
                self.write_line_to_file("@" + place_in_stack)
                self.write_line_to_file("M=D")
            elif arg1 in TRANSITION_TO_ADDRESS:
                self.write_line_to_file("@" + str(TRANSITION_TO_ADDRESS[
                                                      arg1]))
                self.write_line_to_file("D=M")
                self.write_line_to_file("@" + arg2)
                self.write_line_to_file("D=A+D")
                self.write_line_to_file("@" + str(TRANSITION_TO_ADDRESS[
                                                      arg1]))
                self.write_line_to_file("M=D")
                self.decrease_sp_and_read_into_d()
                self.write_line_to_file("@" + str(TRANSITION_TO_ADDRESS[
                                                      arg1]))
                self.write_line_to_file("A=M")
                self.write_line_to_file("M=D")
                self.write_line_to_file("@" + str(TRANSITION_TO_ADDRESS[
                                                      arg1]))
                self.write_line_to_file("D=M")
                self.write_line_to_file("@" + arg2)
                self.write_line_to_file("D=D-A")
                self.write_line_to_file("@" + str(TRANSITION_TO_ADDRESS[
                                                      arg1]))
                self.write_line_to_file("M=D")

            elif arg1 == "static":
                str_stack_var_name = str(self.file_name) + '.' + str(arg2)
                self.decrease_sp_and_read_into_d()
                self.write_line_to_file("@" + str_stack_var_name)
                self.write_line_to_file("M=D")
            elif arg1 == "pointer":
                if arg2 == SP:
                    this_or_that = SYMBOLS_TABLE["THIS"]
                else:
                    this_or_that = SYMBOLS_TABLE["THAT"]
                self.decrease_sp_and_read_into_d()
                self.write_line_to_file("@" + str(this_or_that))
                self.write_line_to_file("M=D")

    def decrease_sp_and_read_into_d(self):
        """decrease SP and read its content into d"""
        self.decrease_stack_pointer_and_read_into_a()
        self.write_line_to_file("D=M")

    def write_push(self, arg1, arg2):
        """method resposible for creating push"""
        if arg1 == "temp":
            place_in_stack = find_temp_place_in_stack(arg2)
            self.write_line_to_file("@" + place_in_stack)
            self.add_to_stack()
        elif arg1 in TRANSITION_TO_ADDRESS:
            self.write_line_to_file("@" + str(TRANSITION_TO_ADDRESS[arg1]))
            self.write_line_to_file("D=M")
            self.write_line_to_file("@" + arg2)
            self.write_line_to_file("A=D+A")
            self.add_to_stack()
        elif arg1 == "constant":
            self.value_into_stack(arg2)
        elif arg1 == "static":
            str_stack_var_name = str(self.file_name) + '.' + str(arg2)
            self.write_line_to_file("@" + str_stack_var_name)
            self.write_line_to_file("D=M")
            self.load_from_d()
            self.increment_stack_pointer()
        elif arg1 == "pointer":
            if arg2 == SP:
                this_or_that = SYMBOLS_TABLE["THIS"]
            else:
                this_or_that = SYMBOLS_TABLE["THAT"]
            self.write_line_to_file("@" + str(this_or_that))
            self.write_line_to_file("D=M")
            self.load_from_d()
            self.increment_stack_pointer()

    def value_into_stack(self, value):
        """add value into stack"""
        self.write_line_to_file("@" + str(value))
        self.write_line_to_file("D=A")
        self.load_from_d()
        self.increment_stack_pointer()

    def add_to_stack(self):
        """add to stack from D value"""
        self.write_line_to_file("D=M")
        self.load_from_d()
        self.increment_stack_pointer()

    def load_from_d(self):
        """load value from D"""
        self.write_line_to_file("@0")
        self.write_line_to_file("A=M")
        self.write_line_to_file("M=D")

    def increment_stack_pointer(self):
        """increment stack pointer by 1, SP++"""
        self.increment_var(SP)

    def increment_var(self, var):
        """increment var by 1, var++"""
        self.write_line_to_file("@" + var)
        self.write_line_to_file("M=M+1")

    def decrement_var(self, var):
        """decrement var by 1, var--"""
        self.write_line_to_file("@" + var)
        self.write_line_to_file("M=M-1")

    def decrement_stack_pointer(self):
        """decrement stack pointer by 1, SP--"""
        self.decrement_var(SP)

    def write_line_to_file(self, string_to_write):
        """write the string into file and add new line"""
        self.out_file.write(string_to_write + NEW_LINE)
