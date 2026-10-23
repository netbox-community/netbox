import re
from typing import NewType

import strawberry
from graphql import GraphQLError

BigInt = NewType('BigInt', int)

BIGINT_MIN = -2**63
BIGINT_MAX = 2**63 - 1


def parse_bigint(value):
    """
    Coerce an input value to a signed 64-bit integer. Numeric strings are accepted as well as integers, since many
    JSON clients cannot represent integers beyond 2^53 as numbers.
    """
    if isinstance(value, str) and re.fullmatch(r'-?[0-9]+', value):
        value = int(value)
    elif isinstance(value, float) and value.is_integer():
        value = int(value)
    if type(value) is not int:
        raise GraphQLError(f'BigInt cannot represent non-integer value: {value!r}')
    if not BIGINT_MIN <= value <= BIGINT_MAX:
        raise GraphQLError(f'BigInt cannot represent non 64-bit signed integer value: {value!r}')
    return value


BigIntScalar = strawberry.scalar(
    name='BigInt',
    serialize=lambda v: int(v),
    parse_value=parse_bigint,
    description='BigInt field',
)
