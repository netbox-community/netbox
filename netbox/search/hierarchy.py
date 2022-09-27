from circuits.search_indexes import CIRCUIT_SEARCH_TYPES
from dcim.search_indexes import DCIM_SEARCH_TYPES
from extras.search_indexes import JOURNAL_SEARCH_TYPES
from ipam.search_indexes import IPAM_SEARCH_TYPES
from tenancy.search_indexes import TENANCY_SEARCH_TYPES
from virtualization.search_indexes import VIRTUALIZATION_SEARCH_TYPES
from wireless.search_indexes import WIRELESS_SEARCH_TYPES

SEARCH_TYPE_HIERARCHY = {
    'Circuits': CIRCUIT_SEARCH_TYPES,
    'DCIM': DCIM_SEARCH_TYPES,
    'IPAM': IPAM_SEARCH_TYPES,
    'Tenancy': TENANCY_SEARCH_TYPES,
    'Virtualization': VIRTUALIZATION_SEARCH_TYPES,
    'Wireless': WIRELESS_SEARCH_TYPES,
    'Journal': JOURNAL_SEARCH_TYPES,
}


def build_search_types():
    result = dict()

    for app_types in SEARCH_TYPE_HIERARCHY.values():
        for name, items in app_types.items():
            result[name] = items

    return result


SEARCH_TYPES = build_search_types()
