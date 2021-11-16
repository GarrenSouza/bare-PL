from activationFrame import ActivationFrame
from functools import reduce
import copy

class Function():
    
    def __init__(self, name, static_parent = None):
        self.name = name
        self.operations = []
        self.params = {}
        self.local_vars = {}
        self.static_vars = {}
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
        output += f"> temp_vars: "
        output += reduce(lambda x, y: x + y, [str(var) for var in self.temp_vars]) if self.temp_vars else "()"
        output += "\n"
        output += f"> activation_frame: "
        output += str(self.frame)
        output += "\n"
        output += f"> static_parent_name: "
        output += self.static_parent.name if self.static_parent else "None"
        return output


    def add_param(self, name):
        self.frame.params.append(0)
        self.params[name] = len(self.frame.params) - 1
        
    def add_variable(self, name):
        self.frame.local_vars.append(0)
        self.local_vars[name] = len(self.frame.local_vars) - 1

    def add_static_variable(self, name):
        self.frame.static_vars.append(0)
        self.local_vars[name] = len(self.frame.static_vars) - 1

    def getActivationFrame(self, caller_activation_frame):
        deepcopy = copy.deepcopy(self.frame)
        deepcopy.dynamic_link = caller_activation_frame