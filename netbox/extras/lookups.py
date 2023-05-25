from django.db.models import CharField, Lookup


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


CharField.register_lookup(Empty)
