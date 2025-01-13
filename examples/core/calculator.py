"""
Calculator implements generics.Interface to make it universal
It can be used with different implementations of engines (Calculation methods)
Custom engine should be a subclass of BaseEngine
It uses MethodEulerEngine by default if no other engine chosen yet
"""

from dataclasses import dataclass

from typing_extensions import Generic, List, Union

from examples.core.generics.interface import Interface, TEngine, TConfigDict
from examples.core.method_euler import MethodEulerEngine
from py_ballisticcalc import *


@dataclass
class Calculator(Interface[TEngine, TConfigDict], Generic[TEngine, TConfigDict]):
    # _engine: TEngine = field(default=None)  # Not need cause defined in Type[Interface]

    def __post_init__(self):
        if self._engine is None:
            self._engine = MethodEulerEngine()

    def reload(self, ammo: Ammo, engine: TEngine = None, config: TConfigDict = None) -> None:
        if engine:
            self._engine = engine(config)
        elif config:
            self._engine = self._engine.__class__(config)
        self._engine.reload(ammo)

    @property
    def cdm(self) -> List[DragDataPoint]:
        return self._engine.table_data

    def barrel_elevation_for_target(self, shot: Shot, target_distance: Union[float, Distance]) -> Angular:
        self._engine.reload(shot.ammo, config=self._engine._config)
        target_distance = PreferredUnits.distance(target_distance)
        total_elevation = self._engine.zero_angle(shot, target_distance)
        return Angular.Radian(
            (total_elevation >> Angular.Radian) - (shot.look_angle >> Angular.Radian)
        )

    def set_weapon_zero(self, shot: Shot, zero_distance: Union[float, Distance]) -> Angular:
        shot.weapon.zero_elevation = self.barrel_elevation_for_target(shot, zero_distance)
        return shot.weapon.zero_elevation

    def fire(self, shot: Shot, trajectory_range: Union[float, Distance],
             trajectory_step: Union[float, Distance] = 0,
             extra_data: bool = False,
             time_step: float = 0.0) -> HitResult:
        trajectory_range = PreferredUnits.distance(trajectory_range)
        if not trajectory_step:
            trajectory_step = trajectory_range.unit_value / 10.0
        step: Distance = PreferredUnits.distance(trajectory_step)
        self._engine.reload(shot.ammo, config=self._engine._config)
        data = self._engine.trajectory(shot, trajectory_range, step, extra_data, time_step)
        return HitResult(shot, data, extra_data)

# """
# Other approach to create custom interface
# custom_interface = Interface[CustomEngine, CustomConfig](
#     _engine=CustomEngine,
#     _config={"param1": 100, "param2": "test"}  # This must match CustomConfig
# )
# """
