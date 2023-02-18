from django.db.models import CharField, TextField, Lookup
from .fields import CachedValueField


class Empty(Lookup):
    """
    Filter on whether a string is empty.
    """
    lookup_name = 'empty'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'CAST(LENGTH(%s) AS BOOLEAN) != %s' % (lhs, rhs), params


class NetContainsOrEquals(Lookup):
    """
    This lookup has the same functionality as the one from the ipam app except lhs is cast to inet
    """
    lookup_name = 'net_contains_or_equals'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'CAST(%s AS INET) >>= %s' % (lhs, rhs), params


CharField.register_lookup(Empty)
CachedValueField.register_lookup(NetContainsOrEquals)
