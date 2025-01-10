# Example
from typing_extensions import List

from examples.core.generics.engine import BaseConfig, BaseEngine
from py_ballisticcalc import *

# Concrete Engine classes (for example, Euler and RK methods)
class MethodRKConfig(BaseConfig):
    step_size: float
    accuracy: float

class MethodRKEngine(BaseEngine[MethodRKConfig]):
    def __init__(self, config: MethodRKConfig) -> None:
        self._config = config

    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance,
                   extra_data: bool = False, time_step: float = 0.0) -> List[TrajectoryData]:
        return []

    def zero_angle(self, shot_info: Shot, distance: Distance) -> Angular:
        return Angular.Degree(0.0)

