from dataclasses import dataclass
import netaddr

from django.utils.translation import gettext_lazy as _

from .constants import *
from .models import Prefix, VLAN

__all__ = (
    'AvailableIPSpace',
    'add_available_vlans',
    'add_requested_prefixes',
    'annotate_ip_space',
    'get_next_available_prefix',
    'rebuild_prefixes',
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
    :param prefix_list: Child prefixes list
    :param show_available: Include available prefixes.
    :param show_assigned: Show assigned prefixes.
    """
    child_prefixes = []

    # Add available prefixes to the table if requested
    if prefix_list and show_available:

        # Find all unallocated space, add fake Prefix objects to child_prefixes.
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
    if prefix.family == 4 and prefix.mask_length < 31 and not prefix.is_pool:
        # Ignore the network and broadcast addresses for non-pool IPv4 prefixes larger than /31
        first_ip_in_prefix = netaddr.IPAddress(prefix.prefix.first + 1)
        last_ip_in_prefix = netaddr.IPAddress(prefix.prefix.last - 1)
    else:
        first_ip_in_prefix = netaddr.IPAddress(prefix.prefix.first)
        last_ip_in_prefix = netaddr.IPAddress(prefix.prefix.last)

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
    vlans.sort(key=lambda v: v.vid if type(v) is VLAN else v['vid'])

    return vlans


def rebuild_prefixes(vrf):
    """
    Rebuild the prefix hierarchy for all prefixes in the specified VRF (or global table).
    """
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
    prefixes = Prefix.objects.filter(vrf=vrf).values('pk', 'prefix')

    # Iterate through all Prefixes in the VRF, growing and shrinking the stack as we go
    for i, p in enumerate(prefixes):

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
