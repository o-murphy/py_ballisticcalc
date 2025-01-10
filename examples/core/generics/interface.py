from dataclasses import dataclass, field
from typing import Type, TypeVar, List, Union

# Define a generic type variable T, bound to BaseEngine
TEngine = TypeVar('TEngine', bound='BaseEngine')


@dataclass
class Interface:
    _engine: Type[TEngine]  # This is the type of the engine class (e.g., ConcreteEngine)
    _instance: TEngine = field(default=None, init=False)

    @property
    def cdm(self) -> List['DragDataPoint']:
        """returns custom drag function based on input data"""
        return self._instance.table_data

    def barrel_elevation_for_target(self, shot: 'Shot', target_distance: Union[float, 'Distance']) -> 'Angular':
        ...

    def set_weapon_zero(self, shot: 'Shot', zero_distance: Union[float, 'Distance']) -> 'Angular':
        ...

    def fire(self, shot: 'Shot', trajectory_range: Union[float, 'Distance'],
             trajectory_step: Union[float, 'Distance'] = 0,
             extra_data: bool = False,
             time_step: float = 0.0) -> 'HitResult':
        ...
