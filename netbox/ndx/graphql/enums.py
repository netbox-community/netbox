import strawberry

from ndx.choices import *

__all__ = (
    'ImportRecordSourceEnum',
)

ImportRecordSourceEnum = strawberry.enum(ImportRecordSourceChoices.as_enum(prefix='source'))
