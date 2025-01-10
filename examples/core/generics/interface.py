from abc import abstractmethod, ABC

from typing_extensions import TypeVar, Generic, List, Union
from dataclasses import dataclass, field

from examples.core.generics.engine import BaseEngine, TConfigDict
from py_ballisticcalc import *

# Ensure TConfigDict is bound in the Interface class
TEngine = TypeVar("TEngine", bound=BaseEngine)  # Engine type is bound to BaseEngine with TConfigDict


# Interface class that expects an engine and config
@dataclass
class Interface(ABC, Generic[TEngine, TConfigDict]):
    _engine: TEngine = field(default=None)  # The class/type of a BaseEngine subclass

    def __post_init__(self):
        if self._engine is None:
            self._engine = BaseEngine()

    @abstractmethod
    def reload(self, ammo: Ammo) -> None:
        pass

    @property
    def cdm(self) -> List[DragDataPoint]:
        pass

    @abstractmethod
    def barrel_elevation_for_target(self, shot: Shot, target_distance: Union[float, Distance]) -> Angular:
        pass

    @abstractmethod
    def set_weapon_zero(self, shot: Shot, zero_distance: Union[float, Distance]) -> Angular:
        pass

    @abstractmethod
    def fire(self, shot: Shot, trajectory_range: Union[float, Distance],
             trajectory_step: Union[float, Distance] = 0,
             extra_data: bool = False,
             time_step: float = 0.0) -> HitResult:
        pass
