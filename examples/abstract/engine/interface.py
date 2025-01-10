from dataclasses import dataclass, field
from typing_extensions import Type, TypeVar, List, Union, Optional, Protocol

from .engine import BaseEngine
from py_ballisticcalc import *
from py_ballisticcalc import create_interface_config


# Define a TypeVar for the engine configuration type
T_Config = TypeVar("T_Config", bound=BaseEngine.BaseEngineConfig)


class BaseInterfaceConfig(Protocol):
    """Protocol for engine configuration with a flexible type."""
    _config: Optional[InterfaceConfigDict] = None

    @classmethod
    def from_dict(cls, data: InterfaceConfigDict) -> T_Config:
        """Convert dictionary to config."""
        raise NotImplementedError("Must implement from_dict method.")


@dataclass
class Interface:
    """Basic interface for the ballistics calculator"""

    _config: Optional[InterfaceConfigDict] = field(default=None)
    _engine: Type[BaseEngine] = field(init=True, default=None, compare=False)
    _calc: BaseEngine = field(init=False, repr=False, compare=False)

    def __post_init__(self):
        if self._engine is None:
            self._engine = BaseEngine

    @property
    def cdm(self) -> List[DragDataPoint]:
        """Returns custom drag function based on input data"""
        return self._calc.table_data

    def barrel_elevation_for_target(self, shot: Shot, target_distance: Union[float, Distance]) -> Angular:
        """Calculates barrel elevation to hit target at zero_distance."""
        self._calc = self._engine(shot.ammo, create_interface_config(self._config))
        target_distance = PreferredUnits.distance(target_distance)
        total_elevation = self._engine.zero_angle(shot, target_distance)
        return Angular.Radian(
            (total_elevation >> Angular.Radian) - (shot.look_angle >> Angular.Radian)
        )

    def set_weapon_zero(self, shot: Shot, zero_distance: Union[float, Distance]) -> Angular:
        """Sets shot.weapon.zero_elevation so that it hits a target at zero_distance."""
        shot.weapon.zero_elevation = self.barrel_elevation_for_target(shot, zero_distance)
        return shot.weapon.zero_elevation

    def fire(self, shot: Shot, trajectory_range: Union[float, Distance],
             trajectory_step: Union[float, Distance] = 0,
             extra_data: bool = False,
             time_step: float = 0.0) -> HitResult:
        """Calculates trajectory."""
        trajectory_range = PreferredUnits.distance(trajectory_range)
        if not trajectory_step:
            trajectory_step = trajectory_range.unit_value / 10.0
        step: Distance = PreferredUnits.distance(trajectory_step)
        self._calc = self._engine(shot.ammo, create_interface_config(self._config))
        data = self._calc.trajectory(shot, trajectory_range, step, extra_data, time_step)
        return HitResult(shot, data, extra_data)
