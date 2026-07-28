from dataclasses import dataclass

import netaddr
from django.apps import apps
from django.utils.translation import gettext_lazy as _

from .constants import *

__all__ = (
    'AvailableIPSpace',
    'add_available_vlans',
    'add_requested_prefixes',
    'annotate_ip_space',
    'expand_port_mapping',
    'get_next_available_prefix',
    'group_port_mappings',
    'legacy_protocol_and_ports',
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


def annotate_ip_space(prefix):
    # Compile child objects
    records = []
    records.extend([
        (iprange.start_address.ip, iprange) for iprange in prefix.get_child_ranges(mark_populated=True)
    ])
    records.extend([
        (ip.address.ip, ip) for ip in prefix.get_child_ips()
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


def sorted_int_ports(ports):
    """
    Sort a protocol's port strings numerically and return them as integers. Any entry that bypassed
    validation (a raw SQL write, a plugin, or an unmigrated row) and isn't a plain integer is skipped
    rather than raising, so a single malformed mapping degrades gracefully on API reads instead of
    raising a 500 — mirroring the tolerance of ``ServiceBase.port_list``.
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
    """
    grouped = group_port_mappings(mappings)
    if len(grouped) == 1:
        protocol, ports = next(iter(grouped.items()))
        return protocol, sorted_int_ports(ports)
    return (None, []) if not grouped else (None, None)


def expand_port_mapping(protocol, ports_str):
    """
    Expand a single protocol plus a comma/range port string (e.g. ``('tcp', '80,443,8000-8010')``) into
    the model's flat ``['tcp/80', 'tcp/443', ...]`` tokens. An empty ``ports_str`` yields a single bare
    ``'protocol/'`` token so ``validate_port_mappings`` reports a clear "expected protocol/port" error
    (rather than ``parse_numeric_range`` raising a confusing 'Range "" is invalid'). Shared by the model
    form field and the CSV import form so the protocol/port string is parsed in exactly one place.
    """
    # Imported lazily to avoid pulling the forms layer in at module load.
    from utilities.forms.utils import parse_numeric_range

    protocol = (protocol or '').strip().lower()
    ports_str = (ports_str or '').strip()
    if not ports_str:
        return [f'{protocol}/']
    # parse_numeric_range validates each range against the port bounds (rejecting reversed and
    # out-of-range values before expansion), so a non-empty string always yields >=1 port.
    ports = parse_numeric_range(ports_str, min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX)
    return [f'{protocol}/{port}' for port in ports]
    return None
