from __future__ import unicode_literals


# Rack types
RACK_TYPE_2POST = 100
RACK_TYPE_4POST = 200
RACK_TYPE_CABINET = 300
RACK_TYPE_WALLFRAME = 1000
RACK_TYPE_WALLCABINET = 1100
RACK_TYPE_CHOICES = (
    (RACK_TYPE_2POST, '2-post frame'),
    (RACK_TYPE_4POST, '4-post frame'),
    (RACK_TYPE_CABINET, '4-post cabinet'),
    (RACK_TYPE_WALLFRAME, 'Wall-mounted frame'),
    (RACK_TYPE_WALLCABINET, 'Wall-mounted cabinet'),
)

# Rack widths
RACK_WIDTH_19IN = 19
RACK_WIDTH_23IN = 23
RACK_WIDTH_CHOICES = (
    (RACK_WIDTH_19IN, '19 inches'),
    (RACK_WIDTH_23IN, '23 inches'),
)

# Rack faces
RACK_FACE_FRONT = 0
RACK_FACE_REAR = 1
RACK_FACE_CHOICES = [
    [RACK_FACE_FRONT, 'Front'],
    [RACK_FACE_REAR, 'Rear'],
]

# Parent/child device roles
SUBDEVICE_ROLE_PARENT = True
SUBDEVICE_ROLE_CHILD = False
SUBDEVICE_ROLE_CHOICES = (
    (None, 'None'),
    (SUBDEVICE_ROLE_PARENT, 'Parent'),
    (SUBDEVICE_ROLE_CHILD, 'Child'),
)

# Interface ordering schemes (for device types)
IFACE_ORDERING_POSITION = 1
IFACE_ORDERING_NAME = 2
IFACE_ORDERING_CHOICES = [
    [IFACE_ORDERING_POSITION, 'Slot/position'],
    [IFACE_ORDERING_NAME, 'Name (alphabetically)']
]

# Interface form factors
# Virtual
IFACE_FF_VIRTUAL = 0
IFACE_FF_LAG = 200
# Ethernet
IFACE_FF_100ME_FIXED = 800
IFACE_FF_1GE_FIXED = 1000
IFACE_FF_1GE_GBIC = 1050
IFACE_FF_1GE_SFP = 1100
IFACE_FF_10GE_FIXED = 1150
IFACE_FF_10GE_CX4 = 1170
IFACE_FF_10GE_SFP_PLUS = 1200
IFACE_FF_10GE_XFP = 1300
IFACE_FF_10GE_XENPAK = 1310
IFACE_FF_10GE_X2 = 1320
IFACE_FF_25GE_SFP28 = 1350
IFACE_FF_40GE_QSFP_PLUS = 1400
IFACE_FF_100GE_CFP = 1500
IFACE_FF_100GE_CFP2 = 1510
IFACE_FF_100GE_CFP4 = 1520
IFACE_FF_100GE_CPAK = 1550
IFACE_FF_100GE_QSFP28 = 1600
# Wireless
IFACE_FF_80211A = 2600
IFACE_FF_80211G = 2610
IFACE_FF_80211N = 2620
IFACE_FF_80211AC = 2630
IFACE_FF_80211AD = 2640
# Fibrechannel
IFACE_FF_1GFC_SFP = 3010
IFACE_FF_2GFC_SFP = 3020
IFACE_FF_4GFC_SFP = 3040
IFACE_FF_8GFC_SFP_PLUS = 3080
IFACE_FF_16GFC_SFP_PLUS = 3160
# Serial
IFACE_FF_T1 = 4000
IFACE_FF_E1 = 4010
IFACE_FF_T3 = 4040
IFACE_FF_E3 = 4050
# Stacking
IFACE_FF_STACKWISE = 5000
IFACE_FF_STACKWISE_PLUS = 5050
IFACE_FF_FLEXSTACK = 5100
IFACE_FF_FLEXSTACK_PLUS = 5150
IFACE_FF_JUNIPER_VCP = 5200
IFACE_FF_SUMMITSTACK = 5300
IFACE_FF_SUMMITSTACK128 = 5310
IFACE_FF_SUMMITSTACK256 = 5320
IFACE_FF_SUMMITSTACK512 = 5330

# Other
IFACE_FF_OTHER = 32767

IFACE_FF_CHOICES = [
    [
        'Virtual interfaces',
        [
            [IFACE_FF_VIRTUAL, 'Virtual'],
            [IFACE_FF_LAG, 'Link Aggregation Group (LAG)'],
        ],
    ],
    [
        'Ethernet (fixed)',
        [
            [IFACE_FF_100ME_FIXED, '100BASE-TX (10/100ME)'],
            [IFACE_FF_1GE_FIXED, '1000BASE-T (1GE)'],
            [IFACE_FF_10GE_FIXED, '10GBASE-T (10GE)'],
            [IFACE_FF_10GE_CX4, '10GBASE-CX4 (10GE)'],
        ]
    ],
    [
        'Ethernet (modular)',
        [
            [IFACE_FF_1GE_GBIC, 'GBIC (1GE)'],
            [IFACE_FF_1GE_SFP, 'SFP (1GE)'],
            [IFACE_FF_10GE_SFP_PLUS, 'SFP+ (10GE)'],
            [IFACE_FF_10GE_XFP, 'XFP (10GE)'],
            [IFACE_FF_10GE_XENPAK, 'XENPAK (10GE)'],
            [IFACE_FF_10GE_X2, 'X2 (10GE)'],
            [IFACE_FF_25GE_SFP28, 'SFP28 (25GE)'],
            [IFACE_FF_40GE_QSFP_PLUS, 'QSFP+ (40GE)'],
            [IFACE_FF_100GE_CFP, 'CFP (100GE)'],
            [IFACE_FF_100GE_CFP2, 'CFP2 (100GE)'],
            [IFACE_FF_100GE_CFP4, 'CFP4 (100GE)'],
            [IFACE_FF_100GE_CPAK, 'Cisco CPAK (100GE)'],
            [IFACE_FF_100GE_QSFP28, 'QSFP28 (100GE)'],
        ]
    ],
    [
        'Wireless',
        [
            [IFACE_FF_80211A, 'IEEE 802.11a'],
            [IFACE_FF_80211G, 'IEEE 802.11b/g'],
            [IFACE_FF_80211N, 'IEEE 802.11n'],
            [IFACE_FF_80211AC, 'IEEE 802.11ac'],
            [IFACE_FF_80211AD, 'IEEE 802.11ad'],
        ]
    ],
    [
        'FibreChannel',
        [
            [IFACE_FF_1GFC_SFP, 'SFP (1GFC)'],
            [IFACE_FF_2GFC_SFP, 'SFP (2GFC)'],
            [IFACE_FF_4GFC_SFP, 'SFP (4GFC)'],
            [IFACE_FF_8GFC_SFP_PLUS, 'SFP+ (8GFC)'],
            [IFACE_FF_16GFC_SFP_PLUS, 'SFP+ (16GFC)'],
        ]
    ],
    [
        'Serial',
        [
            [IFACE_FF_T1, 'T1 (1.544 Mbps)'],
            [IFACE_FF_E1, 'E1 (2.048 Mbps)'],
            [IFACE_FF_T3, 'T3 (45 Mbps)'],
            [IFACE_FF_E3, 'E3 (34 Mbps)'],
        ]
    ],
    [
        'Stacking',
        [
            [IFACE_FF_STACKWISE, 'Cisco StackWise'],
            [IFACE_FF_STACKWISE_PLUS, 'Cisco StackWise Plus'],
            [IFACE_FF_FLEXSTACK, 'Cisco FlexStack'],
            [IFACE_FF_FLEXSTACK_PLUS, 'Cisco FlexStack Plus'],
            [IFACE_FF_JUNIPER_VCP, 'Juniper VCP'],
            [IFACE_FF_SUMMITSTACK, 'Extreme SummitStack'],
            [IFACE_FF_SUMMITSTACK128, 'Extreme SummitStack-128'],
            [IFACE_FF_SUMMITSTACK256, 'Extreme SummitStack-256'],
            [IFACE_FF_SUMMITSTACK512, 'Extreme SummitStack-512'],
        ]
    ],
    [
        'Other',
        [
            [IFACE_FF_OTHER, 'Other'],
        ]
    ],
]

VIRTUAL_IFACE_TYPES = [
    IFACE_FF_VIRTUAL,
    IFACE_FF_LAG,
]

WIRELESS_IFACE_TYPES = [
    IFACE_FF_80211A,
    IFACE_FF_80211G,
    IFACE_FF_80211N,
    IFACE_FF_80211AC,
    IFACE_FF_80211AD,
]

NONCONNECTABLE_IFACE_TYPES = VIRTUAL_IFACE_TYPES + WIRELESS_IFACE_TYPES

IFACE_MODE_ACCESS = 100
IFACE_MODE_TAGGED = 200
IFACE_MODE_TAGGED_ALL = 300
IFACE_MODE_CHOICES = [
    [IFACE_MODE_ACCESS, 'Access'],
    [IFACE_MODE_TAGGED, 'Tagged'],
    [IFACE_MODE_TAGGED_ALL, 'Tagged All'],
]

# Device statuses
DEVICE_STATUS_OFFLINE = 0
DEVICE_STATUS_ACTIVE = 1
DEVICE_STATUS_PLANNED = 2
DEVICE_STATUS_STAGED = 3
DEVICE_STATUS_FAILED = 4
DEVICE_STATUS_INVENTORY = 5
DEVICE_STATUS_CHOICES = [
    [DEVICE_STATUS_ACTIVE, 'Active'],
    [DEVICE_STATUS_OFFLINE, 'Offline'],
    [DEVICE_STATUS_PLANNED, 'Planned'],
    [DEVICE_STATUS_STAGED, 'Staged'],
    [DEVICE_STATUS_FAILED, 'Failed'],
    [DEVICE_STATUS_INVENTORY, 'Inventory'],
]

# Site statuses
SITE_STATUS_ACTIVE = 1
SITE_STATUS_PLANNED = 2
SITE_STATUS_RETIRED = 4
SITE_STATUS_CHOICES = [
    [SITE_STATUS_ACTIVE, 'Active'],
    [SITE_STATUS_PLANNED, 'Planned'],
    [SITE_STATUS_RETIRED, 'Retired'],
]

# Bootstrap CSS classes for device statuses
STATUS_CLASSES = {
    0: 'warning',
    1: 'success',
    2: 'info',
    3: 'primary',
    4: 'danger',
    5: 'default',
}

# Console/power/interface connection statuses
CONNECTION_STATUS_PLANNED = False
CONNECTION_STATUS_CONNECTED = True
CONNECTION_STATUS_CHOICES = [
    [CONNECTION_STATUS_PLANNED, 'Planned'],
    [CONNECTION_STATUS_CONNECTED, 'Connected'],
]

# Platform -> RPC client mappings
RPC_CLIENT_JUNIPER_JUNOS = 'juniper-junos'
RPC_CLIENT_CISCO_IOS = 'cisco-ios'
RPC_CLIENT_OPENGEAR = 'opengear'
RPC_CLIENT_CHOICES = [
    [RPC_CLIENT_JUNIPER_JUNOS, 'Juniper Junos (NETCONF)'],
    [RPC_CLIENT_CISCO_IOS, 'Cisco IOS (SSH)'],
    [RPC_CLIENT_OPENGEAR, 'Opengear (SSH)'],
]
