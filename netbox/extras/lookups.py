from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields.ranges import RangeField
from django.db.models import CharField, JSONField, Lookup
from django.db.models.fields.json import KeyTextTransform

from .fields import CachedValueField


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
        else:
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
        return 'HOST(CAST(%s AS INET)) = HOST(%s)' % (lhs, rhs), params


class NetContainsOrEquals(Lookup):
    """
    Similar to ipam.lookups.NetContainsOrEquals, but casts the field to INET.
    """
    lookup_name = 'net_contains_or_equals'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'CAST(%s AS INET) >>= %s' % (lhs, rhs), params


ArrayField.register_lookup(RangeContains)
CharField.register_lookup(Empty)
JSONField.register_lookup(JSONEmpty)
CachedValueField.register_lookup(NetHost)
CachedValueField.register_lookup(NetContainsOrEquals)
