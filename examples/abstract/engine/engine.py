import math
from abc import ABC, abstractmethod
from typing import List, Protocol, Union, TypeVar, Generic, TypedDict, Type

from py_ballisticcalc import *


# Type variable for flexible data type
T_Data = TypeVar("T_Data")


# Define a generic TypedDict for engine configurations
class BaseEngineConfigDict(TypedDict, Generic[T_Data]):
    """Generic TypedDict with a flexible value type."""
    id: int
    data: T_Data  # This can be any type


class BaseEngine(ABC):
    """Abstract base class for ballistics engines."""

    barrel_azimuth: float
    barrel_elevation: float
    twist: float
    ammo: Ammo
    gravity_vector: Vector
    _table_data: List[DragDataPoint]

    # Nested configuration class for engine-specific configurations
    class BaseEngineConfig(Protocol):
        """Base protocol for engine configurations."""

        @classmethod
        def from_dict(cls, d: BaseEngineConfigDict[T_Data]) -> "BaseEngine.BaseEngineConfig":
            """Create an instance from a dictionary."""
            raise NotImplementedError("Must implement from_dict method.")

    def __init__(self, ammo: Ammo, _config: BaseEngineConfig[T_Data]):
        self.ammo = ammo
        self._config = _config

    @property
    def table_data(self) -> List[DragDataPoint]:
        return self._table_data

    @abstractmethod
    def zero_angle(self, shot_info: Shot, distance: Distance) -> Angular:
        ...

    @abstractmethod
    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance,
                   extra_data: bool = False, time_step: float = 0.0) -> List[TrajectoryData]:
        ...


def create_trajectory_row(time: float, range_vector: Vector, velocity_vector: Vector,
                          velocity: float, mach: float, spin_drift: float, look_angle: float,
                          density_factor: float, drag: float, weight: float,
                          flag: Union[TrajFlag, int]) -> TrajectoryData:
    """
    Create a TrajectoryData object representing a single row of trajectory data.

    :param time: Time of flight.
    :param range_vector: Position vector.
    :param velocity_vector: Velocity vector.
    :param velocity: Velocity magnitude.
    :param mach: Mach number.
    :param spin_drift: Spin drift value.
    :param look_angle: Look angle value.
    :param density_factor: Density factor.
    :param drag: Drag value.
    :param weight: Weight value.
    :param flag: Flag value.

    :return: A TrajectoryData object representing the trajectory data.
    """
    windage = range_vector.z + spin_drift
    drop_adjustment = get_correction(range_vector.x, range_vector.y)
    windage_adjustment = get_correction(range_vector.x, windage)
    trajectory_angle = math.atan2(velocity_vector.y, velocity_vector.x)

    return TrajectoryData(
        time=time,
        distance=Distance.Foot(range_vector.x),
        velocity=Velocity.FPS(velocity),
        mach=velocity / mach,
        height=Distance.Foot(range_vector.y),
        target_drop=Distance.Foot((range_vector.y - range_vector.x * math.tan(look_angle)) * math.cos(look_angle)),
        drop_adj=Angular.Radian(drop_adjustment - (look_angle if range_vector.x else 0)),
        windage=Distance.Foot(windage),
        windage_adj=Angular.Radian(windage_adjustment),
        look_distance=Distance.Foot(range_vector.x / math.cos(look_angle)),
        angle=Angular.Radian(trajectory_angle),
        density_factor=density_factor - 1,
        drag=drag,
        energy=Energy.FootPound(calculate_energy(weight, velocity)),
        ogw=Weight.Pound(calculate_ogw(weight, velocity)),
        flag=flag
    )


def get_correction(distance: float, offset: float) -> float:
    """:return: Sight adjustment in radians"""
    if distance != 0:
        return math.atan(offset / distance)
    return 0  # None


def calculate_energy(bullet_weight: float, velocity: float) -> float:
    """:return: energy in ft-lbs"""
    return bullet_weight * math.pow(velocity, 2) / 450400


def calculate_ogw(bullet_weight: float, velocity: float) -> float:
    """:return: Optimal Game Weight in pounds"""
    return math.pow(bullet_weight, 2) * math.pow(velocity, 3) * 1.5e-12
