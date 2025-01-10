from typing_extensions import List

from engine import Interface, BaseEngine
from py_ballisticcalc import *


class Euler(BaseEngine):

    class EulerConfig(BaseEngine.BaseEngineConfig):
        use_powder_sensitivity: bool = False


    def zero_angle(self, shot_info: Shot, distance: Distance) -> Angular:
        ...

    def trajectory(self, shot_info: Shot, max_range: Distance, dist_step: Distance,
                   extra_data: bool = False, time_step: float = 0.0) -> List[TrajectoryData]:
        ...


if __name__ == "__main__":
    weapon = Weapon(sight_height=Unit.Centimeter(9), twist=10)
    dm = DragModel(0.381, TableG7, 300, 0.338, 1.8)
    ammo = Ammo(dm=dm, mv=Unit.MPS(815), powder_temp=Temperature.Celsius(0), temp_modifier=0.0123)

    i = Interface(_engine=Euler, _config=Euler.EulerConfig.from_dict({}))
    print(i)
    t = i.fire(shot=Shot(weapon, ammo), trajectory_range=Distance.Meter(100))
    print(t)
