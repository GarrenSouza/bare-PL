from enum import Enum
import functools
from function import Function
from activationFrame import ActivationFrame

class Simulator():

    class operations(Enum):
        ATTRIB          = 1
        IF_ZERO         = 2
        SKIP            = 3
        FUNCTION_CALL   = 4
        
    class scope_resolution_modes(Enum):
        STATIC = 0
        DYNAMIC = 1

    class reserved_functions(Enum):
        GLOBAL = "__GLOBAL__"

    class registers(Enum):
        RETURN_REG = "__RETURN_REG__"
        AUX_REG = "__AUX_REG__"
        FLAG_REG = "__FLAG_REGISTER__"

    def __init__(self, functions, static_variables, scope_resolution_mode):
        self.functions = functions
        self.static_variables = static_variables
        self.internal_registers = { register : 0 for register in self.registers }
        self.current_function = self.functions[self.reserved_functions.GLOBAL]
        self.program_counter = 0
        self.scope_resolution_mode = scope_resolution_mode
        self.stack = []
        self.current_frame = None

    def __str__(self):
        state_string = "Simulator State"
        state_string += "-functions:\n"
        state_string += functools.reduce(lambda x,y : x + ", " + y, [function_name for function_name in self.functions.keys()])
        state_string += "\n"
        state_string += "-static variables:\n"
        for function, static_vars in self.static_variables:
            state_string += f"function: {function}\n"
            for static_var, value in static_vars:
                state_string += f"{static_var} : {value}\n"
        state_string += "\n"

        state_string += "-external_scope_resolution_mode: "
        state_string += self.scope_resolution_mode.value + "\n"

        state_string += str(self.current_function)
        state_string += str(self.current_frame)

        state_string += "-registers"
        for register in self.registers:
            state_string += f"{register.value} : {self.internal_registers[register]}"

        state_string += "-next instruction"
        state_string += str(self.current_function.code[self.program_counter])

        # functions DONE
        # static_vars DONE
        # modo DONE
        # current function DONE
        # current frame DONE
        # registers DONE
        # next instruction DONE
        pass

    def inc_program_counter(self, amount):
        self.program_counter += amount

    def attrib(self, instruction):

        destination = instruction[1]
        source = instruction[2]
        
        if source == self.registers.RETURN_REG.value:
            self.current_function.set_variable(destination, self.internal_registers[self.registers.RETURN_REG], self.current_frame)
        elif source.isnumeric():
            self.current_function.set_variable(destination, int(source), self.current_frame)
        else:
            self.current_function.set_variable(destination, source, self.current_frame)

        self.inc_program_counter(1)

    def inc(self, instruction):
        # op1, op2
        op1 = instruction[2][0]
        op2 = instruction[2][1]

        op1_value = int(op1) if op1.isnumeric() else self.current_function.get_var_value(op1, self.current_frame)
        op2_value = int(op2) if op1.isnumeric() else self.current_function.get_var_value(op2, self.current_frame)

        self.internal_registers[self.registers.RETURN_REG] = op1_value + op2_value
        self.inc_program_counter(1)

    def if_zero(self, instruction):
        # function, else_offset, op
        operand_value = int(instruction[2]) if instruction[2].isnumeric() else self.current_function.get_var_value(instruction[2], self.current_frame)
        if operand_value == 0:
            self.inc_program_counter(1)
        else:
            self.inc_program_counter(instruction[1])

    def skip(self, instruction):
        # function, amount
        self.inc_program_counter(instruction[1])

    def get_target_scope_dynamically(self, var_name, frame):
        dynamically_linked_frame = frame.static_link
        while dynamically_linked_frame != None:
            if dynamically_linked_frame.owner.get_var_scope(var_name) != Function.var_scope.UNDEFINED:
                return dynamically_linked_frame
            else:
                dynamically_linked_frame = dynamically_linked_frame.dynamic_link
        raise NameError

    def get_target_scope_statically(self, var_name, frame):
        statically_linked_frame = frame.static_link
        while statically_linked_frame != None:
            if statically_linked_frame.owner.get_var_scope(var_name) != Function.var_scope.UNDEFINED:
                return statically_linked_frame
            else:
                statically_linked_frame = statically_linked_frame.static_link
        raise NameError

    def get_var_value_dynamically(self, var_name, frame):
        return self.current_function.get_var_value(var_name, self.get_target_scope_dynamically(var_name, frame))

    def get_var_value_statically(self, var_name, frame):
        return self.current_function.get_var_value(var_name, self.get_target_scope_statically(var_name, frame))

    def set_var_value_dynamically(self, var_name, value, frame):
        self.current_function.set_var_value(var_name, value, self.get_target_scope_dynamically(var_name, frame))

    def set_var_value_statically(self, var_name, value, frame):
        self.current_function.set_var_value(var_name, value, self.get_target_scope_statically(var_name, frame))

    def function_call(self, instruction):
        function_name = instruction[1]
        if function_name == 'inc':
            self.inc(instruction)
        else:
            function_called = self.functions[function_name]
            parameters = instruction[2]
            activation_frame = function_called.get_activation_frame()
            activation_frame.owner = function_called
            activation_frame.previous_PC = self.program_counter + 1
            activation_frame.dynamic_link = self.stack[-1]

            for frame in reversed(self.stack):
                if frame.owner.name == function_called.static_parent.name:
                    activation_frame.static_link = frame
            
            activation_frame.static_link = None

            for param in parameters:
                if self.scope_resolution_mode == self.scope_resolution_modes.DYNAMIC:
                    function_called.set_var_value(param, self.get_var_value_dynamically(param, self.current_frame), activation_frame)
                elif self.scope_resolution_mode == self.scope_resolution_modes.STATIC:
                    function_called.set_var_value(param, self.get_var_value_statically(param, self.current_frame), activation_frame)
                else:
                    raise ValueError

            self.push_activation_frame(activation_frame)
            self.current_function = function_called
            self.program_counter = 0

            # instanciar activation_frame DONE
            # setar PC de retorno no activation frame DONE
            # setar pai dinamico DONE
            # setar pai estatico DONE
            # preencher parametros DONE
            #   external variables DONE
            # empilha o activation frame DONE
            # atualiza current_function DONE
            # reseta PC atual DONE

    def execute(self):
        self.function_call((self.reserved_functions.GLOBAL.value, []))
        while self.stack:
            instructions = self.current_function.code[self.program_counter]
            while self.program_counter < len(instructions):
                if instructions[0] == self.operations.ATTRIB:
                    self.attrib(instructions)
                elif instructions[0] == self.operations.FUNCTION_CALL:
                    self.function_call(instructions)
                elif instructions[0] == self.operations.IF_ZERO:
                    self.ifzero(instructions)
                elif instructions[0] == self.operations.SKIP:
                    self.skip(instructions)
                print(self)
                input("Press Enter to execute the next instruction...")
            self.pop_activation_frame()
        print(f"Program terminated with status {self.internal_registers[self.registers.RETURN_REG]}")

    def push_activation_frame(self, frame):
        self.stack.append(frame)
        self.current_frame = frame

    def pop_activation_frame(self):
        current_activation_frame = self.stack.pop()
        current_func = current_activation_frame.owner
        for static_var, location in current_func.static_vars.items():
            self.static_variables[current_func.name][static_var] = current_activation_frame.static_vars[location]

        self.program_counter = current_activation_frame.previous_PC
        self.current_frame = self.stack[-1]
        self.current_function = self.current_frame.owner

        for external_var, location in current_func.external_vars:
            if self.scope_resolution_mode == self.scope_resolution_modes.STATIC:
                self.set_var_value_statically(external_var, current_func.get_var_value(external_var, current_activation_frame), current_activation_frame)
            elif self.scope_resolution_mode == self.scope_resolution_modes.DYNAMIC:
                self.set_var_value_statically(external_var, current_func.get_var_value(external_var, current_activation_frame), current_activation_frame)
            else:
                raise ValueError