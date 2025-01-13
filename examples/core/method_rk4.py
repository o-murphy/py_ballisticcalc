"""
Now this module just a placeholder for future RK4 method
It's not the realisation of MethodRKEngine
"""
from typing_extensions import List, Optional

from examples.core.generics.engine import BaseConfig, BaseEngine
from py_ballisticcalc import *


# Concrete Engine classes (for example, Euler and RK methods)
class MethodRKConfig(BaseConfig):
    step_size: float
    accuracy: float


class MethodRKEngine(BaseEngine[MethodRKConfig]):
    def __init__(self, config: Optional[MethodRKConfig] = None) -> None:
        self._config = config

    def reload(self, ammo: Ammo, config: MethodRKConfig = None) -> None:
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
