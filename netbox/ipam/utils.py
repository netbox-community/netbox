from dataclasses import dataclass

import netaddr
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db.models import BooleanField, F, Func, Q
from django.utils.translation import gettext_lazy as _

from .constants import *

__all__ = (
    'PORT_MAPPING_LOOKUPS',
    'AvailableIPSpace',
    'PortMappingMatch',
    'add_available_vlans',
    'add_requested_prefixes',
    'annotate_ip_space',
    'expand_port_mapping',
    'get_next_available_prefix',
    'group_port_mapping_rows',
    'group_port_mappings',
    'legacy_protocol_and_ports',
    'normalize_port_mapping',
    'port_mapping_q',
    'rebuild_prefixes',
    'sorted_int_ports',
    'split_port_mapping',
)


@dataclass
class AvailableIPSpace:
    """
    A representation of available IP space between two IP addresses/ranges.
    """
    size: int
    first_ip: str

    @property
    def title(self):
        if self.size == 1:
            return _('1 IP available')
        if self.size <= 65536:
            return _('{count} IPs available').format(count=self.size)
        return _('Many IPs available')


def add_requested_prefixes(parent, prefix_list, show_available=True, show_assigned=True):
    """
    Return a list of requested prefixes using show_available, show_assigned filters. If available prefixes are
    requested, create fake Prefix objects for all unallocated space within a prefix.

    :param parent: Parent Prefix instance
    :param prefix_list: Child prefixes list (or queryset)
    :param show_available: Include available prefixes.
    :param show_assigned: Show assigned prefixes.
    """
    child_prefixes = []

    # Add available prefixes to the table if requested
    if prefix_list and show_available:
        Prefix = apps.get_model('ipam', 'Prefix')

        # Find all unallocated space, add fake Prefix objects to child_prefixes.
        # IMPORTANT: These are unsaved Prefix instances (pk=None). If this is ever changed to use
        # saved Prefix instances with real pks, bulk delete will fail for mixed-type selections
        # due to single-model form validation. See: https://github.com/netbox-community/netbox/issues/21176
        available_prefixes = netaddr.IPSet(parent) ^ netaddr.IPSet([p.prefix for p in prefix_list])
        available_prefixes = [Prefix(prefix=p, status=None) for p in available_prefixes.iter_cidrs()]
        child_prefixes = child_prefixes + available_prefixes

    # Add assigned prefixes to the table if requested
    if prefix_list and show_assigned:
        child_prefixes = child_prefixes + list(prefix_list)

    # Sort child prefixes after additions
    child_prefixes.sort(key=lambda p: p.prefix)

    return child_prefixes


def annotate_ip_space(prefix, *, ip_addresses=None, ip_ranges=None):
    """
    Return a prefix's child ranges and IPs interleaved with available space records.

    :param prefix: Parent Prefix instance
    :param ip_addresses: Child IP addresses queryset (defaults to all child IPs)
    :param ip_ranges: Child IP ranges queryset (defaults to all populated child ranges)
    """
    if ip_addresses is None:
        ip_addresses = prefix.get_child_ips()
    if ip_ranges is None:
        ip_ranges = prefix.get_child_ranges(mark_populated=True)

    # Compile child objects
    records = []
    records.extend([
        (iprange.start_address.ip, iprange) for iprange in ip_ranges
    ])
    records.extend([
        (ip.address.ip, ip) for ip in ip_addresses
    ])
    records = sorted(records, key=lambda x: x[0])

    # Determine the first & last valid IP addresses in the prefix
    first_ip_in_prefix, last_ip_in_prefix = prefix.usable_ip_bounds

    if not records:
        return [
            AvailableIPSpace(
                size=int(last_ip_in_prefix - first_ip_in_prefix + 1),
                first_ip=f'{first_ip_in_prefix}/{prefix.mask_length}'
            )
        ]

    output = []
    prev_ip = None

    # Account for any available IPs before the first real IP
    if records[0][0] > first_ip_in_prefix:
        output.append(AvailableIPSpace(
            size=int(records[0][0] - first_ip_in_prefix),
            first_ip=f'{first_ip_in_prefix}/{prefix.mask_length}'
        ))

    # Add IP ranges & addresses, annotating available space in between records
    for record in records:
        if prev_ip:
            # Annotate available space
            if (diff := int(record[0]) - int(prev_ip)) > 1:
                first_skipped = f'{prev_ip + 1}/{prefix.mask_length}'
                output.append(AvailableIPSpace(
                    size=diff - 1,
                    first_ip=first_skipped
                ))

        output.append(record[1])

        # Update the previous IP address
        if hasattr(record[1], 'end_address'):
            prev_ip = record[1].end_address.ip
        else:
            prev_ip = record[0]

    # Include any remaining available IPs
    if prev_ip < last_ip_in_prefix:
        output.append(AvailableIPSpace(
            size=int(last_ip_in_prefix - prev_ip),
            first_ip=f'{prev_ip + 1}/{prefix.mask_length}'
        ))

    return output


def available_vlans_from_range(vlans, vlan_group, vid_range):
    """
    Create fake records for all gaps between used VLANs
    """
    min_vid = int(vid_range.lower) if vid_range else VLAN_VID_MIN
    max_vid = int(vid_range.upper) if vid_range else VLAN_VID_MAX

    if not vlans:
        return [{
            'vid': min_vid,
            'vlan_group': vlan_group,
            'available': max_vid - min_vid
        }]

    prev_vid = min_vid - 1
    new_vlans = []
    for vlan in vlans:

        # Ignore VIDs outside the range
        if not min_vid <= vlan.vid < max_vid:
            continue

        # Annotate any available VIDs between the previous (or minimum) VID
        # and the current VID
        if vlan.vid - prev_vid > 1:
            new_vlans.append({
                'vid': prev_vid + 1,
                'vlan_group': vlan_group,
                'available': vlan.vid - prev_vid - 1,
            })

        prev_vid = vlan.vid

    # Annotate any remaining available VLANs
    if prev_vid < max_vid - 1:
        new_vlans.append({
            'vid': prev_vid + 1,
            'vlan_group': vlan_group,
            'available': max_vid - prev_vid - 1,
        })

    return new_vlans


def add_available_vlans(vlans, vlan_group):
    """
    Create fake records for all gaps between used VLANs
    """
    new_vlans = []
    for vid_range in vlan_group.vid_ranges:
        new_vlans.extend(available_vlans_from_range(vlans, vlan_group, vid_range))

    vlans = list(vlans) + new_vlans
    vlans.sort(key=lambda v: v['vid'] if isinstance(v, dict) else v.vid)

    return vlans


def rebuild_prefixes(vrf):
    """
    Rebuild the prefix hierarchy for all prefixes in the specified VRF (or global table).
    """
    Prefix = apps.get_model('ipam', 'Prefix')
    prefix_queryset = Prefix.objects.filter(vrf=vrf)

    def contains(parent, child):
        return child in parent and child != parent

    def push_to_stack(prefix):
        # Increment child count on parent nodes
        for n in stack:
            n['children'] += 1
        stack.append({
            'pk': [prefix['pk']],
            'prefix': prefix['prefix'],
            'children': 0,
        })

    stack = []
    update_queue = []
    prefixes = prefix_queryset.order_by('prefix', 'pk').values('pk', 'prefix')

    # Iterate through all Prefixes in the table, growing and shrinking the stack as we go
    for p in prefixes:

        # Grow the stack if this is a child of the most recent prefix
        if not stack or contains(stack[-1]['prefix'], p['prefix']):
            push_to_stack(p)

        # Handle duplicate prefixes
        elif stack[-1]['prefix'] == p['prefix']:
            stack[-1]['pk'].append(p['pk'])

        # If this is a sibling or parent of the most recent prefix, pop nodes from the
        # stack until we reach a parent prefix (or the root)
        else:
            while stack and not contains(stack[-1]['prefix'], p['prefix']):
                node = stack.pop()
                for pk in node['pk']:
                    update_queue.append(
                        Prefix(pk=pk, _depth=len(stack), _children=node['children'])
                    )
            push_to_stack(p)

        # Flush the update queue once it reaches 100 Prefixes
        if len(update_queue) >= 100:
            Prefix.objects.bulk_update(update_queue, ['_depth', '_children'])
            update_queue = []

    # Clear out any prefixes remaining in the stack
    while stack:
        node = stack.pop()
        for pk in node['pk']:
            update_queue.append(
                Prefix(pk=pk, _depth=len(stack), _children=node['children'])
            )

    # Final flush of any remaining Prefixes
    Prefix.objects.bulk_update(update_queue, ['_depth', '_children'])


def get_next_available_prefix(ipset, prefix_size):
    """
    Given a prefix length, allocate the next available prefix from an IPSet.
    """
    for available_prefix in ipset.iter_cidrs():
        if prefix_size >= available_prefix.prefixlen:
            allocated_prefix = f"{available_prefix.network}/{prefix_size}"
            ipset.remove(allocated_prefix)
            return allocated_prefix
    return None


#
# Service port mappings
#

def split_port_mapping(mapping):
    """
    Split a ``protocol/port`` string (e.g. ``'tcp/80'``) into its ``(protocol, port)`` parts. A missing
    separator or port yields an empty string for that part, leaving validation to report the problem.
    """
    protocol, _sep, port = mapping.partition('/')
    return protocol, port


def normalize_port_mapping(mapping):
    """
    Canonicalize a single ``protocol/port`` string as far as possible *without raising*: the protocol is
    lowercased and a numeric port loses any leading zeros, so ``'TCP/080'`` becomes ``'tcp/80'``. Anything
    unrecognized is returned unchanged, in which case it simply won't match a stored (always-canonical)
    mapping.

    This is the lookup-side counterpart to ``validate_port_mappings()``, which enforces the same
    canonical form on write but rejects bad input. Filtering must not 400 on an unknown protocol or a
    malformed pair — an empty result set is the right answer there — hence the separate, lenient variant.
    """
    # Imported lazily to avoid a circular import during settings load (ipam.choices reads
    # settings.FIELD_CHOICES), matching validate_port_mappings().
    from ipam.choices import ServiceProtocolChoices

    protocol, port = split_port_mapping(mapping)
    if not port or not port.isdigit():
        return mapping
    protocol = protocol.lower()
    if protocol not in ServiceProtocolChoices.values():
        return mapping
    return f'{protocol}/{int(port)}'


def group_port_mappings(mappings):
    """
    Group a flat ``['tcp/80', 'tcp/443', 'udp/53']`` list into an ordered ``{protocol: [ports]}`` dict,
    preserving first-seen protocol order. Shared by the display property and the form widget so the
    ``protocol/port`` string is parsed in exactly one place.
    """
    grouped = {}
    for mapping in mappings:
        protocol, port = split_port_mapping(mapping)
        grouped.setdefault(protocol, []).append(port)
    return grouped


def group_port_mapping_rows(mappings):
    """
    Group a flat ``['tcp/80', 'tcp/443', 'udp/53']`` list into per-protocol rows
    ``[{'protocol': 'tcp', 'ports': '80,443'}, {'protocol': 'udp', 'ports': '53'}]`` — the shape the
    port-mapping form widget renders, one row per protocol.
    """
    return [
        {'protocol': protocol, 'ports': ','.join(ports)}
        for protocol, ports in group_port_mappings(mappings).items()
    ]


def sorted_int_ports(ports):
    """
    Sort a protocol's port strings numerically and return them as integers. Any entry that bypassed
    validation (a raw SQL write, a plugin, or an unmigrated row) and isn't a plain integer is skipped
    rather than raising, so a single malformed mapping degrades gracefully on API reads instead of
    raising a 500 — mirroring the tolerance of ``ServiceBase.port_mappings_list``.
    """
    return sorted(int(port) for port in ports if str(port).isdigit())


def legacy_protocol_and_ports(mappings):
    """
    Collapse port mappings into the deprecated single-protocol ``(protocol, ports)`` representation.
    Single source of truth for the backward-compatibility contract shared by the REST serializers and
    the GraphQL types:

      * single protocol    -> ``(protocol, [sorted int ports])``
      * no mappings         -> ``(None, [])``   (representable as an empty legacy ports list)
      * multiple protocols  -> ``(None, None)`` (not representable; ``ports=None`` signals "read
        port_mappings instead")
      * single protocol, but a port fails integer coercion (malformed raw/plugin data) -> ``(None, None)``
        (a subset would be plausible-but-wrong, so signal "not representable" rather than silently
        dropping the bad mapping)
    """
    grouped = group_port_mappings(mappings)
    if len(grouped) == 1:
        protocol, ports = next(iter(grouped.items()))
        int_ports = sorted_int_ports(ports)
        # If any port was dropped by coercion, the legacy single-protocol view can't faithfully
        # represent this service; signal "not representable" instead of returning a partial list.
        if len(int_ports) != len(ports):
            return None, None
        return protocol, int_ports
    return (None, []) if not grouped else (None, None)


# Whitelisted SQL comparison operators for the port half of a mapping, keyed by the django-filter
# lookup name. Only these five names are ever interpolated into SQL by PortMappingMatch, so the
# operator can never originate from user input.
PORT_MAPPING_LOOKUPS = {
    'exact': '=',
    'gt': '>',
    'gte': '>=',
    'lt': '<',
    'lte': '<=',
}

# The port half of an unnested mapping, as an integer. Guarded by a numeric test so a malformed mapping
# written outside the ORM (raw SQL, a plugin) evaluates to NULL — which no comparison matches — instead
# of aborting the whole query with an invalid-input-syntax error. Mirrors the tolerance that
# sorted_int_ports() and ServiceBase.port_mappings_list already apply on reads.
_PORT_MAPPING_PORT_SQL = (
    "CASE WHEN split_part(port_mapping, '/', 2) ~ '^[0-9]+$' "
    "THEN split_part(port_mapping, '/', 2)::integer END"
)


class PortMappingMatch(Func):
    """
    A boolean expression which is true for services having at least one port mapping that satisfies the
    given protocol and port tests:

        EXISTS (
            SELECT 1 FROM unnest(port_mappings) AS port_mapping
            WHERE split_part(port_mapping, '/', 1) = ANY(<protocols>)
              AND <port> >= <value> AND <port> <= <value> ...
        )

    Testing every condition against the *same* unnested mapping is what keeps protocol and port
    correlated: a service exposing tcp/80 and udp/9999 must not match ``protocol=tcp&port__gt=1000``,
    and one exposing tcp/500 and tcp/5000 must not match ``port__gte=1000&port__lte=2000``.

    This is deliberately a sequential scan. GIN's ``array_ops`` opclass supports only ``=``, ``&&``,
    ``@>`` and ``<@``, so no array index can serve a range comparison, and the alternatives (a
    trigger-maintained denormalized column, or a related table) either cannot express the correlation or
    cost far more than the scan — measured at ~200 ms over 400k services and ~1 s over 2M.
    ``port_mapping_q()`` therefore reserves this for the cases an array overlap cannot express and uses
    the GIN-indexable overlap for exact protocol+port lookups.
    """
    output_field = BooleanField()

    def __init__(self, protocols=(), port_tests=()):
        """
        Args:
            protocols: protocol values to match, OR'd together.
            port_tests: ``(lookup, values)`` pairs, where ``lookup`` is a key of
                ``PORT_MAPPING_LOOKUPS``. Pairs are AND'd (and so must hold for one single mapping);
                the values within a pair are OR'd, matching how django-filter's multi-value filters
                combine ``?port=80&port=443``.
        """
        self.protocols = list(protocols or ())
        self.port_tests = [
            (lookup, list(values)) for lookup, values in (port_tests or ()) if values
        ]
        for lookup, _values in self.port_tests:
            if lookup not in PORT_MAPPING_LOOKUPS:
                raise ValueError(f"Unsupported port mapping lookup: {lookup}")
        super().__init__(F('port_mappings'))

    def as_sql(self, compiler, connection, **extra_context):
        mappings_sql, mappings_params = compiler.compile(self.source_expressions[0])
        conditions = []
        params = list(mappings_params)

        if self.protocols:
            conditions.append("split_part(port_mapping, '/', 1) = ANY(%s)")
            params.append(self.protocols)
        for lookup, values in self.port_tests:
            operator = PORT_MAPPING_LOOKUPS[lookup]
            conditions.append('({})'.format(
                ' OR '.join(f'{_PORT_MAPPING_PORT_SQL} {operator} %s' for _value in values)
            ))
            params.extend(values)

        if not conditions:
            # port_mapping_q() never builds an unconstrained match, but be explicit rather than emit an
            # EXISTS with an empty WHERE clause.
            return 'TRUE', []

        sql = (
            f"EXISTS (SELECT 1 FROM unnest({mappings_sql}) AS port_mapping "
            f"WHERE {' AND '.join(conditions)})"
        )
        return sql, params


def port_mapping_q(protocols=(), port_tests=()):
    """
    Build a ``Q`` filtering services by protocol and/or port, correlated so that a combined query must
    be satisfied by a *single* mapping. See ``PortMappingMatch`` for the argument shapes.

    A lone exact port test reduces to a GIN-indexable array overlap on ``port_mappings``
    (``port_mappings && ['tcp/80', ...]`` — each element is one whole mapping, so an overlap means
    "shares any mapping"); for a port-only query each port is paired with every valid protocol to keep
    it a single overlap. Everything else — a protocol-only query, whose ports are unbounded and cannot
    be enumerated, and any range lookup, which no array index can serve — falls back to
    ``PortMappingMatch``. Shared by the FilterSet and the GraphQL filters.
    """
    # Imported lazily to avoid a circular import during settings load (ipam.choices reads
    # settings.FIELD_CHOICES), matching ipam.validators.
    from ipam.choices import ServiceProtocolChoices

    protocols = list(protocols or ())
    port_tests = [(lookup, list(values)) for lookup, values in (port_tests or ()) if values]

    if not protocols and not port_tests:
        return Q()

    if len(port_tests) == 1 and port_tests[0][0] == 'exact':
        # Every stored mapping's protocol is validated against ServiceProtocolChoices, so enumerating
        # the (small, fixed) protocol set covers all valid data for a port-only query.
        ports = port_tests[0][1]
        mapping_protocols = protocols or ServiceProtocolChoices.values()
        combos = [f'{protocol}/{port}' for protocol in mapping_protocols for port in ports]
        return Q(port_mappings__overlap=combos)

    return Q(PortMappingMatch(protocols=protocols, port_tests=port_tests))


def expand_port_mapping(protocol, ports):
    """
    Expand a single protocol plus its ports into the model's flat ``['tcp/80', 'tcp/443', ...]`` tokens.
    ``ports`` may be a comma/range string (the form widget's format, e.g. ``('tcp', '80,443,8000-8010')``)
    or an already-expanded list of ports (e.g. set programmatically).

    An empty ``ports`` yields a single bare ``'protocol/'`` token so ``validate_port_mappings`` reports a
    clear "expected protocol/port" error (rather than ``parse_numeric_range`` raising a confusing
    'Range "" is invalid'). An empty ``protocol`` raises a clear error rather than producing a ``'/80'``
    token that surfaces as "Invalid protocol:" with a blank value. Shared by the model form field so the
    protocol/port pairing is built in one place, and so every entry path gets the blank-protocol check.
    """
    # Imported lazily to avoid pulling the forms layer in at module load.
    from utilities.forms.utils import parse_numeric_range

    # No case-folding here: validate_port_mappings (which every token below flows through) matches the
    # protocol case-insensitively and stores the canonical value.
    protocol = (protocol or '').strip()
    if not protocol:
        # Ports given with no protocol would otherwise expand to '/80' and surface as a confusing
        # "Invalid protocol:" with a blank value. Report the real problem instead, in wording that fits
        # all entry paths that route through here (the form widget and CSV import).
        raise ValidationError(_("Each port mapping must specify a protocol."))

    if isinstance(ports, (list, tuple)):
        # Already-expanded ports are paired as-is; validate_port_mappings() checks each value's range.
        if not ports:
            return [f'{protocol}/']
        return [f'{protocol}/{port}' for port in ports]

    ports_str = (ports or '').strip()
    if not ports_str:
        return [f'{protocol}/']
    # parse_numeric_range validates each range against the port bounds (rejecting reversed and
    # out-of-range values before expansion), so a non-empty string always yields >=1 port.
    return [
        f'{protocol}/{port}'
        for port in parse_numeric_range(ports_str, min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX)
    ]
