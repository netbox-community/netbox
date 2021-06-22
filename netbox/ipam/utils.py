import netaddr

from .constants import *
from .models import Prefix, VLAN


def add_available_prefixes(parent, prefix_list):
    """
    Create fake Prefix objects for all unallocated space within a prefix.
    """

    # Find all unallocated space
    available_prefixes = netaddr.IPSet(parent) ^ netaddr.IPSet([p.prefix for p in prefix_list])
    available_prefixes = [Prefix(prefix=p, status=None) for p in available_prefixes.iter_cidrs()]

    # Concatenate and sort complete list of children
    prefix_list = list(prefix_list) + available_prefixes
    prefix_list.sort(key=lambda p: p.prefix)

    return prefix_list


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


def add_available_vlans(vlans, vlan_group=None):
    """
    Create fake records for all gaps between used VLANs
    """
    if not vlans:
        return [{
            'vid': VLAN_VID_MIN,
            'vlan_group': vlan_group,
            'available': VLAN_VID_MAX - VLAN_VID_MIN + 1
        }]

    prev_vid = VLAN_VID_MAX
    new_vlans = []
    for vlan in vlans:
        if vlan.vid - prev_vid > 1:
            new_vlans.append({
                'vid': prev_vid + 1,
                'vlan_group': vlan_group,
                'available': vlan.vid - prev_vid - 1,
            })
        prev_vid = vlan.vid

    if vlans[0].vid > VLAN_VID_MIN:
        new_vlans.append({
            'vid': VLAN_VID_MIN,
            'vlan_group': vlan_group,
            'available': vlans[0].vid - VLAN_VID_MIN,
        })
    if prev_vid < VLAN_VID_MAX:
        new_vlans.append({
            'vid': prev_vid + 1,
            'vlan_group': vlan_group,
            'available': VLAN_VID_MAX - prev_vid,
        })

    vlans = list(vlans) + new_vlans
    vlans.sort(key=lambda v: v.vid if type(v) == VLAN else v['vid'])

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
