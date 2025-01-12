from py_ballisticcalc.conditions import Atmo, Shot, Wind
from py_ballisticcalc.drag_model import DragDataPoint
from py_ballisticcalc.munition import Ammo
from py_ballisticcalc.trajectory_data import TrajFlag
from py_ballisticcalc.unit import Angular, Distance
from py_ballisticcalc.trajectory_calc import Config
from py_ballisticcalc_exts import Vector, TrajectoryData
from typing_extensions import Union

__all__ = ['TrajectoryCalc']

class _TrajectoryDataFilter:
    filter: Union[TrajFlag, int]
    current_flag: Union[TrajFlag, int]
    seen_zero: Union[TrajFlag, int]
    current_item: int
    ranges_length: int
    previous_mach: float
    previous_time: float
    time_step: float
    next_range_distance: float
    def __init__(self, filter_flags: Union[TrajFlag, int], ranges_length: int) -> None: ...
    def setup_seen_zero(self, height: float, barrel_elevation: float, look_angle: float) -> None: ...
    def clear_current_flag(self) -> None: ...
    def should_record(self, range_vector: Vector, velocity: float, mach: float, step: float, look_angle: float, time: float) -> bool: ...
    def should_break(self) -> bool: ...
    def check_next_range(self, next_range: float, step: float) -> bool: ...
    def check_mach_crossing(self, velocity: float, mach: float): ...
    def check_zero_crossing(self, range_vector: Vector, look_angle: float): ...

class _WindSock:
    winds: tuple['Wind', ...]
    current: int
    next_range: float
    def __init__(self, winds: Union[tuple['Wind', ...], None]) -> None: ...
    def current_vector(self) -> Vector: ...
    def update_cache(self) -> None: ...
    def vector_for_range(self, next_range: float) -> Vector: ...

class TrajectoryCalc:
    barrel_azimuth: float
    barrel_elevation: float
    twist: float
    ammo: Ammo
    gravity_vector: Vector
    def __init__(self, ammo: Ammo, _config: Config) -> None: ...
    @property
    def table_data(self) -> list[DragDataPoint]: ...
    def get_calc_step(self, step: float = 0) -> float: ...
    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance, extra_data: bool = False, time_step: float = 0.0) -> list[TrajectoryData]: ...
    def zero_angle(self, shot_info: Shot, distance: Distance, time_step: float = 0.0) -> Angular: ...
    def drag_by_mach(self, mach: float) -> float: ...
    def spin_drift(self, time) -> float: ...
    def calc_stability_coefficient(self, atmo: Atmo) -> float: ...
