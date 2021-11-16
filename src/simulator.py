from enum import Enum

class Simulator():

    class operations(Enum):
        ATTRIB = 1
        INC = 2
        IF_ZERO = 3
        FUNCTION_CALL = 4
        SKIP = 5

    class registers(Enum):
        RETURN_REG = "__RETURN_REG__"
        AUX_REG = "__AUX_REG__"
        FLAG_REG = "__FLAG_REGISTER__"

    def __init__(self):
        self.code = []
        self.stack = []
        self.stack_pointer = 0
        self.program_counter = 0

    def attrib(self, function, op1, op2):
        pass

    def inc(self, function, op1, op2, op3):
        pass

    def if_zero(self, function, else_offset, op):
        pass

    def skip(self, function, amount):
        pass