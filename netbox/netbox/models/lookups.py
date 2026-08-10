from django.db.models import Lookup

__all__ = (
    'Ancestor',
    'AncestorOrEqual',
    'Descendant',
    'DescendantOrEqual',
)


class Ancestor(Lookup):
    """
    `path` is a strict ancestor of the queried path:  path @> rhs AND path <> rhs.

    Use `ancestor_or_equal` for the inclusive form (`@>`).
    """
    lookup_name = 'ancestor'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'({lhs} @> {rhs} AND {lhs} <> {rhs})', lhs_params + rhs_params + lhs_params + rhs_params


class AncestorOrEqual(Lookup):
    """`path` is an ancestor of (or equal to) the queried path:  path @> rhs"""
    lookup_name = 'ancestor_or_equal'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'{lhs} @> {rhs}', lhs_params + rhs_params


class Descendant(Lookup):
    """
    `path` is a strict descendant of the queried path:  path <@ rhs AND path <> rhs.

    Use `descendant_or_equal` for the inclusive form (`<@`).
    """
    lookup_name = 'descendant'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'({lhs} <@ {rhs} AND {lhs} <> {rhs})', lhs_params + rhs_params + lhs_params + rhs_params


class DescendantOrEqual(Lookup):
    """`path` is a descendant of (or equal to) the queried path:  path <@ rhs"""
    lookup_name = 'descendant_or_equal'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return f'{lhs} <@ {rhs}', lhs_params + rhs_params
