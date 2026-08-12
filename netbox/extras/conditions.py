import re

from django.utils.translation import gettext as _

__all__ = (
    'AbsentData',
    'Condition',
    'ConditionSet',
    'InvalidCondition',
)

AND = 'and'
OR = 'or'

# Prefix identifying a condition attribute that reads an event's pre- or post-change snapshot directly, e.g.
# 'snapshots.prechange.status'.
SNAPSHOT_PREFIX = 'snapshots.'

# Maps each snapshot to its counterpart
OPPOSITE_SNAPSHOT = {
    'prechange': 'postchange',
    'postchange': 'prechange',
}

# Sentinel for a snapshot attribute that could not be resolved (missing key or null snapshot). Using a unique object
# ensures that two independently unresolvable values compare equal to each other, which is the correct semantics for the
# 'unchanged' operator when neither snapshot has the field.
_MISSING = object()


class AbsentData(dict):
    """
    An empty dict standing in for event data which is absent altogether, as opposed to data
    which is present but does not contain a referenced attribute.

    A condition referencing an attribute of absent data resolves to null instead of raising
    InvalidCondition: the absence is a normal property of the event (e.g. a job which
    recorded no data), not a malformed condition, so it must not abort evaluation of the
    condition set or log an error for every rule on every such event.
    """
    def copy(self):
        # dict.copy() would return a plain dict, silently discarding the marker.
        return AbsentData(self)


def walk_path(obj, keys):
    """
    Walk a sequence of keys through obj, returning _MISSING if a key is absent along the way.

    Raises TypeError if the path cannot be walked at all, i.e. if it descends into a value
    which cannot be indexed by key (e.g. a REST API-style 'status.value' applied to a
    snapshot, where status is the raw string "active" rather than a nested dict).

    Walkability is determined from the type of the value being descended into, never from
    its truthiness: an empty string or a zero is just as unwalkable as any other scalar, and
    must be reported as such rather than being mistaken for an absent key.

    Null values and empty lists are the exception. Neither is evidence of a malformed path,
    since there is nothing there to walk either way, so both resolve to _MISSING exactly as
    an absent key does.
    """
    for key in keys:
        if obj is None:
            return _MISSING
        if isinstance(obj, list):
            values = []
            for item in obj:
                if item is None:
                    return _MISSING
                if not isinstance(item, dict):
                    raise TypeError(f"cannot resolve '{key}' within {type(item).__name__}")
                if key not in item:
                    return _MISSING
                values.append(item[key])
            if not values:
                # An empty list yields no evidence either way
                return _MISSING
            obj = values
        elif isinstance(obj, dict):
            if key not in obj:
                return _MISSING
            obj = obj[key]
        else:
            raise TypeError(f"cannot resolve '{key}' within {type(obj).__name__}")
    return obj


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
            if attr.startswith(SNAPSHOT_PREFIX):
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
        missing keys, or when an intermediate value can't be indexed by key (e.g. a
        REST API-style path like 'status.value' applied to a raw snapshot value).
        """
        try:
            value = walk_path(data, self.attr.split('.'))
        except TypeError as e:
            raise InvalidCondition(f"Invalid key path: {self.attr} ({e})")
        if value is _MISSING:
            raise InvalidCondition(f"Invalid key path: {self.attr}")
        return value

    def _references_absent_data(self, data):
        """
        Return True if self.attr references data which is absent altogether, as opposed to
        data which is present but does not contain the attribute. Two cases qualify:

        * The data itself is absent (an AbsentData payload), e.g. a job event for a job
          which recorded no data.
        * self.attr is a direct snapshot path (snapshots.prechange.* or
          snapshots.postchange.*) whose referenced snapshot is null. Create events have no
          prechange snapshot and delete events have no postchange snapshot.
        """
        if isinstance(data, AbsentData) and self.attr.split('.')[0] not in data:
            return True
        if not self.attr.startswith(SNAPSHOT_PREFIX):
            return False
        snapshots = data.get('snapshots') if isinstance(data, dict) else None
        if type(snapshots) is not dict:
            return False
        which, _sep, remainder = self.attr[len(SNAPSHOT_PREFIX):].partition('.')
        if which not in snapshots or snapshots[which] is not None:
            return False

        # The referenced snapshot is null. Validate the remainder of the path against the
        # opposite snapshot, so that a path which cannot be walked at all (e.g. the REST
        # API-style 'status.value') fails closed here exactly as it does when both snapshots
        # are present, rather than resolving to None and firing the rule on every create or
        # delete. A path which is merely absent from the opposite snapshot is indeterminate
        # and treated as absent, since it resolves to nothing either way.
        other = snapshots.get(OPPOSITE_SNAPSHOT.get(which))
        if remainder and other is not None:
            try:
                walk_path(other, remainder.split('.'))
            except TypeError:
                return False

        return True

    def _resolve_snapshot_attrs(self, snapshots):
        """
        Walk self.attr through both the prechange and postchange snapshots, returning the
        two resolved values. _MISSING is returned for a snapshot which is absent, which does
        not contain the attribute, or in which the path cannot be walked at all (e.g. a REST
        API-style 'status.value', where status is the raw string "active" rather than a
        nested dict).

        Snapshots use the model serializer format (raw field values), not the REST
        API format, so e.g. status is stored as "active" not {"value": "active"}.

        Raises InvalidCondition if the path cannot be walked in any snapshot and resolves to
        a value in none of them, which is the case for a genuinely malformed path. A path
        which resolves in one snapshot but not the other describes a real difference between
        them (a JSON attribute whose value changed shape, say), so the unwalkable side is
        treated as missing and the comparison proceeds: raising would report the attribute as
        unchanged even though it demonstrably changed. Only a snapshot which actually yields
        a value excuses the unwalkable side; one which merely resolves to nothing (an absent
        key, a null, an empty list) offers no evidence that the path is well-formed.
        """
        keys = self.attr.split('.')
        values = []
        errors = []
        resolved = False

        for which in ('prechange', 'postchange'):
            snapshot = snapshots.get(which)
            if snapshot is None:
                # Absent snapshot (normal for create and delete events): nothing to resolve
                values.append(_MISSING)
                continue
            try:
                value = walk_path(snapshot, keys)
            except TypeError as e:
                values.append(_MISSING)
                errors.append(e)
            else:
                values.append(value)
                resolved = resolved or value is not _MISSING

        if errors and not resolved:
            raise InvalidCondition(
                f"Invalid key path for '{self.op}' operator: {self.attr} ({errors[0]}). Note that snapshots store "
                f"raw field values, so choice fields have no '.value' suffix."
            )

        return values

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

        absent = self._references_absent_data(data)
        value = None if absent else self._resolve_attr(data)
        try:
            result = self.eval_func(value)
        except TypeError as e:
            if not absent:
                raise InvalidCondition(f"Invalid data type at '{self.attr}' for '{self.op}' evaluation: {e}")
            # Absent data resolves to null, which satisfies only a comparison against null:
            # operators such as contains, regex, and the numeric comparisons raise a
            # TypeError on None. That is a non-match, not a malformed condition, so report
            # False (subject to negation below) rather than aborting the condition set.
            result = False

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
    # compare the resulting values.  _MISSING is used when a snapshot is absent,
    # does not contain the attribute, or cannot be walked by the path.
    #
    # Fail-closed semantics:
    #   changed:   False when attr is absent from both snapshots (field never existed)
    #   unchanged: False when attr is absent from both snapshots (avoids silent pass on typos)
    #
    # A path that cannot be walked in any of the snapshots available for the event (as
    # opposed to one that resolves to nothing) raises InvalidCondition from
    # _resolve_snapshot_attrs(), so a malformed condition is logged by
    # EventRule.eval_conditions() rather than quietly evaluating False forever.

    def eval_changed(self, snapshots):
        pre, post = self._resolve_snapshot_attrs(snapshots)
        return pre != post

    def eval_unchanged(self, snapshots):
        pre, post = self._resolve_snapshot_attrs(snapshots)
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
