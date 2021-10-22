import functools

__all__ = (
    'Condition',
    'ConditionSet',
)


LOGIC_TYPES = (
    'and',
    'or'
)


def is_ruleset(data):
    """
    Determine whether the given dictionary looks like a rule set.
    """
    return type(data) is dict and len(data) == 1 and list(data.keys())[0] in LOGIC_TYPES


class Condition:
    """
    An individual conditional rule that evaluates a single attribute and its value.

    :param attr: The name of the attribute being evaluated
    :param value: The value being compared
    :param op: The logical operation to use when evaluating the value (default: 'eq')
    """
    EQ = 'eq'
    NEQ = 'neq'
    GT = 'gt'
    GTE = 'gte'
    LT = 'lt'
    LTE = 'lte'
    IN = 'in'
    CONTAINS = 'contains'

    OPERATORS = (
        EQ, NEQ, GT, GTE, LT, LTE, IN, CONTAINS
    )

    def __init__(self, attr, value, op=EQ):
        self.attr = attr
        self.value = value
        if op not in self.OPERATORS:
            raise ValueError(f"Unknown operator: {op}")
        self.eval_func = getattr(self, f'eval_{op}')

    def eval(self, data):
        """
        Evaluate the provided data to determine whether it matches the condition.
        """
        value = functools.reduce(dict.get, self.attr.split('.'), data)
        return self.eval_func(value)

    # Equivalency

    def eval_eq(self, value):
        return value == self.value

    def eval_neq(self, value):
        return value != self.value

    # Numeric comparisons

    def eval_gt(self, value):
        return value > self.value

    def eval_gte(self, value):
        return value >= self.value

    def eval_lt(self, value):
        return value < self.value

    def eval_lte(self, value):
        return value <= self.value

    # Membership

    def eval_in(self, value):
        return value in self.value

    def eval_contains(self, value):
        return self.value in value


class ConditionSet:
    """
    A set of one or more Condition to be evaluated per the prescribed logic (AND or OR). Example:

    {"and": [
        {"attr": "foo", "op": "eq", "value": 1},
        {"attr": "bar", "op": "neq", "value": 2}
    ]}

    :param ruleset: A dictionary mapping a logical operator to a list of conditional rules
    """
    def __init__(self, ruleset):
        if type(ruleset) is not dict:
            raise ValueError(f"Ruleset must be a dictionary, not {type(ruleset)}.")
        if len(ruleset) != 1:
            raise ValueError(f"Ruleset must have exactly one logical operator (found {len(ruleset)})")

        # Determine the logic type
        logic = list(ruleset.keys())[0]
        if type(logic) is not str or logic.lower() not in LOGIC_TYPES:
            raise ValueError(f"Invalid logic type: {logic} (must be 'and' or 'or')")
        self.logic = logic.lower()

        # Compile the set of Conditions
        self.conditions = [
            ConditionSet(rule) if is_ruleset(rule) else Condition(**rule)
            for rule in ruleset[self.logic]
        ]

    def eval(self, data):
        """
        Evaluate the provided data to determine whether it matches this set of conditions.
        """
        func = any if self.logic == 'or' else all
        return func(d.eval(data) for d in self.conditions)
