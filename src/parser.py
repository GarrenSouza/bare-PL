import functools
from function import Function
from simulator import Simulator as Sim

class Parser():

    def __init__(self, file_path):
        self.functions = {}
        self.static_vars = {}
        self.current_line = 0
        self.lines = self.load_lines(file_path)
        self.global_scope_function = Function("__GLOBAL__", None)

    def inc_current_line(self, amount):
        self.current_line += amount

    def load_lines(self, file_path):
        with open(file_path, "r") as src_file:
            lines = list(filter(lambda x: x != "", [line.strip() for line in src_file.readlines()]))
        return lines

    # key operations parsing

    def parse_def(self, tokens, static_parent):
        print("parse_def")
        func = Function(tokens[1], static_parent) # static_parent é activation frame ou func?
        for param in tokens[2:]:
            func.add_param(param)

        self.inc_current_line(1)
        func.operations = self.parse_block(func)
        self.functions[func.name] = func
        return []

    def parse_block(self, func):
        print("parse_block")
        self.inc_current_line(1)
        tokens = self.lines[self.current_line].split(" ")
        operations = []
        # let, slet, def, begin, end, ifzero, attrib, inc
        print(f"parsing> {tokens}")
        while tokens[0] != "end":
            if tokens[0] == "def":  # ok
                operations += self.parse_def(tokens, func)
            elif tokens[0] == "ifzero": # ok
                operations += self.parse_ifzero(tokens, func)
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
            else:
                self.inc_current_line(1)
            tokens = self.lines[self.current_line].split(" ")
            print(f"parsing> {tokens}")
        self.inc_current_line(1)
        return operations

    def parse_ifzero(self, tokens, func):
        print("parse_if_zero")
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
        print("parse_return")
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
        print("parse_inc")
        operations = []
        operations.append((Sim.operations.INC, tokens[1], tokens[2], Sim.registers.RETURN_REG))
        operations.append((Sim.operations.ATTRIB, Sim.registers.AUX_REG, Sim.registers.RETURN_REG))
        self.inc_current_line(1)
        return operations

    def parse_attrib(self, tokens, func):
        print("parse_attrib")
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
        print("parse_let")
        func.add_variable(tokens[1])
        self.inc_current_line(1)
        return []

    def parse_slet(self, tokens, func):
        print("parse_slet")
        func.add_static_variable(tokens[1])
        self.static_vars[func.name][tokens[1]] = 0
        self.inc_current_line(1)
        return []

    def init_parsing(self):
        operations = []
        # let, slet, def, begin, end, ifzero, attrib, inc
        while self.current_line < len(self.lines):
            tokens = self.lines[self.current_line].split(" ")
            if tokens[0] == "def":  # ok
                operations += self.parse_def(tokens, self.global_scope_function)
            elif tokens[0] == "ifzero": # ok
                operations += self.parse_ifzero(tokens, self.global_scope_function)
            elif tokens[0] == "let": # ok
                operations += self.parse_let(tokens, self.global_scope_function)
            elif tokens[0] == "slet": # ok
                operations += self.parse_slet(tokens, self.global_scope_function)
            elif tokens[0] == "attrib": # ok
                operations += self.parse_attrib(tokens, self.global_scope_function)
            elif tokens[0] == "inc": # ok
                operations += self.parse_inc(tokens, self.global_scope_function)
            else: # ok
                self.inc_current_line(1)


p = Parser("../examples/test.txt")
p.init_parsing()
print("")
for f in p.functions.values():
    print(str(f)+"\n")