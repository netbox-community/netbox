from __future__ import unicode_literals

from django.db import connections, models
from django.db.models.sql.compiler import SQLCompiler


class NullsFirstSQLCompiler(SQLCompiler):

    def get_order_by(self):
        result = super(NullsFirstSQLCompiler, self).get_order_by()
        if result:
            return [(expr, (sql + ' NULLS FIRST', params, is_ref)) for (expr, (sql, params, is_ref)) in result]
        return result


class NullsFirstQuery(models.sql.query.Query):

    def get_compiler(self, using=None, connection=None):
        if using is None and connection is None:
            raise ValueError("Need either using or connection")
        if using:
            connection = connections[using]
        return NullsFirstSQLCompiler(self, connection, using)


class NullsFirstQuerySet(models.QuerySet):
    """
    Override PostgreSQL's default behavior of ordering NULLs last. This is needed e.g. to order Prefixes in the global
    table before those assigned to a VRF.
    """

    def __init__(self, model=None, query=None, using=None, hints=None):
        super(NullsFirstQuerySet, self).__init__(model, query, using, hints)
        self.query = query or NullsFirstQuery(self.model)
