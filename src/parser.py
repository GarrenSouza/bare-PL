import functools
from enum import Enum
from function import Function
from simulator import Simulator as Sim

class Parser():

    # let, slet, def, begin, end, ifzero, attrib, inc
    class Keywords(Enum):
        attribution = "give"
        function_definition = "def"
        local_variable = "let"
        static_local_variable = "slet"
        block_start = "begin"
        block_end = "end"
        conditional = "ifzero"
        increment = "inc"
        return_statement = "return"

    def __init__(self, file_path):
        self.file_path = file_path
        self.functions = {}
        self.static_vars = {}
        self.current_line = 0
        self.lines = self.load_lines(file_path)
        self.global_scope_function = Function("__GLOBAL__", None)

    def inc_current_line(self, amount):
        self.current_line += amount

    def load_lines(self, file_path):
        with open(file_path, "r") as src_file:
            lines = [line.strip() for line in src_file.readlines()]
        return lines

    def print_bear(self):
        print('''$$$$$$$$$$$$**$$$$$$$$$**$$$$$$$$$$$$$$$
$$$$$$$$$$"   ^$$$$$$F    *$$$$$$$$$$$$$
$$$$$$$$$     z$$$$$$L    ^$$$$$$$$$$$$$
$$$$$$$$$    e$$$$$$$$$e  J$$$$$$$$$$$$$
$$$$$$$$$eee$$$$$$$$$$$$$e$$$$$$$$$$$$$$
$$$$$$$$b$$$$$$$BEAR$$$$$$$*$$$$$$$$$$$$
$$$$$$$)$$$$P"e^$$$F$r*$$$$F"$$$$$$$$$$$
$$$$$$$d$$$$  "z$$$$"  $$$$%  $3$$$$$$$$
$$$$*"""*$$$  .$$$$$$ z$$$*   ^$e*$$$$$$
$$$"     *$$ee$$$$$$$$$$*"     $$$C$$$$$
$$$.      "***$$"*"$$""        $$$$e*$$$
$$$b          "$b.$$"          $$$$$b"$$
$$$$$c.         """            $$$$$$$^$''')
    
    # parsing key operations
    def print_parse_call(self, keyword):
        print(f">> parsing {keyword}")

    def print_parse_line(self, line):
        print(f"@ line[{self.current_line + 1}] {line}")

    def define_static_variable(self, func, var_name):
        if func.name not in self.static_vars.keys():
            self.static_vars[func.name] = {}
        self.static_vars[func.name][var_name] = 0

    def parse_def(self, tokens, static_parent):
        self.print_parse_call(self.Keywords.function_definition.value)
        func = Function(tokens[1], static_parent) # static_parent é activation frame ou func?
        for param in tokens[2:]:
            func.add_param(param)

        self.inc_current_line(1)
        func.operations = self.parse_block(func)
        self.functions[func.name] = func
        return []

    def parse_block(self, func):
        self.print_parse_call(self.Keywords.block_start.value)
        self.print_parse_line(self.lines[self.current_line])
        self.inc_current_line(1)
        tokens = self.lines[self.current_line].split(" ")
        operations = []
        self.print_parse_line(self.lines[self.current_line])
        while tokens[0] != self.Keywords.block_end.value:
            if tokens[0] == self.Keywords.function_definition.value:
                operations += self.parse_def(tokens, func)
            elif tokens[0] == self.Keywords.conditional.value:
                operations += self.parse_ifzero(tokens, func)
            elif tokens[0] == self.Keywords.local_variable.value:
                operations += self.parse_let(tokens, func)
            elif tokens[0] == self.Keywords.static_local_variable.value:
                operations += self.parse_slet(tokens, func)
            elif tokens[0] == self.Keywords.attribution.value:
                operations += self.parse_attrib(tokens, func)
            elif tokens[0] == self.Keywords.increment.value:
                operations += self.parse_inc(tokens, func)
            elif tokens[0] == self.Keywords.return_statement.value:
                operations += self.parse_return(tokens, func)
            else:
                self.inc_current_line(1)
            tokens = self.lines[self.current_line].split(" ")
            self.print_parse_line(self.lines[self.current_line])
        self.inc_current_line(1)
        return operations

    def parse_ifzero(self, tokens, func):
        self.print_parse_call(self.Keywords.conditional.value)
        operations = []
        then_code = self.parse_block(func)
        else_offset = len(then_code)
        if self.lines[self.current_line] == "else":
            self.inc_current_line(1)

            else_code = self.parse_block(func)
            then_offset = len(else_code)
            operations = [(Sim.operations.IF_ZERO, else_offset + 1, tokens[1])] + \
                            then_code + \
                            [(Sim.operations.SKIP, then_offset, tokens[1])] + \
                            else_code
        else:
            operations = [(Sim.operations.IF_ZERO, else_offset, tokens[1])] + \
                            then_code
        return operations

    def parse_return(self, tokens, func):
        self.print_parse_call(self.Keywords.return_statement.value)
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
        self.print_parse_call(self.Keywords.increment.value)
        operations = []
        operations.append((Sim.operations.INC, tokens[1], tokens[2], Sim.registers.RETURN_REG))
        operations.append((Sim.operations.ATTRIB, Sim.registers.AUX_REG, Sim.registers.RETURN_REG))
        self.inc_current_line(1)
        return operations

    def parse_attrib(self, tokens, func):
        self.print_parse_call(self.Keywords.attribution.value)
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
        self.print_parse_call(self.Keywords.local_variable.value)
        func.add_variable(tokens[1])
        self.inc_current_line(1)
        return []

    def parse_slet(self, tokens, func):
        self.print_parse_call(self.Keywords.static_local_variable.value)
        func.add_static_variable(tokens[1])
        self.define_static_variable(func, tokens[1])
        self.inc_current_line(1)
        return []

    def init_parsing(self):
        print("# the bear programming language...")
        self.print_bear()
        print("----> Starting interpreter...")
        print(f"----> parsing: {self.file_path}")
        operations = []
        # let, slet, def, begin, end, ifzero, attrib, inc
        while self.current_line < len(self.lines):
            tokens = self.lines[self.current_line].split(" ")
            self.print_parse_line(self.lines[self.current_line])
            if tokens[0] == self.Keywords.function_definition.value:
                operations += self.parse_def(tokens, self.global_scope_function)
            elif tokens[0] == self.Keywords.conditional.value:
                operations += self.parse_ifzero(tokens, self.global_scope_function)
            elif tokens[0] == self.Keywords.local_variable.value:
                operations += self.parse_let(tokens, self.global_scope_function)
            elif tokens[0] == self.Keywords.static_local_variable.value:
                operations += self.parse_slet(tokens, self.global_scope_function)
            elif tokens[0] == self.Keywords.attribution.value:
                operations += self.parse_attrib(tokens, self.global_scope_function)
            elif tokens[0] == self.Keywords.increment.value:
                operations += self.parse_inc(tokens, self.global_scope_function)
            else:
                self.inc_current_line(1)
        print(f"----> parsed successfully!")


p = Parser("../examples/test.txt")
p.init_parsing()
print("")
for f in p.functions.values():
    print(str(f)+"\n")