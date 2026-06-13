import netaddr
from django.db.models import IntegerField, Lookup, Transform, lookups


class NetFieldDecoratorMixin:

    def process_lhs(self, qn, connection, lhs=None):
        lhs = lhs or self.lhs
        lhs_string, lhs_params = qn.compile(lhs)
        lhs_string = f'TEXT({lhs_string})'
        return lhs_string, lhs_params


class IExact(NetFieldDecoratorMixin, lookups.IExact):

    def get_rhs_op(self, connection, rhs):
        return f'= LOWER({rhs})'


class EndsWith(NetFieldDecoratorMixin, lookups.EndsWith):
    pass


class IEndsWith(NetFieldDecoratorMixin, lookups.IEndsWith):
    pass

    def get_rhs_op(self, connection, rhs):
        return f'LIKE LOWER({rhs})'


class StartsWith(NetFieldDecoratorMixin, lookups.StartsWith):
    lookup_name = 'startswith'


class IStartsWith(NetFieldDecoratorMixin, lookups.IStartsWith):
    pass

    def get_rhs_op(self, connection, rhs):
        return f'LIKE LOWER({rhs})'


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
        return f'{lhs} >>= {rhs}', params


class NetContains(Lookup):
    lookup_name = 'net_contains'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} >> {rhs}', params


class NetContained(Lookup):
    lookup_name = 'net_contained'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} << {rhs}', params


class NetContainedOrEqual(Lookup):
    lookup_name = 'net_contained_or_equal'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return f'{lhs} <<= {rhs}', params


class NetHost(Lookup):
    lookup_name = 'net_host'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        # Query parameters are automatically converted to IPNetwork objects, which are then turned to strings. We need
        # to omit the mask portion of the object's string representation to match PostgreSQL's HOST() function.
        # Note: params may be tuples (Django 6.0+) or lists (older Django), so convert before mutating.
        rhs_params = list(rhs_params)
        if rhs_params:
            rhs_params[0] = rhs_params[0].split('/')[0]
        params = list(lhs_params) + rhs_params
        # Cast to INET so the predicate matches the inet ipam_ipaddress_host index.
        return f'CAST(HOST({lhs}) AS INET) = {rhs}', params


class NetIn(Lookup):
    lookup_name = 'net_in'

    def get_prep_lookup(self):
        # Don't cast the query value to a netaddr object, since it may or may not include a mask.
        return self.rhs

    def as_sql(self, qn, connection):
        lhs = self.process_lhs(qn, connection)[0]
        rhs_params = self.process_rhs(qn, connection)[1]
        with_mask, without_mask = [], []
        for address in rhs_params[0]:
            if '/' in address:
                with_mask.append(address)
            else:
                without_mask.append(address)

        address_in_clause = self.create_in_clause('{} IN ('.format(lhs), len(with_mask))
        # Cast to INET so the predicate matches the inet ipam_ipaddress_host index.
        host_in_clause = self.create_in_clause('CAST(HOST({}) AS INET) IN ('.format(lhs), len(without_mask))

        if with_mask and not without_mask:
            return address_in_clause, with_mask
        if not with_mask and without_mask:
            return host_in_clause, without_mask

        in_clause = '({}) OR ({})'.format(address_in_clause, host_in_clause)
        with_mask.extend(without_mask)
        return in_clause, with_mask

    @staticmethod
    def create_in_clause(clause_part, max_size):
        clause_elements = [clause_part]
        for offset in range(0, max_size):
            if offset > 0:
                clause_elements.append(', ')
            clause_elements.append('%s')
        clause_elements.append(')')
        return ''.join(clause_elements)


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
        return f'CAST(HOST({lhs}) AS INET) <<= {rhs}', params


class NetHostBetween(Lookup):
    """
    Match host addresses (mask ignored) falling inclusively between two bounds. The left-hand
    side is kept as an inet-typed host expression so PostgreSQL can use the host expression
    indexes on the IPAM address and range tables; the CAST(HOST(...) AS INET) spelling matches
    NetHost/NetIn for consistency (PostgreSQL canonicalizes the INET(HOST(...)) function form
    to the same expression).
    """
    lookup_name = 'host_between'

    def get_prep_lookup(self):
        if not isinstance(self.rhs, (list, tuple)) or len(self.rhs) != 2:
            raise ValueError('The host_between lookup requires a (lower, upper) pair of bounds')
        try:
            # Normalize to bare hosts; reject malformed values before they reach SQL.
            lower, upper = (netaddr.IPNetwork(str(bound)).ip for bound in self.rhs)
        except (netaddr.AddrFormatError, ValueError) as e:
            raise ValueError(f'Invalid host_between bound: {e}') from e
        if lower.version != upper.version:
            raise ValueError('host_between bounds must not mix address families')
        return lower, upper

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        params = list(lhs_params) + [str(bound) for bound in self.rhs]
        return f'CAST(HOST({lhs}) AS INET) BETWEEN %s AND %s', params


class NetFamily(Transform):
    lookup_name = 'family'
    function = 'FAMILY'

    @property
    def output_field(self):
        return IntegerField()


class NetMaskLength(Transform):
    function = 'MASKLEN'
    lookup_name = 'net_mask_length'

    @property
    def output_field(self):
        return IntegerField()


class Host(Transform):
    function = 'HOST'
    lookup_name = 'host'


class Inet(Transform):
    function = 'INET'
    lookup_name = 'inet'
