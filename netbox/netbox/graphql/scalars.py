from graphene import Scalar
from graphql.language import ast
from graphql.type.scalars import MAX_INT, MIN_INT


class BigInt(Scalar):
    """
    Handle any BigInts
    """
    @staticmethod
    def to_float(value):
        num = int(value)
        if num > MAX_INT or num < MIN_INT:
            return float(num)
        return num

    serialize = to_float
    parse_value = to_float

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.IntValue):
            return BigInt.to_float(node.value)
