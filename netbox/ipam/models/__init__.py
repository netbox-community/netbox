# Ensure that VRFs are imported before IPs/prefixes so dumpdata & loaddata work correctly
from .fhrp import *
from .vrfs import *
from .ip import *
from .l2vpn import *
from .services import *
from .vlans import *

__all__ = (
    'ASN',
    'Aggregate',
    'IPAddress',
    'IPRange',
    'FHRPGroup',
    'FHRPGroupAssignment',
    'L2VPN',
    'L2VPNTermination',
    'Prefix',
    'RIR',
    'Role',
    'RouteTarget',
    'Service',
    'ServiceTemplate',
    'VLAN',
    'VLANGroup',
    'VRF',
)
