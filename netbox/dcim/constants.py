
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

# Rack statuses
RACK_STATUS_RESERVED = 0
RACK_STATUS_AVAILABLE = 1
RACK_STATUS_PLANNED = 2
RACK_STATUS_ACTIVE = 3
RACK_STATUS_DEPRECATED = 4
RACK_STATUS_CHOICES = [
    [RACK_STATUS_ACTIVE, 'Active'],
    [RACK_STATUS_PLANNED, 'Planned'],
    [RACK_STATUS_RESERVED, 'Reserved'],
    [RACK_STATUS_AVAILABLE, 'Available'],
    [RACK_STATUS_DEPRECATED, 'Deprecated'],
]

# Device rack position
DEVICE_POSITION_CHOICES = [
    # Rack.u_height is limited to 100
    (i, 'Unit {}'.format(i)) for i in range(1, 101)
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
IFACE_FF_200GE_CFP2 = 1650
IFACE_FF_200GE_QSFP56 = 1700
IFACE_FF_400GE_QSFP_DD = 1750
# Wireless
IFACE_FF_80211A = 2600
IFACE_FF_80211G = 2610
IFACE_FF_80211N = 2620
IFACE_FF_80211AC = 2630
IFACE_FF_80211AD = 2640
# Cellular
IFACE_FF_GSM = 2810
IFACE_FF_CDMA = 2820
IFACE_FF_LTE = 2830
# SONET
IFACE_FF_SONET_OC3 = 6100
IFACE_FF_SONET_OC12 = 6200
IFACE_FF_SONET_OC48 = 6300
IFACE_FF_SONET_OC192 = 6400
IFACE_FF_SONET_OC768 = 6500
IFACE_FF_SONET_OC1920 = 6600
IFACE_FF_SONET_OC3840 = 6700
# Fibrechannel
IFACE_FF_1GFC_SFP = 3010
IFACE_FF_2GFC_SFP = 3020
IFACE_FF_4GFC_SFP = 3040
IFACE_FF_8GFC_SFP_PLUS = 3080
IFACE_FF_16GFC_SFP_PLUS = 3160
IFACE_FF_32GFC_SFP28 = 3320
IFACE_FF_128GFC_QSFP28 = 3400
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
            [IFACE_FF_200GE_CFP2, 'CFP2 (200GE)'],
            [IFACE_FF_100GE_CFP4, 'CFP4 (100GE)'],
            [IFACE_FF_100GE_CPAK, 'Cisco CPAK (100GE)'],
            [IFACE_FF_100GE_QSFP28, 'QSFP28 (100GE)'],
            [IFACE_FF_200GE_QSFP56, 'QSFP56 (200GE)'],
            [IFACE_FF_400GE_QSFP_DD, 'QSFP-DD (400GE)'],
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
        'Cellular',
        [
            [IFACE_FF_GSM, 'GSM'],
            [IFACE_FF_CDMA, 'CDMA'],
            [IFACE_FF_LTE, 'LTE'],
        ]
    ],
    [
        'SONET',
        [
            [IFACE_FF_SONET_OC3, 'OC-3/STM-1'],
            [IFACE_FF_SONET_OC12, 'OC-12/STM-4'],
            [IFACE_FF_SONET_OC48, 'OC-48/STM-16'],
            [IFACE_FF_SONET_OC192, 'OC-192/STM-64'],
            [IFACE_FF_SONET_OC768, 'OC-768/STM-256'],
            [IFACE_FF_SONET_OC1920, 'OC-1920/STM-640'],
            [IFACE_FF_SONET_OC3840, 'OC-3840/STM-1234'],
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
            [IFACE_FF_32GFC_SFP28, 'SFP28 (32GFC)'],
            [IFACE_FF_128GFC_QSFP28, 'QSFP28 (128GFC)'],
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

# Pass-through port types
PORT_TYPE_8P8C = 1000
PORT_TYPE_110_PUNCH = 1100
PORT_TYPE_ST = 2000
PORT_TYPE_SC = 2100
PORT_TYPE_SC_APC = 2110
PORT_TYPE_FC = 2200
PORT_TYPE_LC = 2300
PORT_TYPE_LC_APC = 2310
PORT_TYPE_MTRJ = 2400
PORT_TYPE_MPO = 2500
PORT_TYPE_LSH = 2600
PORT_TYPE_LSH_APC = 2610
PORT_TYPE_CHOICES = [
    [
        'Copper',
        [
            [PORT_TYPE_8P8C, '8P8C'],
            [PORT_TYPE_110_PUNCH, '110 Punch'],
        ],
    ],
    [
        'Fiber Optic',
        [
            [PORT_TYPE_FC, 'FC'],
            [PORT_TYPE_LC, 'LC'],
            [PORT_TYPE_LC_APC, 'LC/APC'],
            [PORT_TYPE_LSH, 'LSH'],
            [PORT_TYPE_LSH_APC, 'LSH/APC'],
            [PORT_TYPE_MPO, 'MPO'],
            [PORT_TYPE_MTRJ, 'MTRJ'],
            [PORT_TYPE_SC, 'SC'],
            [PORT_TYPE_SC_APC, 'SC/APC'],
            [PORT_TYPE_ST, 'ST'],
        ]
    ]
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

# Bootstrap CSS classes for device/rack statuses
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

# Cable endpoint types
CABLE_TERMINATION_TYPES = [
    'consoleport', 'consoleserverport', 'interface', 'poweroutlet', 'powerport', 'frontport', 'rearport',
]

# Cable types
CABLE_TYPE_CAT3 = 1300
CABLE_TYPE_CAT5 = 1500
CABLE_TYPE_CAT5E = 1510
CABLE_TYPE_CAT6 = 1600
CABLE_TYPE_CAT6A = 1610
CABLE_TYPE_CAT7 = 1700
CABLE_TYPE_DAC_ACTIVE = 1800
CABLE_TYPE_DAC_PASSIVE = 1810
CABLE_TYPE_MMF = 3000
CABLE_TYPE_MMF_OM1 = 3010
CABLE_TYPE_MMF_OM2 = 3020
CABLE_TYPE_MMF_OM3 = 3030
CABLE_TYPE_MMF_OM4 = 3040
CABLE_TYPE_SMF = 3500
CABLE_TYPE_SMF_OS1 = 3510
CABLE_TYPE_SMF_OS2 = 3520
CABLE_TYPE_AOC = 3800
CABLE_TYPE_POWER = 5000
CABLE_TYPE_CHOICES = (
    (
        'Copper', (
            (CABLE_TYPE_CAT3, 'CAT3'),
            (CABLE_TYPE_CAT5, 'CAT5'),
            (CABLE_TYPE_CAT5E, 'CAT5e'),
            (CABLE_TYPE_CAT6, 'CAT6'),
            (CABLE_TYPE_CAT6A, 'CAT6a'),
            (CABLE_TYPE_CAT7, 'CAT7'),
            (CABLE_TYPE_DAC_ACTIVE, 'Direct Attach Copper (Active)'),
            (CABLE_TYPE_DAC_PASSIVE, 'Direct Attach Copper (Passive)'),
        ),
    ),
    (
        'Fiber', (
            (CABLE_TYPE_MMF, 'Multimode Fiber'),
            (CABLE_TYPE_MMF_OM1, 'Multimode Fiber (OM1)'),
            (CABLE_TYPE_MMF_OM2, 'Multimode Fiber (OM2)'),
            (CABLE_TYPE_MMF_OM3, 'Multimode Fiber (OM3)'),
            (CABLE_TYPE_MMF_OM4, 'Multimode Fiber (OM4)'),
            (CABLE_TYPE_SMF, 'Singlemode Fiber'),
            (CABLE_TYPE_SMF_OS1, 'Singlemode Fiber (OS1)'),
            (CABLE_TYPE_SMF_OS2, 'Singlemode Fiber (OS2)'),
            (CABLE_TYPE_AOC, 'Active Optical Cabling (AOC)'),
        ),
    ),
    (CABLE_TYPE_POWER, 'Power'),
)

CABLE_TERMINATION_TYPE_CHOICES = {
    # (API endpoint, human-friendly name)
    'consoleport': ('console-ports', 'Console port'),
    'consoleserverport': ('console-server-ports', 'Console server port'),
    'powerport': ('power-ports', 'Power port'),
    'poweroutlet': ('power-outlets', 'Power outlet'),
    'interface': ('interfaces', 'Interface'),
    'frontport': ('front-ports', 'Front panel port'),
    'rearport': ('rear-ports', 'Rear panel port'),
}

COMPATIBLE_TERMINATION_TYPES = {
    'consoleport': ['consoleserverport', 'frontport', 'rearport'],
    'consoleserverport': ['consoleport', 'frontport', 'rearport'],
    'powerport': ['poweroutlet', 'powerfeed'],
    'poweroutlet': ['powerport'],
    'interface': ['interface', 'circuittermination', 'frontport', 'rearport'],
    'frontport': ['consoleport', 'consoleserverport', 'interface', 'frontport', 'rearport', 'circuittermination'],
    'rearport': ['consoleport', 'consoleserverport', 'interface', 'frontport', 'rearport', 'circuittermination'],
    'circuittermination': ['interface', 'frontport', 'rearport'],
}

LENGTH_UNIT_METER = 1200
LENGTH_UNIT_CENTIMETER = 1100
LENGTH_UNIT_MILLIMETER = 1000
LENGTH_UNIT_FOOT = 2100
LENGTH_UNIT_INCH = 2000
CABLE_LENGTH_UNIT_CHOICES = (
    (LENGTH_UNIT_METER, 'Meters'),
    (LENGTH_UNIT_CENTIMETER, 'Centimeters'),
    (LENGTH_UNIT_FOOT, 'Feet'),
    (LENGTH_UNIT_INCH, 'Inches'),
)
RACK_DIMENSION_UNIT_CHOICES = (
    (LENGTH_UNIT_MILLIMETER, 'Millimeters'),
    (LENGTH_UNIT_INCH, 'Inches'),
)

# Power feeds
POWERFEED_TYPE_PRIMARY = 1
POWERFEED_TYPE_REDUNDANT = 2
POWERFEED_TYPE_CHOICES = (
    (POWERFEED_TYPE_PRIMARY, 'Primary'),
    (POWERFEED_TYPE_REDUNDANT, 'Redundant'),
)
POWERFEED_SUPPLY_AC = 1
POWERFEED_SUPPLY_DC = 2
POWERFEED_SUPPLY_CHOICES = (
    (POWERFEED_SUPPLY_AC, 'AC'),
    (POWERFEED_SUPPLY_DC, 'DC'),
)
POWERFEED_PHASE_SINGLE = 1
POWERFEED_PHASE_3PHASE = 3
POWERFEED_PHASE_CHOICES = (
    (POWERFEED_PHASE_SINGLE, 'Single phase'),
    (POWERFEED_PHASE_3PHASE, 'Three-phase'),
)
POWERFEED_STATUS_OFFLINE = 0
POWERFEED_STATUS_ACTIVE = 1
POWERFEED_STATUS_PLANNED = 2
POWERFEED_STATUS_FAILED = 4
POWERFEED_STATUS_CHOICES = (
    (POWERFEED_STATUS_ACTIVE, 'Active'),
    (POWERFEED_STATUS_OFFLINE, 'Offline'),
    (POWERFEED_STATUS_PLANNED, 'Planned'),
    (POWERFEED_STATUS_FAILED, 'Failed'),
)
