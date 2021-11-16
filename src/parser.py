from function import Function
from simulator import Simulator as Sim

class Parser():

    def __init__(self, file_path):
        self.functions = {}
        self.static_vars = {"func_name" : {"var" : "value"}, }
        self.current_line = 1
        self.lines = self.load_lines(file_path)

    def inc_current_line(self, amount):
        self.current_line += amount

    def load_lines(self, file_path):
        with open(file_path, "r") as src_file:
            lines = [line.strip() for line in src_file.readlines()]
        return lines

    # key operations parsing

    def parse_def(self, tokens, static_parent):
        func = Function(tokens[1], static_parent) # static_parent é activation frame ou func?
        for param in tokens[2:]:
            func.add_param(param)

        self.inc_current_line(1)
        func.operations = self.parse_block(func)
        self.functions[func.name] = func

    def parse_block(self, func):
        self.inc_current_line(1)
        tokens = self.lines[self.current_line].split(" ")
        operations = []
        # let, slet, def, begin, end, ifzero, attrib, inc
        while tokens[0] != "end":
            if tokens[0] == "def":  # ok
                operations += self.parse_def(tokens, self.lines[1:], func)
            elif tokens[0] == "ifzero": # ok
                operations += self.parse_ifzero(tokens, self.lines[1:], func)
            elif tokens[0] == "let": # ok
                operations += self.parse_let(tokens, func)
            elif tokens[0] == "slet": # ok
                operations += self.parse_slet(tokens, func)
            elif tokens[0] == "attrib": # ok
                operations += self.parse_attrib(tokens, func)
            elif tokens[0] == "inc": # ok
                operations += self.parse_inc(tokens, func)
            elif tokens[0] == "return":  # ok
                operations += self.parse_return(tokens, func)
            tokens = self.lines[self.current_line].split(" ")
        self.inc_current_line(1)
        return operations

    def parse_ifzero(self, tokens, func):
        operations = []
        then_code = self.parse_block(func)
        else_offset = len(then_code)
        if self.lines[self.current_line] == "else":
            self.inc_current_line(1)

            else_code = self.parse_block(func)
            then_offset = len(else_code)
            operations = [(Sim.operations.IF_ZERO, else_offset, tokens[1])] + \
                            then_code + \
                            [(Sim.operations.SKIP, then_offset, tokens[1])] + \
                            else_code
        else:
            operations = [(Sim.operations.IF_ZERO, else_offset, tokens[1])] + \
                            then_code
        return operations

    def parse_return(self, tokens, func):
        operations = []
        if len(tokens) > 2:
            function_name = tokens[1]
            function_parameters = tokens[2:]
            operations.append((Sim.operations.FUNCTION_CALL, function_name, function_parameters))
        else:
            operations.append((Sim.operations.ATTRIB, Sim.registers.RETURN_REG, tokens[1]))
        self.inc_current_line(1)
        return operations

    def parse_inc(self, tokens, func):
        operations = []
        operations.append((Sim.operations.INC, tokens[1], tokens[2], Sim.registers.RETURN_REG))
        operations.append((Sim.operations.ATTRIB, Sim.registers.AUX_REG, Sim.registers.RETURN_REG))
        self.inc_current_line(1)
        return operations

    def parse_attrib(self, tokens, func):
        operations = []
        variable = tokens[1]
        if len(tokens) > 3:
            function_name = tokens[2]
            function_parameters = tokens[3:]
            operations.append((Sim.operations.FUNCTION_CALL, function_name, function_parameters))
            operations.append((Sim.operations.ATTRIB, variable, Sim.registers.RETURN_REG))
        else:
            operations.append((Sim.operations.ATTRIB, variable, tokens[2]))
        self.inc_current_line(1)
        return operations

    def parse_let(self, tokens, func):
        func.add_variable(tokens[1])
        self.inc_current_line(1)

    def parse_slet(self, tokens, func):
        func.add_static_variable(tokens[1])
        self.static_vars[func.name][tokens[1]] = 0
        self.inc_current_line(1)
