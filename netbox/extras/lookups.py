from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields.ranges import RangeField
from django.db.models import CharField, JSONField, Lookup
from django.db.models.expressions import Col
from django.db.models.fields.json import KeyTextTransform
from django.db.models.lookups import IContains, IEndsWith, IExact, IStartsWith

from .fields import CachedValueField, ChoiceSetField

__all__ = (
    'ChoiceValueLookup',
    'CollatedIContains',
    'CollatedIEndsWith',
    'CollatedIExact',
    'CollatedIStartsWith',
    'Empty',
    'JSONEmpty',
    'NetContainsOrEquals',
    'NetHost',
    'RangeContains',
)

# The ICU collation created by dcim.migrations.0197_natural_sort_collation and applied to
# the name field of most models.
NATURAL_SORT_COLLATION = 'natural_sort'


class RangeContains(Lookup):
    """
    Filter ArrayField(RangeField) columns where ANY element-range contains the scalar RHS.

    Usage (ORM):
        Model.objects.filter(<range_array_field>__range_contains=<scalar>)

    Works with int4range[], int8range[], daterange[], tstzrange[], etc.
    """

    lookup_name = 'range_contains'

    def as_sql(self, compiler, connection):
        # Compile LHS (the array-of-ranges column/expression) and RHS (scalar)
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)

        # Guard: only allow ArrayField whose base_field is a PostgreSQL RangeField
        field = getattr(self.lhs, 'output_field', None)
        if not (isinstance(field, ArrayField) and isinstance(field.base_field, RangeField)):
            raise TypeError('range_contains is only valid for ArrayField(RangeField) columns')

        # Range-contains-element using EXISTS + UNNEST keeps the range on the LHS: r @> value
        sql = f"EXISTS (SELECT 1 FROM unnest({lhs}) AS r WHERE r @> {rhs})"
        params = lhs_params + rhs_params
        return sql, params


class ChoiceValueLookup(Lookup):
    """
    Match rows where any [value, label] pair in a ChoiceSetField has the given value.

    Compares the RHS against the first element (the value) of each pair.
    """
    lookup_name = 'choice_value'
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        # Slice the value column of the two-dimensional array and match any element
        return f'{rhs} = ANY({lhs}[:][1:1])', [*rhs_params, *lhs_params]


class Empty(Lookup):
    """
    Filter on whether a string is empty.
    """
    lookup_name = 'empty'
    prepare_rhs = False

    def as_sql(self, compiler, connection):
        sql, params = compiler.compile(self.lhs)
        if self.rhs:
            return f"CAST(LENGTH({sql}) AS BOOLEAN) IS NOT TRUE", params
        return f"CAST(LENGTH({sql}) AS BOOLEAN) IS TRUE", params


class JSONEmpty(Lookup):
    """
    Support "empty" lookups for JSONField keys.

    A key is considered empty if it is "", null, or does not exist.
    """
    lookup_name = 'empty'

    def as_sql(self, compiler, connection):
        # self.lhs.lhs is the parent expression (could be a JSONField or another KeyTransform)
        # Rebuild the expression using KeyTextTransform to guarantee ->> (text)
        text_expr = KeyTextTransform(self.lhs.key_name, self.lhs.lhs)
        lhs_sql, lhs_params = compiler.compile(text_expr)

        value = self.rhs
        if value not in (True, False):
            raise ValueError("The 'empty' lookup only accepts True or False.")

        condition = '' if value else 'NOT '
        sql = f"(NULLIF({lhs_sql}, '') IS {condition}NULL)"

        return sql, lhs_params


class NetHost(Lookup):
    """
    Similar to ipam.lookups.NetHost, but casts the field to INET.
    """
    lookup_name = 'net_host'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'HOST(CAST({lhs} AS INET)) = HOST({rhs})', params


class NetContainsOrEquals(Lookup):
    """
    Similar to ipam.lookups.NetContainsOrEquals, but casts the field to INET.
    """
    lookup_name = 'net_contains_or_equals'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'CAST({lhs} AS INET) >>= {rhs}', params


class CollatedCaseInsensitiveMixin:
    """
    Apply the column's collation to the right-hand side of a case-insensitive comparison.

    UPPER() folds according to the collation of its argument. Django uppercases the column
    under the column's own collation but the parameter under the database default, so for a
    column using natural_sort the two sides disagree: UPPER('ß') is 'SS' on the left and
    'ß' on the right, and the comparison silently matches nothing (#23012).

    The COLLATE clause must sit inside UPPER(), not after the comparison, or it applies to
    the comparison's result rather than to its operand and has no effect.

    Tested in dcim.tests.test_filtersets.DeviceCollatedFilterTestCase, which is where the
    collated fields these lookups act upon are defined.
    """
    def process_rhs(self, compiler, connection):
        rhs, params = super().process_rhs(compiler, connection)
        collation = getattr(self.lhs.output_field, 'db_collation', None)

        # Restricted to a bare column compared against a single placeholder. An expression
        # wrapping the column (Collate() and CollateAsChar() in particular) may already
        # carry an explicit collation, and PostgreSQL rejects two explicit collations in
        # one comparison. Requiring a Col also avoids reading a collation from an
        # annotation's output_field which the annotation itself does not carry, as Concat()
        # and Coalesce() both do.
        #
        # The placeholder is compared literally rather than inspected structurally: a field
        # declaring its own get_placeholder() compiles to something other than '%s', and
        # splicing a COLLATE clause into that is not safe. Any other rhs is a deliberate
        # opt-out which leaves the lookup at its previous behaviour.
        if collation == NATURAL_SORT_COLLATION and rhs == '%s' and isinstance(self.lhs, Col):
            # The collation name cannot be passed as a query parameter, but it originates
            # from the field definition rather than from user input.
            rhs = f'%s COLLATE "{collation}"'

        return rhs, params


class CollatedIContains(CollatedCaseInsensitiveMixin, IContains):
    pass


class CollatedIExact(CollatedCaseInsensitiveMixin, IExact):
    pass


class CollatedIStartsWith(CollatedCaseInsensitiveMixin, IStartsWith):
    pass


class CollatedIEndsWith(CollatedCaseInsensitiveMixin, IEndsWith):
    pass


ArrayField.register_lookup(RangeContains)
ChoiceSetField.register_lookup(ChoiceValueLookup)
CharField.register_lookup(Empty)
JSONField.register_lookup(JSONEmpty)
CachedValueField.register_lookup(NetHost)
CachedValueField.register_lookup(NetContainsOrEquals)

# Override the built-in case-insensitive lookups so that they respect the collation of the
# column being searched.
CharField.register_lookup(CollatedIContains)
CharField.register_lookup(CollatedIExact)
CharField.register_lookup(CollatedIStartsWith)
CharField.register_lookup(CollatedIEndsWith)
