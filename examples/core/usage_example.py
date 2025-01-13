"""
Example how generic types can be used with py_ballisticcalc to allow use different calculation engines

Import universal Calculator interface and appropriate engines
    > from examples.core.calculator import Calculator
    > from examples.core.method_euler import MethodEulerEngine, MethodEulerConfig
    > from examples.core.method_rk4 import MethodRKEngine, MethodRKConfig
    
Define the correct configurations
    >  euler_cfg: MethodEulerConfig = {'step_size': 0.2, 'max_iterations': 20}  #  Euler configuration
    >  rk4_cfg: MethodRKConfig = {'step_size': 0.1, 'accuracy': 0.001}  #  RK configuration
    
define Calculator interface with Euler engine
    >  euler_calc = Calculator(MethodEulerEngine(euler_cfg))
    >  print(euler_calc)
    
define Calculator interface with RK engine
    >  rk4_calc = Calculator(MethodRKEngine(rk4_cfg))
    >  print(rk4_calc)
"""

from py_ballisticcalc import *

# set global library settings
loadMixedUnits()

# definitions for both calculations
weapon = Weapon(sight_height=Unit.Centimeter(9), twist=10)
dm = DragModel(0.381, TableG7, 300, 0.338, 1.7)
ammo = Ammo(dm=dm, mv=Unit.MPS(815), powder_temp=Unit.Celsius(0), temp_modifier=0.0123)
zero_atmo = Atmo(Unit.Meter(150), Unit.MmHg(745), Unit.Celsius(-1), 78)
zero = Shot(weapon=weapon, ammo=ammo, atmo=zero_atmo)
zero_distance = Unit.Meter(100)
current_atmo = Atmo(Unit.Meter(150), Unit.hPa(992), Unit.Celsius(23), 29)
shot = Shot(weapon=weapon, ammo=ammo, atmo=current_atmo)
config: InterfaceConfigDict = {'use_powder_sensitivity': True}

# use default Calculator interface from py_ballisticcalc
calc = Calculator(_config=config)
calc.set_weapon_zero(zero, zero_distance)
shot_result = calc.fire(shot, Distance.Meter(1000), extra_data=False)
expected_result = shot_result.trajectory[-1].in_def_units()

# override Calculator interface
# load MethodEulerEngine that is subclass of BaseEngine
from examples.core.calculator import Calculator
from examples.core.method_euler import MethodEulerEngine, MethodEulerConfig

config: MethodEulerConfig = {'use_powder_sensitivity': True}

# initialize Calculator with appropriate MethodEulerEngine
calc = Calculator(MethodEulerEngine())
# load ammo and engine config to Calculator, it will initialize the engine with this data
calc.reload(ammo, config=config)
# calculate data using Calculator interface methods with no need to work directly with the engine
calc.set_weapon_zero(zero, zero_distance)
shot_result = calc.fire(shot, Unit.Meter(1000), extra_data=False)
engine_result = shot_result.trajectory[-1].in_def_units()

# comparing the last result point
assert expected_result == engine_result





