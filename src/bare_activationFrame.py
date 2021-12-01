class ActivationFrame():

    def __init__(self, owner):
        self.owner = owner
        self.static_link = None
        self.dynamic_link = None
        self.params = []
        self.local_vars = []
        self.static_vars = []
        self.external_vars = []
        self.temp_vars = []
        self.previous_PC = 0

    def get_owner_name(self):
        return self.owner.name if self.owner != None else "None"

    def get_dynamic_link_str(self):
        return self.dynamic_link.get_owner_name() if self.dynamic_link != None else "None"

    def get_static_link_str(self):
        return self.static_link.get_owner_name() if self.static_link != None else "None"

    def get_stack_representation(self):
        stack_rep = []
        if self.local_vars:
            stack_rep += self.local_vars
        if self.static_vars:
            stack_rep += self.static_vars
        if self.temp_vars:
            stack_rep += self.temp_vars
        if self.external_vars:
            stack_rep += self.external_vars
        if self.params:
            stack_rep += self.params
        stack_rep.append(self.get_dynamic_link_str())
        stack_rep.append(self.get_static_link_str())
        stack_rep.append(self.get_owner_name())
        stack_rep.append(self.previous_PC)
        return stack_rep

    def get_deep_copy(self):
        copy = ActivationFrame(self.owner)
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

