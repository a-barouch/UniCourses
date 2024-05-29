from enum import Enum


class Command(Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8


ARITHMETIC_SET = {
    "add",
    "sub",
    "neg",
    "eq",
    "gt",
    "lt",
    "and",
    "or",
    "not"
}


class Parser:
    def __init__(self, location):
        """constrctor, init variables"""
        self.file = self.read_file(location)
        self.EOF = False
        self.arg1 = ""
        self.arg2 = ""
        self.command = ""
        self.advance()

    def read_file(self, location):
        """"read given file"""
        return open(location, "r")

    def get_command(self):
        """get command of current line"""
        return self.command

    def get_arg1(self):
        """get first argument of current line"""
        return self.arg1.strip()

    def get_arg2(self):
        """get second argument of current line"""
        return self.arg2.strip()

    def advance(self):
        """advance line by one, ignore non code lines"""
        self.current_line = self.file.readline()
        if self.current_line == "":
            self.EOF = True
            self.file.close()  # close file
        # check for comments
        elif self.current_line.startswith("//") or \
                self.current_line.startswith("\n") or \
                self.current_line.startswith("\r"):
            self.advance()
        else:
            self.set_command_name()
            args = self.current_line.split(' ')
            if self.command == Command.C_ARITHMETIC:
                self.arg1 = args[0]
            else:
                if len(args) > 1:
                    self.arg1 = args[1]
                if len(args) > 2:
                    self.arg2 = args[2]

    def set_command_name(self):
        """set command name"""
        if self.current_line.startswith("push"):
            self.command = Command.C_PUSH
        if self.current_line.startswith("pop"):
            self.command = Command.C_POP
        for command in ARITHMETIC_SET:
            if self.current_line.startswith(command):
                self.command = Command.C_ARITHMETIC
        if self.current_line.startswith("label"):
            self.command = Command.C_LABEL
        if self.current_line.startswith("goto"):
            self.command = Command.C_GOTO
        if self.current_line.startswith("if-goto"):
            self.command = Command.C_IF
        if self.current_line.startswith("function"):
            self.command = Command.C_FUNCTION
        if self.current_line.startswith("call"):
            self.command = Command.C_CALL
        if self.current_line.startswith("return"):
            self.command = Command.C_RETURN
