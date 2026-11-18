"""
Payload factories matching the NDX catalog API's response shapes.
"""
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from ndx.client import HTTP_STATUS_ERRORS, UNAVAILABLE, NDXError, NDXResponse

__all__ = (
    'create_import_record',
    'mock_auth_response',
    'mock_enrichment',
    'mock_enrichment_flags',
    'mock_entry',
    'mock_error_response',
    'mock_manifest_response',
    'mock_pdu_entry',
    'mock_search_response',
)


def mock_entry(vendor_slug='cisco', slug='catalyst-9300', manufacturer='Cisco', model='Catalyst 9300',
               entry_type='device-type', source='community', dtl=None, enrichment=None, enrichment_flags=None,
               **extra):
    """
    Return a catalog entry as served by the device-types detail endpoint.
    """
    if dtl is None:
        dtl = {
            'u_height': 1.0,
            'is_full_depth': True,
            'airflow': 'front-to-rear',
            'weight': 6.5,
            'weight_unit': 'kg',
            'comments': 'Imported from NDX.',
            'interfaces': [
                {'name': 'GigabitEthernet0/0/0', 'type': '1000base-t', 'label': 'Gi0/0/0', 'mgmt_only': True,
                 'description': 'Uplink', 'poe_mode': 'pd', 'poe_type': 'type1-ieee802.3af', 'enabled': False},
                {'name': 'GigabitEthernet0/0/1', 'type': '1000base-t'},
                {'name': 'radio0', 'type': 'ieee802.11ax', 'rf_role': 'ap'},
            ],
            'power-ports': [
                {'name': 'PSU1', 'type': 'iec-60320-c14', 'maximum_draw': 350, 'allocated_draw': 300},
            ],
            'console-ports': [
                {'name': 'Console', 'type': 'rj-45'},
            ],
            'console-server-ports': [
                {'name': 'Serial1', 'type': 'rj-45'},
            ],
            'front-ports': [
                {'name': 'Front1', 'type': '8p8c', 'color': '0000ff', 'positions': 2},
            ],
            'rear-ports': [
                {'name': 'Rear1', 'type': '8p8c', 'positions': 4},
            ],
            'port-mappings': [
                {'front_port': 'Front1', 'front_port_position': 1, 'rear_port': 'Rear1', 'rear_port_position': 2},
            ],
            'module-bays': [
                {'name': 'Network Module 1', 'position': '1', 'label': 'NM1'},
            ],
            'device-bays': [
                {'name': 'Bay 1'},
            ],
            'inventory-items': [
                {'name': 'Storage', 'manufacturer': manufacturer, 'part_id': 'SSD-1TB'},
            ],
        }
    entry = {
        'vendor_slug': vendor_slug,
        'vendor_name': manufacturer,
        'slug': slug,
        'manufacturer': manufacturer,
        'model': model,
        'part_number': 'C9300-24T',
        'type': entry_type,
        'source': source,
        'dtl': dtl,
        **extra,
    }
    if enrichment is not None:
        entry['enrichment'] = enrichment
    if enrichment_flags is not None:
        entry['enrichment_flags'] = enrichment_flags
    return NDXResponse(entry)


def mock_pdu_entry(inlets=(('Input A', 1440), ('Input B', 1440)), **kwargs):
    """
    Return a power distribution unit whose outlets all draw from the first inlet.
    """
    power_ports = [{'name': name, 'type': 'iec-60320-c20', 'maximum_draw': draw} for name, draw in inlets]
    outlets = [
        {'name': f'Outlet {i}', 'type': 'iec-60320-c13', 'power_port': inlets[0][0], 'feed_leg': 'A'}
        for i in range(1, 3)
    ]
    kwargs.setdefault('vendor_slug', 'acme')
    kwargs.setdefault('slug', 'pdu-dual')
    kwargs.setdefault('manufacturer', 'Acme')
    kwargs.setdefault('model', 'PDU-DUAL')
    return mock_entry(dtl={'power-ports': power_ports, 'power-outlets': outlets}, **kwargs)


def mock_enrichment():
    """
    Return the enrichment data included for an entitled token.
    """
    return {
        'thermal': {'tdp_watts': 350, 'airflow_cfm': 65.0, 'cooling_type': 'fans'},
        'lifecycle': {
            'ga_date': '2018-11-01',
            'eol_announced': '2024-01-15',
            'eos_date': '2025-10-31',
            'eosw_date': '2026-10-31',
            'eosec_date': '2027-10-31',
            'last_support_date': '2028-10-31',
        },
        'environmental': {
            'max_operating_temp_c': 45.0,
            'min_operating_temp_c': 0.0,
            'max_operating_humidity': 95,
            'min_operating_humidity': 5,
            'max_operating_altitude_m': 3000,
            'ingress_protection': 'IP20',
            'mtbf_hours': 250000,
        },
        'operational': {'typical_power_draw_watts': 250, 'max_power_draw_watts': 350, 'noise_level_dba': 42.5},
        'extensions': {
            'platform': {'nos': 'IOS-XE', 'nos_family': 'IOS', 'api_types': ['netconf', 'restconf']},
            'snmp': {'sys_object_id': '1.3.6.1.4.1.9.1.2745', 'vendor_oid_prefix': '1.3.6.1.4.1.9'},
        },
        'provenance': [
            {
                'field': 'lifecycle.ga_date',
                'source': 'https://cisco.com/eol',
                'type': 'vendor_eol_bulletin',
                'confidence': 'high',
                'retrieved': '2024-01-15',
                'note': 'GA date from the vendor EoL bulletin.',
            },
            {
                'field': 'thermal.tdp_watts',
                'source': 'https://cisco.com/datasheet',
                'type': 'vendor_datasheet',
                'confidence': 'medium-high',
                'retrieved': '2024-02-20T09:30:00Z',
                'note': 'Rated draw, not measured.',
            },
        ],
    }


def mock_enrichment_flags():
    return {
        'lifecycle': True,
        'thermal': True,
        'environmental': True,
        'operational': True,
        'platform': True,
        'snmp': True,
    }


def mock_search_response(entries=(), total=None):
    return NDXResponse({
        'results': list(entries),
        'next_cursor': None,
        'total': len(entries) if total is None else total,
    })


def mock_manifest_response(vendor_checksums=None):
    return NDXResponse({'vendor_checksums': vendor_checksums or {}})


def mock_auth_response(tier='free'):
    return NDXResponse({'authenticated': True, 'tier': tier})


def mock_error_response(status=401):
    """
    Return the response produced by a failed NDX API request (status None for an unreachable API).
    """
    return NDXResponse(error=NDXError(kind=HTTP_STATUS_ERRORS.get(status, UNAVAILABLE), status=status))


def create_import_record(obj, ndx_id, **kwargs):
    """
    Create an ImportRecord tracking the given object.
    """
    from ndx.models import ImportRecord

    vendor_slug = ndx_id.split('/')[0]
    kwargs.setdefault('entry_type', 'device-type')
    kwargs.setdefault('source', 'community')
    kwargs.setdefault('checksum', 'abc123')
    kwargs.setdefault('last_imported', timezone.now())
    return ImportRecord.objects.create(
        object_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
        ndx_id=ndx_id,
        vendor_slug=vendor_slug,
        **kwargs,
    )
