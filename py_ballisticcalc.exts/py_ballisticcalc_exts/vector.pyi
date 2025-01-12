from dataclasses import dataclass
from typing_extensions import Union

__all__ = ['Vector']


@dataclass
class Vector:
    x: float
    y: float
    z: float
    def magnitude(self) -> float: ...
    def mul_by_const(self, a: float) -> Vector: ...
    def mul_by_vector(self, b: Vector) -> float: ...
    def add(self, b: Vector) -> Vector: ...
    def subtract(self, b: Vector) -> Vector: ...
    def negate(self) -> Vector: ...
    def normalize(self) -> Vector: ...
    def __add__(self, other: Vector) -> Vector: ...
    def __radd__(self, other: Vector) -> Vector: ...
    def __iadd__(self, other: Vector) -> Vector: ...
    def __sub__(self, other: Vector) -> Vector: ...
    def __rsub__(self, other: Vector) -> Vector: ...
    def __isub__(self, other: Vector) -> Vector: ...
    def __mul__(self, other: Union[int, float, 'Vector']) -> Union[float, 'Vector']: ...
    def __rmul__(self, other: Union[int, float, 'Vector']) -> Union[float, 'Vector']: ...
    def __imul__(self, other: Union[int, float, 'Vector']) -> Union[float, 'Vector']: ...
    def __neg__(self) -> Vector: ...
    def __init__(self, x: float, y: float, z: float) -> None: ...