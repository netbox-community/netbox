from __future__ import unicode_literals

from django.db.models import Lookup, Transform, IntegerField
from django.db.models import lookups


class NetFieldDecoratorMixin(object):

    def process_lhs(self, qn, connection, lhs=None):
        lhs = lhs or self.lhs
        lhs_string, lhs_params = qn.compile(lhs)
        lhs_string = 'TEXT(%s)' % lhs_string
        return lhs_string, lhs_params


class IExact(NetFieldDecoratorMixin, lookups.IExact):

    def get_rhs_op(self, connection, rhs):
        return '= LOWER(%s)' % rhs


class EndsWith(NetFieldDecoratorMixin, lookups.EndsWith):
    pass


class IEndsWith(NetFieldDecoratorMixin, lookups.IEndsWith):
    pass

    def get_rhs_op(self, connection, rhs):
        return 'LIKE LOWER(%s)' % rhs


class StartsWith(NetFieldDecoratorMixin, lookups.StartsWith):
    lookup_name = 'startswith'


class IStartsWith(NetFieldDecoratorMixin, lookups.IStartsWith):
    pass

    def get_rhs_op(self, connection, rhs):
        return 'LIKE LOWER(%s)' % rhs


class Regex(NetFieldDecoratorMixin, lookups.Regex):
    pass


class IRegex(NetFieldDecoratorMixin, lookups.IRegex):
    pass


class NetContainsOrEquals(Lookup):
    lookup_name = 'net_contains_or_equals'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s >>= %s' % (lhs, rhs), params


class NetContains(Lookup):
    lookup_name = 'net_contains'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s >> %s' % (lhs, rhs), params


class NetContained(Lookup):
    lookup_name = 'net_contained'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s << %s' % (lhs, rhs), params


class NetContainedOrEqual(Lookup):
    lookup_name = 'net_contained_or_equal'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <<= %s' % (lhs, rhs), params


class NetHost(Lookup):
    lookup_name = 'net_host'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        # Query parameters are automatically converted to IPNetwork objects, which are then turned to strings. We need
        # to omit the mask portion of the object's string representation to match PostgreSQL's HOST() function.
        if rhs_params:
            rhs_params[0] = rhs_params[0].split('/')[0]
        params = lhs_params + rhs_params
        return 'HOST(%s) = %s' % (lhs, rhs), params


class NetHostContained(Lookup):
    """
    Check for the host portion of an IP address without regard to its mask. This allows us to find e.g. 192.0.2.1/24
    when specifying a parent prefix of 192.0.2.0/26.
    """
    lookup_name = 'net_host_contained'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return 'CAST(HOST(%s) AS INET) << %s' % (lhs, rhs), params


class NetMaskLength(Transform):
    lookup_name = 'net_mask_length'
    function = 'MASKLEN'

    @property
    def output_field(self):
        return IntegerField()
