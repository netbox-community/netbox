from django.db.models import CharField, Lookup


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


CharField.register_lookup(Empty)
