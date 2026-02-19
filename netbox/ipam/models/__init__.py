# Ensure that VRFs are imported before IPs/prefixes so dumpdata & loaddata work correctly
from .asns import *
from .fhrp import *
from .ip import *
from .services import *
from .vlans import *
from .vrfs import *
