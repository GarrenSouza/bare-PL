class ActivationFrame():

    def __init__(self, owner):
        self.owner = owner
        self.static_link = None
        self.dynamic_link = None
        self.params = []
        self.local_vars = []
        self.static_vars = []
        self.temp_vars = []

    def __deepcopy__(self):
        copy = ActivationFrame()
        copy.owner = self.owner
        copy.static_link = self.static_link
        copy.dynamic_link = self.dynamic_link
        copy.params = self.params.copy()
        copy.local_vars = self.local_vars.copy()
        copy.static_vars = self.static_vars.copy()
        copy.temp_vars = self.temp_vars.copy()
        return copy

    def __str__(self):
        output = ""
        output += f"owner_function: {self.owner.name} "
        output += f"| static_link: ({str(self.static_link)}) "
        output += f"| dynamic_link: ({str(self.dynamic_link)}) "
        output += f"| params: ({str(self.params)}) "
        output += f"| local_vars: ({str(self.local_vars)}) "
        output += f"| static_vars: ({str(self.static_vars)}) "
        output += f"| temp_vars: ({str(self.temp_vars)})"
        return output

