"""
Now this module just wraps the default py_ballisticcalc.TrajectoryCalc and not overwrites it
It's not the realisation of MethodEulerEngine which should be when generics arch will be done
It's just an example which u can use as reference to understand how the generics will work
"""

from typing_extensions import List, Optional

from examples.core.generics.engine import BaseConfig, BaseEngine
from py_ballisticcalc import *
from py_ballisticcalc import create_interface_config


# Concrete Engine classes (for example, Euler and RK methods)
class MethodEulerConfig(BaseConfig):
    use_powder_sensitivity: bool


class MethodEulerEngine(BaseEngine[MethodEulerConfig]):
    def __init__(self, config: Optional[MethodEulerConfig] = None) -> None:
        self._config = config
        self._calc = None

    @property
    def _internal_calc(self) -> TrajectoryCalc:
        if self._calc:
            return self._calc
        raise RuntimeError("Reload solver first")

    def reload(self, ammo: Ammo, config: MethodEulerConfig = None) -> None:
        """Method to init ammo"""
        self._calc = TrajectoryCalc(ammo, _config=create_interface_config(config))

    @property
    def table_data(self) -> List[DragDataPoint]:
        """:return: List[DragDataPoint]"""
        return self._internal_calc.table_data

    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance,
                   extra_data: bool = False, time_step: float = 0.0) -> List[TrajectoryData]:
        return self._internal_calc.trajectory(shot_info, max_range, dist_step, extra_data, time_step)

    def zero_angle(self, shot_info: Shot, distance: Distance) -> Angular:
        return self._internal_calc.zero_angle(shot_info, distance)
