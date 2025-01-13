from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from typing_extensions import TypedDict, List

from py_ballisticcalc import *  # Assuming this contains Shot, Distance, TrajectoryData, Angular


# Define a base configuration type
class BaseConfig(TypedDict, total=False):
    pass  # Base class for all configurations


# Define engines and their configurations as `TypeVar` pairs
TConfigDict = TypeVar("TConfigDict", bound=BaseConfig)


# Base engine class
class BaseEngine(ABC, Generic[TConfigDict]):
    _config: TConfigDict
    _table_data: List[DragDataPoint]

    @abstractmethod
    def __init__(self, config: Optional[TConfigDict] = None) -> None:
        """Load config"""
        pass

    @abstractmethod
    def reload(self, ammo: Ammo, config: Optional[TConfigDict] = None) -> None:
        """Method to init ammo"""
        pass

    @property
    @abstractmethod
    def table_data(self) -> List[DragDataPoint]:
        """:return: List[DragDataPoint]"""
        return self._table_data

    @abstractmethod
    def zero_angle(self, shot_info: Shot, distance: Distance) -> Angular:
        pass

    @abstractmethod
    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance,
                   extra_data: bool = False, time_step: float = 0.0) -> List[TrajectoryData]:
        pass
