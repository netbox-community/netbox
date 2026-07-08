import functools
import operator
import re

from django.utils.translation import gettext as _

__all__ = (
    'Condition',
    'ConditionSet',
    'InvalidCondition',
)

AND = 'and'
OR = 'or'

# Sentinel for a snapshot attribute that could not be resolved (missing key or
# null snapshot).  Using a unique object ensures that two independently
# unresolvable values compare equal to each other, which is the correct
# semantics for the 'unchanged' operator when neither snapshot has the field.
_MISSING = object()


def is_ruleset(data):
    """
    Determine whether the given dictionary looks like a rule set.
    """
    return type(data) is dict and len(data) == 1 and list(data.keys())[0] in (AND, OR)


class InvalidCondition(Exception):
    pass


class Condition:
    """
    An individual conditional rule that evaluates a single attribute and its value.

    :param attr: The name of the attribute being evaluated
    :param value: The value being compared (not used by snapshot operators)
    :param op: The logical operation to use when evaluating the value (default: 'eq')
    :param negate: Invert the result of evaluation
    """
    EQ = 'eq'
    GT = 'gt'
    GTE = 'gte'
    LT = 'lt'
    LTE = 'lte'
    IN = 'in'
    CONTAINS = 'contains'
    REGEX = 'regex'
    CHANGED = 'changed'
    UNCHANGED = 'unchanged'

    OPERATORS = (
        EQ, GT, GTE, LT, LTE, IN, CONTAINS, REGEX, CHANGED, UNCHANGED
    )

    # Operators that compare pre/post snapshots and do not accept a value.
    SNAPSHOT_OPERATORS = (CHANGED, UNCHANGED)

    TYPES = {
        str: (EQ, CONTAINS, REGEX),
        bool: (EQ, CONTAINS),
        int: (EQ, GT, GTE, LT, LTE, CONTAINS),
        float: (EQ, GT, GTE, LT, LTE, CONTAINS),
        list: (EQ, IN, CONTAINS),
        type(None): (EQ,)
    }

    def __init__(self, attr, value=_MISSING, op=EQ, negate=False):
        if op not in self.OPERATORS:
            raise ValueError(_("Unknown operator: {op}. Must be one of: {operators}").format(
                op=op, operators=', '.join(self.OPERATORS)
            ))

        if op in self.SNAPSHOT_OPERATORS:
            if value is not _MISSING:
                raise ValueError(_(
                    "The '{op}' operator compares snapshots and does not accept a value."
                ).format(op=op))
            if attr.startswith('snapshots.'):
                raise ValueError(_(
                    "The '{op}' operator resolves '{attr}' within each snapshot dict, not the "
                    "top-level condition context. Use the bare attribute name (e.g. 'status') "
                    "rather than a snapshot path (e.g. 'snapshots.prechange.status'), which is "
                    "only valid with standard operators."
                ).format(op=op, attr=attr))
            self.value = _MISSING
        else:
            if value is _MISSING:
                raise ValueError(_("A value is required for the '{op}' operator.").format(op=op))
            if type(value) not in self.TYPES:
                raise ValueError(_("Unsupported value type: {value}").format(value=type(value)))
            if op not in self.TYPES[type(value)]:
                raise ValueError(_("Invalid type for {op} operation: {value}").format(op=op, value=type(value)))
            self.value = value

        self.attr = attr
        self.op = op
        self.eval_func = getattr(self, f'eval_{op}')
        self.negate = negate

    def _resolve_attr(self, data):
        """
        Walk self.attr as a dotted key path through data. Raises InvalidCondition on
        missing keys.
        """
        def _get(obj, key):
            if isinstance(obj, list):
                return [operator.getitem(item or {}, key) for item in obj]
            return operator.getitem(obj or {}, key)

        try:
            return functools.reduce(_get, self.attr.split('.'), data)
        except KeyError:
            raise InvalidCondition(f"Invalid key path: {self.attr}")

    def _resolve_snapshot_attr(self, snapshot):
        """
        Walk self.attr through a snapshot dict, returning _MISSING on any miss.
        Snapshots use the model serializer format (raw field values), not the REST
        API format, so e.g. status is stored as "active" not {"value": "active"}.
        """
        if snapshot is None:
            return _MISSING
        try:
            obj = snapshot
            for key in self.attr.split('.'):
                if isinstance(obj, list):
                    obj = [operator.getitem(item or {}, key) for item in obj]
                else:
                    obj = operator.getitem(obj or {}, key)
            return obj
        except (KeyError, TypeError):
            return _MISSING

    def eval(self, data):
        """
        Evaluate the provided data to determine whether it matches the condition.
        """
        if self.op in self.SNAPSHOT_OPERATORS:
            snapshots = data.get('snapshots') if isinstance(data, dict) else None
            if snapshots is None:
                raise InvalidCondition(
                    f"No snapshot data available for '{self.op}' operator. "
                    f"Snapshot operators are only meaningful on update and delete events."
                )
            result = self.eval_func(snapshots)
            return not result if self.negate else result

        value = self._resolve_attr(data)
        try:
            result = self.eval_func(value)
        except TypeError as e:
            raise InvalidCondition(f"Invalid data type at '{self.attr}' for '{self.op}' evaluation: {e}")

        if self.negate:
            return not result
        return result

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

    # Regular expressions

    def eval_regex(self, value):
        return re.match(self.value, value) is not None

    # Snapshot comparison operators
    # These resolve self.attr in both the prechange and postchange snapshots and
    # compare the resulting values.  _MISSING is used when a snapshot is absent
    # or does not contain the attribute.
    #
    # Fail-closed semantics:
    #   changed:   False when attr is absent from both snapshots (field never existed)
    #   unchanged: False when attr is absent from both snapshots (avoids silent pass on typos)

    def eval_changed(self, snapshots):
        pre = self._resolve_snapshot_attr(snapshots.get('prechange'))
        post = self._resolve_snapshot_attr(snapshots.get('postchange'))
        return pre != post

    def eval_unchanged(self, snapshots):
        pre = self._resolve_snapshot_attr(snapshots.get('prechange'))
        post = self._resolve_snapshot_attr(snapshots.get('postchange'))
        if pre is _MISSING and post is _MISSING:
            return False
        return pre == post


class ConditionSet:
    """
    A set of one or more Condition to be evaluated per the prescribed logic (AND or OR). Example:

    {"and": [
        {"attr": "foo", "op": "eq", "value": 1},
        {"attr": "bar", "op": "eq", "value": 2, "negate": true}
    ]}

    :param ruleset: A dictionary mapping a logical operator to a list of conditional rules
    """
    def __init__(self, ruleset):
        if type(ruleset) is not dict:
            raise ValueError(_("Ruleset must be a dictionary, not {ruleset}.").format(ruleset=type(ruleset)))

        if len(ruleset) == 1:
            self.logic = (list(ruleset.keys())[0]).lower()
            if self.logic not in (AND, OR):
                raise ValueError(_("Invalid logic type: must be 'AND' or 'OR'. Please check documentation."))

            # Compile the set of Conditions
            self.conditions = [
                ConditionSet(rule) if is_ruleset(rule) else Condition(**rule)
                for rule in ruleset[self.logic]
            ]
        else:
            try:
                self.logic = None
                self.conditions = [Condition(**ruleset)]
            except TypeError:
                raise ValueError(_("Incorrect key(s) informed. Please check documentation."))

    def eval(self, data):
        """
        Evaluate the provided data to determine whether it matches this set of conditions.
        """
        func = any if self.logic == 'or' else all
        return func(d.eval(data) for d in self.conditions)
