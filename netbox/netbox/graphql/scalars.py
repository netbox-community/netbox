from typing import NewType

import strawberry

BigInt = NewType('BigInt', int)

BigIntScalar = strawberry.scalar(
    name='BigInt',
    serialize=lambda v: int(v),
    parse_value=lambda v: str(v),
    description='BigInt field',
)
