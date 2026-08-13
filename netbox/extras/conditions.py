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

# Sentinel for a snapshot attribute that could not be resolved (missing key or null snapshot)
_MISSING = object()


class AbsentData(dict):
    """
    An empty dict standing in for an event payload which cannot be evaluated: one which is
    absent (a job which recorded no data) or unusable (a payload which is not a dict at all).
    """
    def copy(self):
        # dict.copy() would return a plain dict, silently discarding the marker.
        return AbsentData(self)


def walk_path(obj, keys, empty_list_is_absent=False):
    """
    Walk a sequence of keys through obj, returning _MISSING if a key is absent or null along the way.

    Raises TypeError if the path descends into a value which cannot be indexed by key (e.g. a
    REST API-style 'status.value' applied to a snapshot, where status is the raw string
    "active"). Walkability follows from the value's type: an empty string is as unwalkable as any
    other scalar, not an absent key.
    """
    for key in keys:
        if obj is None:
            return _MISSING
        if isinstance(obj, list):
            if not obj and empty_list_is_absent:
                # An empty list yields no evidence either way
                return _MISSING
            values = []
            for item in obj:
                if item is None:
                    return _MISSING
                if not isinstance(item, dict):
                    raise TypeError(f"cannot resolve '{key}' within {type(item).__name__}")
                if key not in item:
                    return _MISSING
                values.append(item[key])
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

    def _references_absent_payload(self, data):
        """
        Return True if self.attr references an attribute of a payload which is absent
        altogether (AbsentData), as opposed to one which is present but lacks the attribute.
        """
        return isinstance(data, AbsentData) and self.attr.split('.')[0] not in data

    def _references_absent_snapshot(self, data):
        """
        Return True if self.attr is a direct snapshot path (snapshots.prechange.* or
        snapshots.postchange.*) whose snapshot is null and whose remaining path the opposite
        snapshot resolves. Create events have no prechange snapshot, delete events no
        postchange snapshot.

        Unlike an absent payload, such a reference resolves to null: the snapshot's absence is
        itself meaningful (the object did not exist before, or does not after), and validating
        the path below shows the reference to describe the data.
        """
        if not self.attr.startswith(SNAPSHOT_PREFIX):
            return False
        snapshots = data.get('snapshots') if isinstance(data, dict) else None
        if type(snapshots) is not dict:
            return False
        which, _sep, remainder = self.attr[len(SNAPSHOT_PREFIX):].partition('.')
        if which not in OPPOSITE_SNAPSHOT:
            # Anything other than prechange or postchange names no snapshot the event could have
            # recorded, so the path does not describe the data
            return False
        if which not in snapshots or snapshots[which] is not None:
            return False

        # The referenced snapshot is null, which excuses only data the event would otherwise
        # have carried, never a path which does not describe the data. Validate the remainder
        # against the opposite snapshot so that such a path fails closed here exactly as it does
        # when both snapshots are present; otherwise a typo would resolve to null and fire the
        # rule on every create or delete, with nothing logged.
        other = snapshots.get(OPPOSITE_SNAPSHOT[which])
        if remainder and other is not None:
            try:
                value = walk_path(other, remainder.split('.'), empty_list_is_absent=True)
            except TypeError:
                return False
            if value is _MISSING:
                return False

        # Nothing to validate against: with the opposite snapshot absent too, the event carries
        # no data anywhere for the path to be checked. Testing for the absent snapshot itself
        # (snapshots.prechange, no remainder) lands here too.
        return True

    def _resolve_snapshot_attrs(self, snapshots):
        """
        Walk self.attr through the prechange and postchange snapshots, returning the two
        resolved values, with _MISSING for a snapshot which is absent, lacks the attribute, or
        cannot be walked by the path.

        Raises InvalidCondition if the attribute resolves in neither snapshot, leaving nothing
        to compare: a misspelling, an unwalkable path, or an event which recorded no snapshots.
        The unresolved state must be reported rather than compared, since any boolean it
        returned would become a match under negate.

        A path which resolves in only one snapshot describes a real difference between them (a
        JSON attribute whose value changed shape, say), so the unresolved side counts as missing
        and the comparison proceeds: raising would report as unchanged an attribute which
        demonstrably changed. Only a snapshot yielding a value excuses the other side; one
        resolving to nothing is no evidence that the path describes the data.
        """
        keys = self.attr.split('.')
        values = []
        errors = []
        available = False
        resolved = False

        for which in ('prechange', 'postchange'):
            snapshot = snapshots.get(which)
            if snapshot is None:
                # Absent snapshot (normal for create and delete events): nothing to resolve
                values.append(_MISSING)
                continue
            available = True
            try:
                value = walk_path(snapshot, keys, empty_list_is_absent=True)
            except TypeError as e:
                values.append(_MISSING)
                errors.append(e)
            else:
                values.append(value)
                resolved = resolved or value is not _MISSING

        if not available:
            # Neither snapshot was recorded, so the attribute itself is not in question
            raise InvalidCondition(
                f"No snapshot data available for '{self.op}' operator: {self.attr}. "
                f"Snapshot operators are only meaningful on update and delete events."
            )
        if not resolved:
            reason = f" ({errors[0]})" if errors else ""
            raise InvalidCondition(
                f"Invalid key path for '{self.op}' operator: {self.attr}{reason}. The attribute resolves in neither "
                f"snapshot. Note that snapshots store raw field values, so choice fields have no '.value' suffix."
            )

        return values

    def eval(self, data):
        """
        Evaluate the provided data to determine whether it matches the condition.
        """
        if self.op in self.SNAPSHOT_OPERATORS:
            snapshots = data.get('snapshots') if isinstance(data, dict) else None
            if type(snapshots) is not dict:
                raise InvalidCondition(
                    f"No snapshot data available for '{self.op}' operator. "
                    f"Snapshot operators are only meaningful on update and delete events."
                )
            result = self.eval_func(snapshots)
            return not result if self.negate else result

        if self._references_absent_payload(data):
            # No payload to evaluate, so the condition cannot be satisfied. Negation is not
            # applied: it inverts the result of a comparison, and none took place - inverting
            # would fire the rule on an event which carried nothing to match against. Nor is
            # this an invalid condition: a job which records no data is routine, and logging it
            # per rule per event would bury the malformed conditions worth acting on.
            return False

        absent = self._references_absent_snapshot(data)
        value = None if absent else self._resolve_attr(data)
        try:
            result = self.eval_func(value)
        except TypeError as e:
            if not absent:
                raise InvalidCondition(f"Invalid data type at '{self.attr}' for '{self.op}' evaluation: {e}")
            # An absent snapshot resolves to null, which satisfies only a comparison against
            # null: contains, regex and the numeric comparisons raise TypeError on None. That is
            # a non-match, not a malformed condition, so report False (subject to negation
            # below) rather than aborting the condition set.
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

    def eval_changed(self, snapshots):
        pre, post = self._resolve_snapshot_attrs(snapshots)
        return pre != post

    def eval_unchanged(self, snapshots):
        pre, post = self._resolve_snapshot_attrs(snapshots)
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
