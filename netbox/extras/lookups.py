from django.db.models import CharField, JSONField, Lookup
from django.db.models.fields.json import KeyTextTransform

from .fields import CachedValueField


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
    lookup_name = "empty"

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


CharField.register_lookup(Empty)
JSONField.register_lookup(JSONEmpty)
CachedValueField.register_lookup(NetHost)
CachedValueField.register_lookup(NetContainsOrEquals)
