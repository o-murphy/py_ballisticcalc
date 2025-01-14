from pydantic import BaseModel, root_validator, confloat, ConfigDict
from typing_extensions import Optional

from py_ballisticcalc import *
from py_ballisticcalc.drag_model import DragTableDataType
from pybc_pydantic.unit import conu


# PydanticWind model with Annotated metadata
class PydanticWind(BaseModel):
    MAX_DISTANCE_FEET: Optional[confloat(ge=0.0)] = 1e8
    velocity: Optional[conu("velocity")] = Unit.FPS(0)
    direction_from: Optional[conu(Unit.Radian)] = Unit.Radian(0)
    until_distance: Optional[conu("distance")] = None

    @root_validator(allow_reuse=True)
    def model_validate(cls, values):
        values['MAX_DISTANCE_FEET'] = values.get('MAX_DISTANCE_FEET', 1e8)
        values['until_distance'] = values.get('until_distance', Unit.Foot(values['MAX_DISTANCE_FEET']))
        return values

    def to_obj(self):
        args = self.dict()
        args['max_distance_feet'] = args.pop('MAX_DISTANCE_FEET')
        fields = Wind.__init__.__annotations__
        known_args = {k: v for k, v in args.items() if k in fields}
        return Wind(**known_args)


class PydanticAtmo(BaseModel):
    altitude: Optional[conu("distance")]
    pressure: Optional[conu("pressure")] = None
    temperature: Optional[conu("temperature")] = None
    humidity: Optional[confloat(ge=0.0, le=100.0)] = 0.0

    def to_obj(self):
        args = self.dict()
        fields = Atmo.__init__.__annotations__
        known_args = {k: v for k, v in args.items() if k in fields}
        return Atmo(**known_args)


class PydanticDragModel(BaseModel):
    bc: confloat(ge=0.0)
    drag_table: DragTableDataType
    weight: conu("weight") = Unit.Grain(0)
    diameter: conu("diameter") = Unit.Inch(0)
    length: conu("length") = Unit.Inch(0)

    def to_obj(self):
        args = self.dict()
        fields = DragModel.__init__.__annotations__
        known_args = {k: v for k, v in args.items() if k in fields}
        return DragModel(**known_args)


class PydanticWeapon(BaseModel):
    sight_height: Optional[conu('sight_height')] = Unit.Inch(0)
    twist: Optional[conu('twist')] = Unit.Inch(0)
    zero_elevation: Optional[conu('angular')] = Unit.Radian(0)

    # sight: Optional[Sight] = None

    def to_obj(self):
        args = self.dict()
        fields = Weapon.__init__.__annotations__
        known_args = {k: v for k, v in args.items() if k in fields}
        return Weapon(**known_args)


class PydanticAmmo(BaseModel):
    dm: PydanticDragModel
    mv: conu('velocity')
    powder_temp: Optional[conu('temperature')] = Temperature.Celsius(15)
    temp_modifier: Optional[confloat(ge=0.0)] = 0

    def to_obj(self):
        args = self.dict()
        args['dm'] = self.dm.to_obj()
        fields = Ammo.__init__.__annotations__
        known_args = {k: v for k, v in args.items() if k in fields}
        return Ammo(**known_args)


class PydanticShot(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    weapon: PydanticWeapon
    ammo: PydanticAmmo
    atmo: PydanticAtmo
    look_angle: Optional[conu("angular")] = Unit.Radian(0)
    relative_angle: Optional[conu("angular")] = Unit.Radian(0)
    cant_angle: Optional[conu("angular")] = Unit.Radian(0)

    def to_obj(self):
        args = self.dict()
        args['weapon'] = self.weapon.to_obj()
        args['ammo'] = self.ammo.to_obj()
        args['atmo'] = self.atmo.to_obj()
        fields = Shot.__init__.__annotations__
        known_args = {k: v for k, v in args.items() if k in fields}
        return Shot(**known_args)


# dm = PydanticDragModel(bc=0.4, drag_table=TableG7)
# w = PydanticWeapon()
# a = PydanticAmmo(dm=dm, mv=800)
# s = PydanticShot(weapon=w, ammo=a)


if __name__ == '__main__':
    PreferredUnits.velocity = Velocity.MPS
    PreferredUnits.adjustment = Angular.Mil
    PreferredUnits.temperature = Temperature.Celsius
    PreferredUnits.distance = Distance.Meter
    PreferredUnits.sight_height = Distance.Centimeter
    PreferredUnits.drop = Distance.Centimeter

    weapon = {'sight_height': Unit.Centimeter(9), 'twist': 10}
    ammo = {
        'dm': {
            'bc': 0.381,
            'drag_table': TableG7,
            'weight': 300,
            'diameter': 0.338,
            'length': 1.7
        },
        'mv': Unit.MPS(815),
        'powder_temp': Temperature.Celsius(0),
        'temp_modifier': 0.0123
    }
    zero = PydanticShot(**{
        'weapon': weapon,
        'ammo': ammo,
        'atmo': {
            'altitude': Unit.Meter(150),
            'pressure': Unit.MmHg(745),
            'temperature': Unit.Celsius(-1),
            'humidity': 78
        },

    }).to_obj()

    zero_distance = Distance.Meter(100)

    config: InterfaceConfigDict = {'use_powder_sensitivity': True}
    calc = Calculator(_config=config)
    zero_elevation = calc.set_weapon_zero(zero, zero_distance)

    shot = PydanticShot(
        **{
            'weapon': {
                **weapon,
                'zero_elevation': zero_elevation
            },
            'ammo': ammo,
            'atmo': {
                'altitude': Unit.Meter(150),
                'pressure': Unit.hPa(992),
                'temperature': Unit.Celsius(23),
                'humidity': 29
            }
        }
    )

    shot_result = calc.fire(shot.to_obj(), Distance.Meter(1000), extra_data=False)

    from examples.ukrop_338lm_300gr_smk import shot_result as reference
    assert shot_result.trajectory[-1] == reference.trajectory[-1]
