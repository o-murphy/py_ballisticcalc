from typing_extensions import Generic, TypeVar, Annotated, get_args, get_origin, Union, Literal

from py_ballisticcalc import *

T = TypeVar('T')


def is_union(annotation):
    origin = get_origin(annotation)
    if origin is Union:
        args = get_args(annotation)
        if type(None) in args:
            return args
    return None


class _PydanticUnit(Generic[T]):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, values, config, field):
        annotation = field.annotation

        args = is_union(annotation)
        if args:
            annotation = args[0]

        if get_origin(annotation) is Annotated:
            base_type, pref = get_args(annotation)

            if isinstance(pref, Unit):
                return pref(value)

            if not issubclass(cls, base_type):
                raise TypeError('Not a Unit')

            if isinstance(pref, str) and getattr(PreferredUnits, pref):
                return getattr(
                    PreferredUnits, pref)(value)

        return value


PreferredUnitKey = Literal[
    'distance',
    'angular',
    'velocity',
    'drop',
    'adjustment',
    'sight_height',
    'weight',
    'diameter',
    'length',
    'ogw',
    'temperature',
    'pressure',
    'twist',
]


def conu(preferred: Union[Unit, PreferredUnitKey]):
    return Annotated[_PydanticUnit, preferred]
