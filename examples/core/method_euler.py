# Example
from typing_extensions import List, Optional

from examples.core.generics.engine import BaseConfig, BaseEngine
from py_ballisticcalc import *

# Concrete Engine classes (for example, Euler and RK methods)
class MethodEulerConfig(BaseConfig):
    step_size: float
    max_iterations: int

class MethodEulerEngine(BaseEngine[MethodEulerConfig]):
    def __init__(self, config: Optional[MethodEulerConfig] = None) -> None:
        self._config = config

    def reload(self, ammo: Ammo) -> None:
        """Method to init ammo"""
        pass

    @property
    def table_data(self) -> List[DragDataPoint]:
        """:return: List[DragDataPoint]"""
        return self._table_data

    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance,
                   extra_data: bool = False, time_step: float = 0.0) -> List[TrajectoryData]:
        pass

    def zero_angle(self, shot_info: Shot, distance: Distance) -> Angular:
        pass
