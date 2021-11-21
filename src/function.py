from activationFrame import ActivationFrame
from enum import Enum
from functools import reduce

class Function():
    
    class var_scope(Enum):
        LOCAL = 0
        STATIC = 1
        EXTERNAL = 2
        PARAMETER = 3
        UNDEFINED = 4

    def __init__(self, name, static_parent = None):
        self.name = name
        self.operations = []
        self.params = {}
        self.local_vars = {}
        self.static_vars = {}
        self.external_vars = {}
        self.temp_vars = {}
        self.frame = ActivationFrame(self)
        self.static_parent = static_parent
        # self.frame.static_link = 

    def __str__(self):
        output = f"Function \"{self.name}\":\n"
        output += f"> params: \n"
        output += reduce(lambda x, y: x + y, [str(p) for p in self.params]) if self.params else "()"
        output += "\n"
        output += f"> operations: \n"
        output += reduce(lambda x, y: x + y, [str(op) + "\n" for op in self.operations]) if self.operations else "()"
        output += "\n"
        output += f"> local_vars: \n"
        output += reduce(lambda x, y: x + y, [str(var) for var in self.local_vars]) if self.local_vars else "()"
        output += "\n"
        output += f"> static_vars: \n"
        output += reduce(lambda x, y: x + y, [str(var) for var in self.static_vars]) if self.static_vars else "()"
        output += "\n"
        output += f"> external_vars: \n"
        output += reduce(lambda x, y: x + "," + y, [str(var) for var in self.external_vars]) if self.external_vars else "()"
        output += "\n"
        output += f"> activation_frame: "
        output += str(self.frame)
        output += "\n"
        output += f"> static_parent_name: "
        output += self.static_parent.name if self.static_parent else "None"
        return output

    def get_var_scope(self, var_name):
        if var_name in self.local_vars.keys():
            return self.var_scope.LOCAL
        if var_name in self.params.keys():
            return self.var_scope.PARAMETER
        if var_name in self.static_vars.keys():
            return self.var_scope.STATIC
        if var_name in self.external_vars.keys():
            return self.var_scope.EXTERNAL
        return self.var_scope.UNDEFINED

    def add_param(self, name):
        self.frame.params.append(0)
        self.params[name] = len(self.frame.params) - 1
        
    def add_variable(self, name):
        self.frame.local_vars.append(0)
        self.local_vars[name] = len(self.frame.local_vars) - 1

    def add_static_variable(self, name):
        self.frame.static_vars.append(0)
        self.static_vars[name] = len(self.frame.static_vars) - 1

    def add_external_variable(self, name):
        self.frame.external_vars.append(0)
        self.external_vars[name] = len(self.frame.external_vars) - 1

    def get_activation_frame(self):
        return self.frame.get_deep_copy()

    def set_var_value(self, destination, value, frame):
        destination_scope = self.get_var_scope(destination)

        if destination_scope == self.var_scope.LOCAL:
            frame.local_vars[self.local_vars[destination]] = value
        elif destination_scope == self.var_scope.PARAMETER:
            frame.params[self.params[destination]] = value
        elif destination_scope == self.var_scope.STATIC:
            frame.static_vars[self.static_vars[destination]] = value
        elif destination_scope == self.var_scope.EXTERNAL:
            frame.external_vars[self.external_vars[destination]] = value

    def get_var_value(self, var_name, frame):
        destination_scope = self.get_var_scope(var_name)

        if destination_scope == self.var_scope.LOCAL:
            return frame.local_vars[self.local_vars[var_name]]
        if destination_scope == self.var_scope.PARAMETER:
            return frame.params[self.params[var_name]]
        if destination_scope == self.var_scope.STATIC:
            return frame.static_vars[self.static_vars[var_name]]
        if destination_scope == self.var_scope.EXTERNAL:
            return frame.external_vars[self.external_vars[var_name]]