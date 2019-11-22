from .choices import InterfaceTypeChoices


#
# Interface type groups
#

VIRTUAL_IFACE_TYPES = [
    InterfaceTypeChoices.TYPE_VIRTUAL,
    InterfaceTypeChoices.TYPE_LAG,
]

WIRELESS_IFACE_TYPES = [
    InterfaceTypeChoices.TYPE_80211A,
    InterfaceTypeChoices.TYPE_80211G,
    InterfaceTypeChoices.TYPE_80211N,
    InterfaceTypeChoices.TYPE_80211AC,
    InterfaceTypeChoices.TYPE_80211AD,
]

NONCONNECTABLE_IFACE_TYPES = VIRTUAL_IFACE_TYPES + WIRELESS_IFACE_TYPES


# Pass-through port types
PORT_TYPE_8P8C = 1000
PORT_TYPE_110_PUNCH = 1100
PORT_TYPE_BNC = 1200
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
            [PORT_TYPE_BNC, 'BNC'],
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
DEVICE_STATUS_DECOMMISSIONING = 6
DEVICE_STATUS_CHOICES = [
    [DEVICE_STATUS_ACTIVE, 'Active'],
    [DEVICE_STATUS_OFFLINE, 'Offline'],
    [DEVICE_STATUS_PLANNED, 'Planned'],
    [DEVICE_STATUS_STAGED, 'Staged'],
    [DEVICE_STATUS_FAILED, 'Failed'],
    [DEVICE_STATUS_INVENTORY, 'Inventory'],
    [DEVICE_STATUS_DECOMMISSIONING, 'Decommissioning'],
]

# Bootstrap CSS classes for device/rack statuses
STATUS_CLASSES = {
    0: 'warning',
    1: 'success',
    2: 'info',
    3: 'primary',
    4: 'danger',
    5: 'default',
    6: 'warning',
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
    'circuittermination',
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
CABLE_TYPE_COAXIAL = 1900
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
            (CABLE_TYPE_COAXIAL, 'Coaxial'),
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
POWERFEED_LEG_A = 1
POWERFEED_LEG_B = 2
POWERFEED_LEG_C = 3
POWERFEED_LEG_CHOICES = (
    (POWERFEED_LEG_A, 'A'),
    (POWERFEED_LEG_B, 'B'),
    (POWERFEED_LEG_C, 'C'),
)
