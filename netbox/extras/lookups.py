from django.db.models import CharField, Lookup

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
CachedValueField.register_lookup(NetHost)
CachedValueField.register_lookup(NetContainsOrEquals)
