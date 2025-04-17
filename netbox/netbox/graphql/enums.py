import strawberry

from netbox.choices import *

__all__ = (
    'ColorEnum',
    'DistanceUnitEnum',
    'WeightUnitEnum',
)

ColorEnum = strawberry.enum(ColorChoices.as_enum(prefix='color'))
DistanceUnitEnum = strawberry.enum(DistanceUnitChoices.as_enum())
WeightUnitEnum = strawberry.enum(WeightUnitChoices.as_enum())
