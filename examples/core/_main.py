from examples.core.calculator import Calculator
from examples.core.method_euler import MethodEulerEngine, MethodEulerConfig
from examples.core.method_rk4 import MethodRKEngine, MethodRKConfig

# Define the correct configurations
euler_cfg: MethodEulerConfig = {'step_size': 0.2, 'max_iterations': 20}  # Euler configuration
rk4_cfg: MethodRKConfig = {'step_size': 0.1, 'accuracy': 0.001}  # RK configuration

euler_calc = Calculator(MethodEulerEngine, euler_cfg)

rk4_calc = Calculator(MethodRKEngine, rk4_cfg)
