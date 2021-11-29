import sys
from src.bare_parser import Parser
from src.bare_simulator import Simulator as Sim

p = Parser(sys.argv[1])
p.init_parsing()
simulator = Sim(p.functions, p.static_vars, Sim.scope_resolution_modes.DYNAMIC)
simulator.execute()
