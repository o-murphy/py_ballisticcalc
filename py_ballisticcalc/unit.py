"""
Useful types for prefer_units of measurement conversion for ballistics calculations
"""
import os
import sys
from abc import ABC
from dataclasses import dataclass, MISSING, Field, fields
from enum import IntEnum
from math import pi, atan, tan
from typing import NamedTuple, Union

from py_ballisticcalc.logger import logger

try:
    import tomllib as tomllib
except ImportError:
    import tomli as tomllib

__all__ = ('Unit', 'AbstractUnit', 'UnitProps', 'UnitPropsDict', 'Distance',
           'Velocity', 'Angular', 'Temperature', 'Pressure',
           'Energy', 'Weight', 'Dimension', 'PreferredUnits', 'basicConfig')


# pylint: disable=invalid-name
class Unit(IntEnum):
    """
    Usage of IntEnum simplify data serializing for using it with databases etc.
    """
    Radian = 0
    Degree = 1
    MOA = 2
    Mil = 3
    MRad = 4
    Thousandth = 5
    InchesPer100Yd = 6
    CmPer100M = 7
    OClock = 8

    Inch = 10
    Foot = 11
    Yard = 12
    Mile = 13
    NauticalMile = 14
    Millimeter = 15
    Centimeter = 16
    Meter = 17
    Kilometer = 18
    Line = 19

    FootPound = 30
    Joule = 31

    MmHg = 40
    InHg = 41
    Bar = 42
    hPa = 43
    PSI = 44

    Fahrenheit = 50
    Celsius = 51
    Kelvin = 52
    Rankin = 53

    MPS = 60
    KMH = 61
    FPS = 62
    MPH = 63
    KT = 64

    Grain = 70
    Ounce = 71
    Gram = 72
    Pound = 73
    Kilgram = 74
    Newton = 75

    @property
    def key(self) -> str:
        """
        :return: readable name of the unit of measure
        """
        return UnitPropsDict[self].name

    @property
    def accuracy(self) -> int:
        """
        :return: default accuracy of the unit of measure
        """
        return UnitPropsDict[self].accuracy

    @property
    def symbol(self) -> str:
        """
        :return: short symbol of the unit of measure in CI
        """
        return UnitPropsDict[self].symbol

    def __repr__(self) -> str:
        return UnitPropsDict[self].name

    def __call__(self: 'Unit', value: [int, float, 'AbstractUnit'] = None) -> 'AbstractUnit':
        """Creates new unit instance by dot syntax
        :param self: unit as Unit enum
        :param value: numeric value of the unit
        :return: AbstractUnit instance
        """

        # if value is None:
        #     return self

        if isinstance(value, AbstractUnit):
            return value << self
        if 0 <= self < 10:
            obj = Angular(value, self)
        elif 10 <= self < 20:
            obj = Distance(value, self)
        elif 30 <= self < 40:
            obj = Energy(value, self)
        elif 40 <= self < 50:
            obj = Pressure(value, self)
        elif 50 <= self < 60:
            obj = Temperature(value, self)
        elif 60 <= self < 70:
            obj = Velocity(value, self)
        elif 70 <= self < 80:
            obj = Weight(value, self)
        else:
            raise TypeError(f"{self} Unit is not supported")
        return obj


class UnitProps(NamedTuple):
    """Properties of unit measure"""
    name: str
    accuracy: int
    symbol: str


UnitPropsDict = {
    Unit.Radian: UnitProps('radian', 6, 'rad'),
    Unit.Degree: UnitProps('degree', 4, '°'),
    Unit.MOA: UnitProps('MOA', 2, 'MOA'),
    Unit.Mil: UnitProps('mil', 2, 'mil'),
    Unit.MRad: UnitProps('mrad', 2, 'mrad'),
    Unit.Thousandth: UnitProps('thousandth', 2, 'ths'),
    Unit.InchesPer100Yd: UnitProps('inch/100yd', 2, 'in/100yd'),
    Unit.CmPer100M: UnitProps('cm/100m', 2, 'cm/100m'),
    Unit.OClock: UnitProps('hour', 2, 'h'),

    Unit.Inch: UnitProps("inch", 1, "inch"),
    Unit.Foot: UnitProps("foot", 2, "ft"),
    Unit.Yard: UnitProps("yard", 1, "yd"),
    Unit.Mile: UnitProps("mile", 3, "mi"),
    Unit.NauticalMile: UnitProps("nautical mile", 3, "nm"),
    Unit.Millimeter: UnitProps("millimeter", 3, "mm"),
    Unit.Centimeter: UnitProps("centimeter", 3, "cm"),
    Unit.Meter: UnitProps("meter", 1, "m"),
    Unit.Kilometer: UnitProps("kilometer", 3, "km"),
    Unit.Line: UnitProps("line", 3, "ln"),

    Unit.FootPound: UnitProps('foot-pound', 0, 'ft·lb'),
    Unit.Joule: UnitProps('joule', 0, 'J'),

    Unit.MmHg: UnitProps('mmHg', 0, 'mmHg'),
    Unit.InHg: UnitProps('inHg', 6, 'inHg'),
    Unit.Bar: UnitProps('bar', 2, 'bar'),
    Unit.hPa: UnitProps('hPa', 4, 'hPa'),
    Unit.PSI: UnitProps('psi', 4, 'psi'),

    Unit.Fahrenheit: UnitProps('fahrenheit', 1, '°F'),
    Unit.Celsius: UnitProps('celsius', 1, '°C'),
    Unit.Kelvin: UnitProps('kelvin', 1, '°K'),
    Unit.Rankin: UnitProps('rankin', 1, '°R'),

    Unit.MPS: UnitProps('mps', 0, 'm/s'),
    Unit.KMH: UnitProps('kmh', 1, 'km/h'),
    Unit.FPS: UnitProps('fps', 1, 'ft/s'),
    Unit.MPH: UnitProps('mph', 1, 'mph'),
    Unit.KT: UnitProps('knot', 1, 'kt'),

    Unit.Grain: UnitProps('grain', 1, 'gr'),
    Unit.Ounce: UnitProps('ounce', 1, 'oz'),
    Unit.Gram: UnitProps('gram', 1, 'g'),
    Unit.Pound: UnitProps('pound', 0, 'lb'),
    Unit.Kilgram: UnitProps('kilogram', 3, 'kg'),
    Unit.Newton: UnitProps('newton', 3, 'N'),
}


class AbstractUnit:
    """Abstract class for unit of measure instance definition
    Stores defined unit and value, applies conversions to other prefer_units
    """
    __slots__ = ('_value', '_defined_units')

    def __init__(self, value: [float, int], units: Unit):
        """
        :param units: unit as Unit enum
        :param value: numeric value of the unit
        """
        self._value: float = self.to_raw(value, units)
        self._defined_units: Unit = units

    def __str__(self) -> str:
        """
        :return: readable unit value
        """
        units = self._defined_units
        props = UnitPropsDict[units]
        v = self.from_raw(self._value, units)
        return f'{round(v, props.accuracy)}{props.symbol}'

    def __repr__(self) -> str:
        """
        :return: instance as readable view
        """
        return f'<{self.__class__.__name__}: {self << self.units} ({round(self._value, 4)})>'

    def __float__(self):
        return float(self._value)

    def __eq__(self, other):
        return float(self) == other

    def __lt__(self, other):
        return float(self) < other

    def __gt__(self, other):
        return float(self) > other

    def __le__(self, other):
        return float(self) <= other

    def __ge__(self, other):
        return float(self) >= other

    def __lshift__(self, other: Unit):
        return self.convert(other)

    def __rshift__(self, other: Unit):
        return self.get_in(other)

    def __rlshift__(self, other: Unit):
        return self.convert(other)

    def _unit_support_error(self, value: float, units: Unit):
        """Validates the prefer_units
        :param value: value of the unit
        :param units: Unit enum type
        :return: value in specified prefer_units
        """
        if not isinstance(units, Unit):
            err_msg = f"Type expected: {Unit}, {type(Unit).__name__} " \
                      f"found: {type(units).__name__} ({value})"
            raise TypeError(err_msg)
        if units not in self.__dict__.values():
            raise ValueError(f'{self.__class__.__name__}: unit {units} is not supported')
        return 0

    def to_raw(self, value: float, units: Unit) -> float:
        """Converts value with specified prefer_units to raw value
        :param value: value of the unit
        :param units: Unit enum type
        :return: value in specified prefer_units
        """
        return self._unit_support_error(value, units)

    def from_raw(self, value: float, units: Unit) -> float:
        """Converts raw value to specified prefer_units
        :param value: raw value of the unit
        :param units: Unit enum type
        :return: value in specified prefer_units
        """
        return self._unit_support_error(value, units)

    def convert(self, units: Unit) -> 'AbstractUnit':
        """Returns new unit instance in specified prefer_units
        :param units: Unit enum type
        :return: new unit instance in specified prefer_units
        """
        value = self.get_in(units)
        return self.__class__(value, units)

    def get_in(self, units: Unit) -> float:
        """
        :param units: Unit enum type
        :return: value in specified prefer_units
        """
        return self.from_raw(self._value, units)

    @property
    def units(self) -> Unit:
        """
        :return: defined prefer_units
        """
        return self._defined_units

    @property
    def unit_value(self) -> float:
        """Returns float value in defined prefer_units"""
        return self.get_in(self.units)

    @property
    def raw_value(self) -> float:
        """Raw unit value getter
        :return: raw unit value
        """
        return self._value


class Distance(AbstractUnit):
    """Distance unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Distance.Inch:
            return value
        if units == Distance.Foot:
            result = value * 12
        elif units == Distance.Yard:
            result = value * 36
        elif units == Distance.Mile:
            result = value * 63360
        elif units == Distance.NauticalMile:
            result = value * 72913.3858
        elif units == Distance.Line:
            result = value / 10
        elif units == Distance.Millimeter:
            result = value / 25.4
        elif units == Distance.Centimeter:
            result = value / 2.54
        elif units == Distance.Meter:
            result = value / 25.4 * 1000
        elif units == Distance.Kilometer:
            result = value / 25.4 * 1000000
        else:
            return super().to_raw(value, units)
        return result

    def from_raw(self, value: float, units: Unit):
        if units == Distance.Inch:
            return value
        if units == Distance.Foot:
            result = value / 12
        elif units == Distance.Yard:
            result = value / 36
        elif units == Distance.Mile:
            result = value / 63360
        elif units == Distance.NauticalMile:
            result = value / 72913.3858
        elif units == Distance.Line:
            result = value * 10
        elif units == Distance.Millimeter:
            result = value * 25.4
        elif units == Distance.Centimeter:
            result = value * 2.54
        elif units == Distance.Meter:
            result = value * 25.4 / 1000
        elif units == Distance.Kilometer:
            result = value * 25.4 / 1000000
        else:
            return super().from_raw(value, units)
        return result

    Inch = Unit.Inch
    Foot = Unit.Foot
    Yard = Unit.Yard
    Mile = Unit.Mile
    NauticalMile = Unit.NauticalMile
    Millimeter = Unit.Millimeter
    Centimeter = Unit.Centimeter
    Meter = Unit.Meter
    Kilometer = Unit.Kilometer
    Line = Unit.Line


class Pressure(AbstractUnit):
    """Pressure unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Pressure.MmHg:
            return value
        if units == Pressure.InHg:
            result = value * 25.4
        elif units == Pressure.Bar:
            result = value * 750.061683
        elif units == Pressure.hPa:
            result = value * 750.061683 / 1000
        elif units == Pressure.PSI:
            result = value * 51.714924102396
        else:
            return super().to_raw(value, units)
        return result

    def from_raw(self, value: float, units: Unit):
        if units == Pressure.MmHg:
            return value
        if units == Pressure.InHg:
            result = value / 25.4
        elif units == Pressure.Bar:
            result = value / 750.061683
        elif units == Pressure.hPa:
            result = value / 750.061683 * 1000
        elif units == Pressure.PSI:
            result = value / 51.714924102396
        else:
            return super().from_raw(value, units)
        return result

    MmHg = Unit.MmHg
    InHg = Unit.InHg
    Bar = Unit.Bar
    hPa = Unit.hPa
    PSI = Unit.PSI


class Weight(AbstractUnit):
    """Weight unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Weight.Grain:
            return value
        if units == Weight.Gram:
            result = value * 15.4323584
        elif units == Weight.Kilogram:
            result = value * 15432.3584
        elif units == Weight.Newton:
            result = value * 151339.73750336
        elif units == Weight.Pound:
            result = value / 0.000142857143
        elif units == Weight.Ounce:
            result = value * 437.5
        else:
            return super().to_raw(value, units)
        return result

    def from_raw(self, value: float, units: Unit):
        if units == Weight.Grain:
            return value
        if units == Weight.Gram:
            result = value / 15.4323584
        elif units == Weight.Kilogram:
            result = value / 15432.3584
        elif units == Weight.Newton:
            result = value / 151339.73750336
        elif units == Weight.Pound:
            result = value * 0.000142857143
        elif units == Weight.Ounce:
            result = value / 437.5
        else:
            return super().from_raw(value, units)
        return result

    Grain = Unit.Grain
    Ounce = Unit.Ounce
    Gram = Unit.Gram
    Pound = Unit.Pound
    Kilogram = Unit.Kilgram
    Newton = Unit.Newton


class Temperature(AbstractUnit):
    """Temperature unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Temperature.Fahrenheit:
            return value
        if units == Temperature.Rankin:
            result = value - 459.67
        elif units == Temperature.Celsius:
            result = value * 9 / 5 + 32
        elif units == Temperature.Kelvin:
            result = (value - 273.15) * 9 / 5 + 32
        else:
            return super().to_raw(value, units)
        return result

    def from_raw(self, value: float, units: Unit):
        if units == Temperature.Fahrenheit:
            return value
        if units == Temperature.Rankin:
            result = value + 459.67
        elif units == Temperature.Celsius:
            result = (value - 32) * 5 / 9
        elif units == Temperature.Kelvin:
            result = (value - 32) * 5 / 9 + 273.15
        else:
            return super().from_raw(value, units)
        return result

    Fahrenheit = Unit.Fahrenheit
    Celsius = Unit.Celsius
    Kelvin = Unit.Kelvin
    Rankin = Unit.Rankin


class Angular(AbstractUnit):
    """Angular unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Angular.Radian:
            return value
        if units == Angular.Degree:
            result = value / 180 * pi
        elif units == Angular.MOA:
            result = value / 180 * pi / 60
        elif units == Angular.Mil:
            result = value / 3200 * pi
        elif units == Angular.MRad:
            result = value / 1000
        elif units == Angular.Thousandth:
            result = value / 3000 * pi
        elif units == Angular.InchesPer100Yd:
            result = atan(value / 3600)
        elif units == Angular.CmPer100M:
            result = atan(value / 10000)
        elif units == Angular.OClock:
            result = value / 6 * pi
        else:
            return super().to_raw(value, units)
        if result > 2 * pi:
            result = result % (2 * pi)
        return result

    def from_raw(self, value: float, units: Unit):
        if units == Angular.Radian:
            return value
        if units == Angular.Degree:
            result = value * 180 / pi
        elif units == Angular.MOA:
            result = value * 180 / pi * 60
        elif units == Angular.Mil:
            result = value * 3200 / pi
        elif units == Angular.MRad:
            result = value * 1000
        elif units == Angular.Thousandth:
            result = value * 3000 / pi
        elif units == Angular.InchesPer100Yd:
            result = tan(value) * 3600
        elif units == Angular.CmPer100M:
            result = tan(value) * 10000
        elif units == Angular.OClock:
            result = value * 6 / pi
        else:
            return super().from_raw(value, units)
        return result

    Radian = Unit.Radian
    Degree = Unit.Degree
    MOA = Unit.MOA
    Mil = Unit.Mil
    MRad = Unit.MRad
    Thousandth = Unit.Thousandth
    InchesPer100Yd = Unit.InchesPer100Yd
    CmPer100M = Unit.CmPer100M
    OClock = Unit.OClock


class Velocity(AbstractUnit):
    """Velocity unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Velocity.MPS:
            return value
        if units == Velocity.KMH:
            return value / 3.6
        if units == Velocity.FPS:
            return value / 3.2808399
        if units == Velocity.MPH:
            return value / 2.23693629
        if units == Velocity.KT:
            return value / 1.94384449
        return super().to_raw(value, units)

    def from_raw(self, value: float, units: Unit):
        if units == Velocity.MPS:
            return value
        if units == Velocity.KMH:
            return value * 3.6
        if units == Velocity.FPS:
            return value * 3.2808399
        if units == Velocity.MPH:
            return value * 2.23693629
        if units == Velocity.KT:
            return value * 1.94384449
        return super().from_raw(value, units)

    MPS = Unit.MPS
    KMH = Unit.KMH
    FPS = Unit.FPS
    MPH = Unit.MPH
    KT = Unit.KT


class Energy(AbstractUnit):
    """Energy unit"""

    def to_raw(self, value: float, units: Unit):
        if units == Energy.FootPound:
            return value
        if units == Energy.Joule:
            return value * 0.737562149277
        return super().to_raw(value, units)

    def from_raw(self, value: float, units: Unit):
        if units == Energy.FootPound:
            return value
        if units == Energy.Joule:
            return value / 0.737562149277
        return super().from_raw(value, units)

    FootPound = Unit.FootPound
    Joule = Unit.Joule


class PreferredUnitsMeta(type):
    """Provide representation method for static dataclasses."""

    def __repr__(cls):
        return '\n'.join(f'{field.name} = {getattr(cls, field.name)!r}'
                         for field in fields(cls))


@dataclass
class PreferredUnits(metaclass=PreferredUnitsMeta):  # pylint: disable=too-many-instance-attributes
    """Default prefer_units for specified measures"""

    angular: Unit = Unit.Degree
    distance: Unit = Unit.Yard
    velocity: Unit = Unit.FPS
    pressure: Unit = Unit.InHg
    temperature: Unit = Unit.Fahrenheit
    diameter: Unit = Unit.Inch
    length: Unit = Unit.Inch
    weight: Unit = Unit.Grain
    adjustment: Unit = Unit.Mil
    drop: Unit = Unit.Inch
    energy: Unit = Unit.FootPound
    ogw: Unit = Unit.Pound
    sight_height: Unit = Unit.Inch
    target_height: Unit = Unit.Inch
    twist: Unit = Unit.Inch

    @dataclass
    class Mixine(ABC):  # pylint: disable=too-few-public-methods
        """
        TODO: move it to Units, use it instead of TypedUnits
        Abstract class to apply auto-conversion values to
        specified prefer_units by type-hints in inherited dataclasses
        """

        def __setattr__(self, key, value):
            """
            converts value to specified prefer_units by type-hints in inherited dataclass
            """

            _fields = self.__getattribute__('__dataclass_fields__')

            if (_field := _fields.get(key)) and value is not None and not isinstance(value, AbstractUnit):

                if units := _field.metadata.get('prefer_units'):

                    if isinstance(units, Unit):
                        value = units(value)
                    elif isinstance(units, str):
                        value = PreferredUnits.__dict__[units](value)
                    else:
                        raise TypeError(f"Unsupported unit or dimension use one of {PreferredUnits}")

            super().__setattr__(key, value)

    @classmethod
    def _load_preferred_units(cls, **kwargs):
        for key, value in kwargs.items():
            try:
                if hasattr(PreferredUnits, key):
                    setattr(PreferredUnits, key, Unit[value])
                else:
                    logger.warning(f"attribute {key} not found in preferred_units")
            except KeyError:
                logger.warning(f"{value=} not found in preferred_units")

    @classmethod
    def _load_config(cls, filepath=None):

        def find_pybc_toml(start_dir=os.path.dirname(__file__)):
            """
            Search for the pyproject.toml file starting from the specified directory.
            :param start_dir: (str) The directory to start searching from. Default is the current working directory.
            :return: str: The absolute path to the pyproject.toml file if found, otherwise None.
            """
            current_dir = os.path.abspath(start_dir)
            while True:
                # Check if pybc.toml or .pybc.toml exists in the current directory
                pybc_paths = [
                    os.path.join(current_dir, '.pybc.toml'),
                    os.path.join(current_dir, 'pybc.toml'),
                ]
                for pypc_path in pybc_paths:
                    if os.path.exists(pypc_path):
                        return os.path.abspath(pypc_path)

                # Move to the parent directory
                parent_dir = os.path.dirname(current_dir)

                # If we have reached the root directory, stop searching
                if parent_dir == current_dir:
                    return None

                current_dir = parent_dir

        if filepath is None:
            filepath = find_pybc_toml()

        with open(filepath, "rb") as fp:
            _config = tomllib.load(fp)

            if _pybc := _config.get('pybc'):
                if preferred_units := _pybc.get('preferred_units'):
                    cls._load_preferred_units(**preferred_units)
                else:
                    logger.warning("Config has not `pybc.preferred_units` section")
            else:
                logger.warning("Config has not `pybc` section")

    @classmethod
    def basic_config(cls, filename=None, **preferred_units):

        if filename and preferred_units:
            raise ValueError("Can't use preferred_units and config file at same time")
        elif preferred_units:
            cls._load_preferred_units(**preferred_units)
        else:
            # trying to load definitions from pybc.toml
            cls._load_config(filename)



# pylint: disable=redefined-builtin,too-few-public-methods,too-many-arguments
class Dimension(Field):
    """
    Definition of measure units specified field for
    PreferredUnits.Mixine based dataclasses
    """

    def __init__(self, prefer_units: Union[str, Unit], init=True, repr=True,
                 hash=None, compare=True, metadata=None):
        if metadata is None:
            metadata = {}
        metadata['prefer_units'] = prefer_units

        major, minor = sys.version_info.major, sys.version_info.minor

        if major >= 3 and minor > 9:
            extra = {'kw_only': MISSING}
        elif major >= 3 and minor == 9:
            extra = {}
        else:
            raise RuntimeError("Unsupported python version")

        super().__init__(default=None, default_factory=MISSING,
                         init=init, repr=repr,
                         hash=hash, compare=compare,
                         metadata=metadata, **extra)


PreferredUnits.basic_config()  # init PrefferedUnits

basicConfig = PreferredUnits.basic_config
