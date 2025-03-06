import netaddr

from .constants import *
from .models import Prefix, VLAN

__all__ = (
    'add_available_ipaddresses',
    'add_available_vlans',
    'add_requested_prefixes',
    'get_next_available_prefix',
    'rebuild_prefixes',
)


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


def add_available_ipaddresses(prefix, ipaddress_list, is_pool=False):
    """
    Annotate ranges of available IP addresses within a given prefix. If is_pool is True, the first and last IP will be
    considered usable (regardless of mask length).
    """

    output = []
    prev_ip = None

    # Ignore the network and broadcast addresses for non-pool IPv4 prefixes larger than /31.
    if prefix.version == 4 and prefix.prefixlen < 31 and not is_pool:
        first_ip_in_prefix = netaddr.IPAddress(prefix.first + 1)
        last_ip_in_prefix = netaddr.IPAddress(prefix.last - 1)
    else:
        first_ip_in_prefix = netaddr.IPAddress(prefix.first)
        last_ip_in_prefix = netaddr.IPAddress(prefix.last)

    if not ipaddress_list:
        return [(
            int(last_ip_in_prefix - first_ip_in_prefix + 1),
            '{}/{}'.format(first_ip_in_prefix, prefix.prefixlen)
        )]

    # Account for any available IPs before the first real IP
    if ipaddress_list[0].address.ip > first_ip_in_prefix:
        skipped_count = int(ipaddress_list[0].address.ip - first_ip_in_prefix)
        first_skipped = '{}/{}'.format(first_ip_in_prefix, prefix.prefixlen)
        output.append((skipped_count, first_skipped))

    # Iterate through existing IPs and annotate free ranges
    for ip in ipaddress_list:
        if prev_ip:
            diff = int(ip.address.ip - prev_ip.address.ip)
            if diff > 1:
                first_skipped = '{}/{}'.format(prev_ip.address.ip + 1, prefix.prefixlen)
                output.append((diff - 1, first_skipped))
        output.append(ip)
        prev_ip = ip

    # Include any remaining available IPs
    if prev_ip.address.ip < last_ip_in_prefix:
        skipped_count = int(last_ip_in_prefix - prev_ip.address.ip)
        first_skipped = '{}/{}'.format(prev_ip.address.ip + 1, prefix.prefixlen)
        output.append((skipped_count, first_skipped))

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
    if prev_vid < max_vid:
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
