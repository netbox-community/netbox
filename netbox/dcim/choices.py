from django.utils.translation import gettext_lazy as _

from utilities.choices import Choice, ChoiceSet

#
# Sites
#


class SiteStatusChoices(ChoiceSet):
    key = 'Site.status'

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_RETIRED = 'retired'

    CHOICES = [
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_STAGING, _('Staging'), color='blue', description=_('Being prepared for deployment')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Currently in service')),
        Choice(
            STATUS_DECOMMISSIONING, _('Decommissioning'), color='yellow', description=_('Being removed from service')
        ),
        Choice(STATUS_RETIRED, _('Retired'), color='red', description=_('No longer in service')),
    ]


#
# Locations
#

class LocationStatusChoices(ChoiceSet):
    key = 'Location.status'

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_RETIRED = 'retired'

    CHOICES = [
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_STAGING, _('Staging'), color='blue', description=_('Being prepared for deployment')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Currently in service')),
        Choice(
            STATUS_DECOMMISSIONING, _('Decommissioning'), color='yellow', description=_('Being removed from service')
        ),
        Choice(STATUS_RETIRED, _('Retired'), color='red', description=_('No longer in service')),
    ]


#
# Racks
#

class RackFormFactorChoices(ChoiceSet):

    TYPE_2POST = '2-post-frame'
    TYPE_4POST = '4-post-frame'
    TYPE_CABINET = '4-post-cabinet'
    TYPE_WALLFRAME = 'wall-frame'
    TYPE_WALLFRAME_VERTICAL = 'wall-frame-vertical'
    TYPE_WALLCABINET = 'wall-cabinet'
    TYPE_WALLCABINET_VERTICAL = 'wall-cabinet-vertical'

    CHOICES = (
        Choice(TYPE_2POST, _('2-post frame'), description=_('Open two-post relay rack')),
        Choice(TYPE_4POST, _('4-post frame'), description=_('Open four-post rack')),
        Choice(TYPE_CABINET, _('4-post cabinet'), description=_('Enclosed four-post cabinet')),
        Choice(TYPE_WALLFRAME, _('Wall-mounted frame'), description=_('Open frame mounted to a wall')),
        Choice(
            TYPE_WALLFRAME_VERTICAL,
            _('Wall-mounted frame (vertical)'),
            description=_('Wall-mounted frame with vertical rail orientation'),
        ),
        Choice(TYPE_WALLCABINET, _('Wall-mounted cabinet'), description=_('Enclosed cabinet mounted to a wall')),
        Choice(
            TYPE_WALLCABINET_VERTICAL,
            _('Wall-mounted cabinet (vertical)'),
            description=_('Wall-mounted cabinet with vertical rail orientation'),
        ),
    )


class RackWidthChoices(ChoiceSet):

    WIDTH_10IN = 10
    WIDTH_19IN = 19
    WIDTH_21IN = 21
    WIDTH_23IN = 23

    CHOICES = (
        Choice(WIDTH_10IN, _('{n} inches').format(n=10)),
        Choice(WIDTH_19IN, _('{n} inches').format(n=19)),
        Choice(WIDTH_21IN, _('{n} inches').format(n=21)),
        Choice(WIDTH_23IN, _('{n} inches').format(n=23)),
    )


class RackStatusChoices(ChoiceSet):
    key = 'Rack.status'

    STATUS_RESERVED = 'reserved'
    STATUS_AVAILABLE = 'available'
    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        Choice(STATUS_RESERVED, _('Reserved'), color='yellow', description=_('Set aside for a specific purpose')),
        Choice(STATUS_AVAILABLE, _('Available'), color='green', description=_('Available for use')),
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_ACTIVE, _('Active'), color='blue', description=_('Currently in service')),
        Choice(STATUS_DEPRECATED, _('Deprecated'), color='red', description=_('No longer recommended for use')),
    ]


class RackDimensionUnitChoices(ChoiceSet):

    UNIT_MILLIMETER = 'mm'
    UNIT_INCH = 'in'

    CHOICES = (
        Choice(UNIT_MILLIMETER, _('Millimeters')),
        Choice(UNIT_INCH, _('Inches')),
    )


class RackElevationDetailRenderChoices(ChoiceSet):

    RENDER_JSON = 'json'
    RENDER_SVG = 'svg'

    CHOICES = (
        Choice(RENDER_JSON, 'json'),
        Choice(RENDER_SVG, 'svg')
    )


class RackAirflowChoices(ChoiceSet):
    key = 'Rack.airflow'

    FRONT_TO_REAR = 'front-to-rear'
    REAR_TO_FRONT = 'rear-to-front'

    CHOICES = [
        Choice(FRONT_TO_REAR, _('Front to rear')),
        Choice(REAR_TO_FRONT, _('Rear to front')),
    ]


#
# Rack reservations
#

class RackReservationStatusChoices(ChoiceSet):
    key = 'RackReservation.status'

    STATUS_PENDING = 'pending'
    STATUS_ACTIVE = 'active'
    STATUS_STALE = 'stale'

    CHOICES = [
        Choice(STATUS_PENDING, _('Pending'), color='cyan', description=_('Awaiting confirmation')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Currently in effect')),
        Choice(STATUS_STALE, _('Stale'), color='orange', description=_('No longer valid or in use')),
    ]


#
# DeviceTypes
#

class SubdeviceRoleChoices(ChoiceSet):

    ROLE_PARENT = 'parent'
    ROLE_CHILD = 'child'

    CHOICES = (
        Choice(ROLE_PARENT, _('Parent'), description=_('Houses child devices in its bays')),
        Choice(ROLE_CHILD, _('Child'), description=_('Installed within a parent device bay')),
    )


#
# Devices
#

class DeviceFaceChoices(ChoiceSet):

    FACE_FRONT = 'front'
    FACE_REAR = 'rear'

    CHOICES = (
        Choice(FACE_FRONT, _('Front')),
        Choice(FACE_REAR, _('Rear')),
    )


class DeviceStatusChoices(ChoiceSet):
    key = 'Device.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_INVENTORY = 'inventory'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        Choice(STATUS_OFFLINE, _('Offline'), color='gray', description=_('Installed but not currently in service')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Fully operational and in service')),
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_STAGED, _('Staged'), color='blue', description=_('Installed and being prepared for service')),
        Choice(STATUS_FAILED, _('Failed'), color='red', description=_('Malfunctioning or out of service')),
        Choice(STATUS_INVENTORY, _('Inventory'), color='purple', description=_('In inventory but not yet deployed')),
        Choice(
            STATUS_DECOMMISSIONING,
            _('Decommissioning'),
            color='yellow',
            description=_('Being removed from service'),
        ),
    ]


class DeviceAirflowChoices(ChoiceSet):
    key = 'Device.airflow'

    AIRFLOW_FRONT_TO_REAR = 'front-to-rear'
    AIRFLOW_REAR_TO_FRONT = 'rear-to-front'
    AIRFLOW_LEFT_TO_RIGHT = 'left-to-right'
    AIRFLOW_RIGHT_TO_LEFT = 'right-to-left'
    AIRFLOW_SIDE_TO_REAR = 'side-to-rear'
    AIRFLOW_REAR_TO_SIDE = 'rear-to-side'
    AIRFLOW_BOTTOM_TO_TOP = 'bottom-to-top'
    AIRFLOW_TOP_TO_BOTTOM = 'top-to-bottom'
    AIRFLOW_PASSIVE = 'passive'
    AIRFLOW_MIXED = 'mixed'

    CHOICES = [
        Choice(AIRFLOW_FRONT_TO_REAR, _('Front to rear')),
        Choice(AIRFLOW_REAR_TO_FRONT, _('Rear to front')),
        Choice(AIRFLOW_LEFT_TO_RIGHT, _('Left to right')),
        Choice(AIRFLOW_RIGHT_TO_LEFT, _('Right to left')),
        Choice(AIRFLOW_SIDE_TO_REAR, _('Side to rear')),
        Choice(AIRFLOW_REAR_TO_SIDE, _('Rear to side')),
        Choice(AIRFLOW_BOTTOM_TO_TOP, _('Bottom to top')),
        Choice(AIRFLOW_TOP_TO_BOTTOM, _('Top to bottom')),
        Choice(AIRFLOW_PASSIVE, _('Passive')),
        Choice(AIRFLOW_MIXED, _('Mixed')),
    ]


#
# Modules
#

class ModuleStatusChoices(ChoiceSet):
    key = 'Module.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        Choice(STATUS_OFFLINE, _('Offline'), color='gray', description=_('Installed but not currently in service')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Fully operational and in service')),
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_STAGED, _('Staged'), color='blue', description=_('Installed and being prepared for service')),
        Choice(STATUS_FAILED, _('Failed'), color='red', description=_('Malfunctioning or out of service')),
        Choice(
            STATUS_DECOMMISSIONING,
            _('Decommissioning'),
            color='yellow',
            description=_('Being removed from service'),
        ),
    ]


class ModuleAirflowChoices(ChoiceSet):
    key = 'Module.airflow'

    FRONT_TO_REAR = 'front-to-rear'
    REAR_TO_FRONT = 'rear-to-front'
    LEFT_TO_RIGHT = 'left-to-right'
    RIGHT_TO_LEFT = 'right-to-left'
    SIDE_TO_REAR = 'side-to-rear'
    PASSIVE = 'passive'

    CHOICES = [
        Choice(FRONT_TO_REAR, _('Front to rear')),
        Choice(REAR_TO_FRONT, _('Rear to front')),
        Choice(LEFT_TO_RIGHT, _('Left to right')),
        Choice(RIGHT_TO_LEFT, _('Right to left')),
        Choice(SIDE_TO_REAR, _('Side to rear')),
        Choice(PASSIVE, _('Passive')),
    ]


#
# ConsolePorts
#

class ConsolePortTypeChoices(ChoiceSet):

    TYPE_DE9 = 'de-9'
    TYPE_DB25 = 'db-25'
    TYPE_RJ11 = 'rj-11'
    TYPE_RJ12 = 'rj-12'
    TYPE_RJ45 = 'rj-45'
    TYPE_MINI_DIN_8 = 'mini-din-8'
    TYPE_USB_A = 'usb-a'
    TYPE_USB_B = 'usb-b'
    TYPE_USB_C = 'usb-c'
    TYPE_USB_MINI_A = 'usb-mini-a'
    TYPE_USB_MINI_B = 'usb-mini-b'
    TYPE_USB_MICRO_A = 'usb-micro-a'
    TYPE_USB_MICRO_B = 'usb-micro-b'
    TYPE_USB_MICRO_AB = 'usb-micro-ab'
    TYPE_OTHER = 'other'

    CHOICES = (
        ('Serial', (
            Choice(TYPE_DE9, 'DE-9'),
            Choice(TYPE_DB25, 'DB-25'),
            Choice(TYPE_RJ11, 'RJ-11'),
            Choice(TYPE_RJ12, 'RJ-12'),
            Choice(TYPE_RJ45, 'RJ-45'),
            Choice(TYPE_MINI_DIN_8, 'Mini-DIN 8'),
        )),
        ('USB', (
            Choice(TYPE_USB_A, 'USB Type A'),
            Choice(TYPE_USB_B, 'USB Type B'),
            Choice(TYPE_USB_C, 'USB Type C'),
            Choice(TYPE_USB_MINI_A, 'USB Mini A'),
            Choice(TYPE_USB_MINI_B, 'USB Mini B'),
            Choice(TYPE_USB_MICRO_A, 'USB Micro A'),
            Choice(TYPE_USB_MICRO_B, 'USB Micro B'),
            Choice(TYPE_USB_MICRO_AB, 'USB Micro AB'),
        )),
        ('Other', (
            Choice(TYPE_OTHER, 'Other'),
        )),
    )


class ConsolePortSpeedChoices(ChoiceSet):

    SPEED_1200 = 1200
    SPEED_2400 = 2400
    SPEED_4800 = 4800
    SPEED_9600 = 9600
    SPEED_19200 = 19200
    SPEED_38400 = 38400
    SPEED_57600 = 57600
    SPEED_115200 = 115200

    CHOICES = (
        Choice(SPEED_1200, '1200 bps'),
        Choice(SPEED_2400, '2400 bps'),
        Choice(SPEED_4800, '4800 bps'),
        Choice(SPEED_9600, '9600 bps'),
        Choice(SPEED_19200, '19.2 kbps'),
        Choice(SPEED_38400, '38.4 kbps'),
        Choice(SPEED_57600, '57.6 kbps'),
        Choice(SPEED_115200, '115.2 kbps'),
    )


#
# PowerPorts
#

class PowerPortTypeChoices(ChoiceSet):

    # IEC 60320
    TYPE_IEC_C6 = 'iec-60320-c6'
    TYPE_IEC_C8 = 'iec-60320-c8'
    TYPE_IEC_C14 = 'iec-60320-c14'
    TYPE_IEC_C16 = 'iec-60320-c16'
    TYPE_IEC_C18 = 'iec-60320-c18'
    TYPE_IEC_C20 = 'iec-60320-c20'
    TYPE_IEC_C22 = 'iec-60320-c22'
    # IEC 60309
    TYPE_IEC_PNE4H = 'iec-60309-p-n-e-4h'
    TYPE_IEC_PNE6H = 'iec-60309-p-n-e-6h'
    TYPE_IEC_PNE9H = 'iec-60309-p-n-e-9h'
    TYPE_IEC_2PE4H = 'iec-60309-2p-e-4h'
    TYPE_IEC_2PE6H = 'iec-60309-2p-e-6h'
    TYPE_IEC_2PE9H = 'iec-60309-2p-e-9h'
    TYPE_IEC_3PE4H = 'iec-60309-3p-e-4h'
    TYPE_IEC_3PE6H = 'iec-60309-3p-e-6h'
    TYPE_IEC_3PE9H = 'iec-60309-3p-e-9h'
    TYPE_IEC_3PNE4H = 'iec-60309-3p-n-e-4h'
    TYPE_IEC_3PNE6H = 'iec-60309-3p-n-e-6h'
    TYPE_IEC_3PNE9H = 'iec-60309-3p-n-e-9h'
    # IEC 60906-1
    TYPE_IEC_60906_1 = 'iec-60906-1'
    TYPE_NBR_14136_10A = 'nbr-14136-10a'
    TYPE_NBR_14136_20A = 'nbr-14136-20a'
    # NEMA non-locking
    TYPE_NEMA_115P = 'nema-1-15p'
    TYPE_NEMA_515P = 'nema-5-15p'
    TYPE_NEMA_520P = 'nema-5-20p'
    TYPE_NEMA_530P = 'nema-5-30p'
    TYPE_NEMA_550P = 'nema-5-50p'
    TYPE_NEMA_615P = 'nema-6-15p'
    TYPE_NEMA_620P = 'nema-6-20p'
    TYPE_NEMA_630P = 'nema-6-30p'
    TYPE_NEMA_650P = 'nema-6-50p'
    TYPE_NEMA_1030P = 'nema-10-30p'
    TYPE_NEMA_1050P = 'nema-10-50p'
    TYPE_NEMA_1420P = 'nema-14-20p'
    TYPE_NEMA_1430P = 'nema-14-30p'
    TYPE_NEMA_1450P = 'nema-14-50p'
    TYPE_NEMA_1460P = 'nema-14-60p'
    TYPE_NEMA_1515P = 'nema-15-15p'
    TYPE_NEMA_1520P = 'nema-15-20p'
    TYPE_NEMA_1530P = 'nema-15-30p'
    TYPE_NEMA_1550P = 'nema-15-50p'
    TYPE_NEMA_1560P = 'nema-15-60p'
    # NEMA locking
    TYPE_NEMA_L115P = 'nema-l1-15p'
    TYPE_NEMA_L515P = 'nema-l5-15p'
    TYPE_NEMA_L520P = 'nema-l5-20p'
    TYPE_NEMA_L530P = 'nema-l5-30p'
    TYPE_NEMA_L550P = 'nema-l5-50p'
    TYPE_NEMA_L615P = 'nema-l6-15p'
    TYPE_NEMA_L620P = 'nema-l6-20p'
    TYPE_NEMA_L630P = 'nema-l6-30p'
    TYPE_NEMA_L650P = 'nema-l6-50p'
    TYPE_NEMA_L1030P = 'nema-l10-30p'
    TYPE_NEMA_L1420P = 'nema-l14-20p'
    TYPE_NEMA_L1430P = 'nema-l14-30p'
    TYPE_NEMA_L1450P = 'nema-l14-50p'
    TYPE_NEMA_L1460P = 'nema-l14-60p'
    TYPE_NEMA_L1520P = 'nema-l15-20p'
    TYPE_NEMA_L1530P = 'nema-l15-30p'
    TYPE_NEMA_L1550P = 'nema-l15-50p'
    TYPE_NEMA_L1560P = 'nema-l15-60p'
    TYPE_NEMA_L2120P = 'nema-l21-20p'
    TYPE_NEMA_L2130P = 'nema-l21-30p'
    TYPE_NEMA_L2220P = 'nema-l22-20p'
    TYPE_NEMA_L2230P = 'nema-l22-30p'
    # California style
    TYPE_CS6361C = 'cs6361c'
    TYPE_CS6365C = 'cs6365c'
    TYPE_CS8165C = 'cs8165c'
    TYPE_CS8265C = 'cs8265c'
    TYPE_CS8365C = 'cs8365c'
    TYPE_CS8465C = 'cs8465c'
    # ITA/international
    TYPE_ITA_C = 'ita-c'
    TYPE_ITA_E = 'ita-e'
    TYPE_ITA_F = 'ita-f'
    TYPE_ITA_EF = 'ita-ef'
    TYPE_ITA_G = 'ita-g'
    TYPE_ITA_H = 'ita-h'
    TYPE_ITA_I = 'ita-i'
    TYPE_ITA_J = 'ita-j'
    TYPE_ITA_K = 'ita-k'
    TYPE_ITA_L = 'ita-l'
    TYPE_ITA_M = 'ita-m'
    TYPE_ITA_N = 'ita-n'
    TYPE_ITA_O = 'ita-o'
    # USB
    TYPE_USB_A = 'usb-a'
    TYPE_USB_B = 'usb-b'
    TYPE_USB_C = 'usb-c'
    TYPE_USB_MINI_A = 'usb-mini-a'
    TYPE_USB_MINI_B = 'usb-mini-b'
    TYPE_USB_MICRO_A = 'usb-micro-a'
    TYPE_USB_MICRO_B = 'usb-micro-b'
    TYPE_USB_MICRO_AB = 'usb-micro-ab'
    TYPE_USB_3_B = 'usb-3-b'
    TYPE_USB_3_MICROB = 'usb-3-micro-b'
    # Molex
    TYPE_MOLEX_MICRO_FIT_1X2 = 'molex-micro-fit-1x2'
    TYPE_MOLEX_MICRO_FIT_2X2 = 'molex-micro-fit-2x2'
    TYPE_MOLEX_MICRO_FIT_2X3 = 'molex-micro-fit-2x3'
    TYPE_MOLEX_MICRO_FIT_2X4 = 'molex-micro-fit-2x4'
    # Direct current (DC)
    TYPE_DC = 'dc-terminal'
    # Proprietary
    TYPE_SAF_D_GRID = 'saf-d-grid'
    TYPE_NEUTRIK_POWERCON_20A = 'neutrik-powercon-20'
    TYPE_NEUTRIK_POWERCON_32A = 'neutrik-powercon-32'
    TYPE_NEUTRIK_POWERCON_TRUE1 = 'neutrik-powercon-true1'
    TYPE_NEUTRIK_POWERCON_TRUE1_TOP = 'neutrik-powercon-true1-top'
    TYPE_UBIQUITI_SMARTPOWER = 'ubiquiti-smartpower'
    # Other
    TYPE_HARDWIRED = 'hardwired'
    TYPE_OTHER = 'other'

    CHOICES = (
        ('IEC 60320', (
            Choice(TYPE_IEC_C6, 'C6'),
            Choice(TYPE_IEC_C8, 'C8'),
            Choice(TYPE_IEC_C14, 'C14'),
            Choice(TYPE_IEC_C16, 'C16'),
            Choice(TYPE_IEC_C18, 'C18'),
            Choice(TYPE_IEC_C20, 'C20'),
            Choice(TYPE_IEC_C22, 'C22'),
        )),
        ('IEC 60309', (
            Choice(TYPE_IEC_PNE4H, 'P+N+E 4H'),
            Choice(TYPE_IEC_PNE6H, 'P+N+E 6H'),
            Choice(TYPE_IEC_PNE9H, 'P+N+E 9H'),
            Choice(TYPE_IEC_2PE4H, '2P+E 4H'),
            Choice(TYPE_IEC_2PE6H, '2P+E 6H'),
            Choice(TYPE_IEC_2PE9H, '2P+E 9H'),
            Choice(TYPE_IEC_3PE4H, '3P+E 4H'),
            Choice(TYPE_IEC_3PE6H, '3P+E 6H'),
            Choice(TYPE_IEC_3PE9H, '3P+E 9H'),
            Choice(TYPE_IEC_3PNE4H, '3P+N+E 4H'),
            Choice(TYPE_IEC_3PNE6H, '3P+N+E 6H'),
            Choice(TYPE_IEC_3PNE9H, '3P+N+E 9H'),
        )),
        ('IEC 60906-1', (
            Choice(TYPE_IEC_60906_1, 'IEC 60906-1'),
            Choice(TYPE_NBR_14136_10A, '2P+T 10A (NBR 14136)'),
            Choice(TYPE_NBR_14136_20A, '2P+T 20A (NBR 14136)'),
        )),
        (_('NEMA (Non-locking)'), (
            Choice(TYPE_NEMA_115P, 'NEMA 1-15P'),
            Choice(TYPE_NEMA_515P, 'NEMA 5-15P'),
            Choice(TYPE_NEMA_520P, 'NEMA 5-20P'),
            Choice(TYPE_NEMA_530P, 'NEMA 5-30P'),
            Choice(TYPE_NEMA_550P, 'NEMA 5-50P'),
            Choice(TYPE_NEMA_615P, 'NEMA 6-15P'),
            Choice(TYPE_NEMA_620P, 'NEMA 6-20P'),
            Choice(TYPE_NEMA_630P, 'NEMA 6-30P'),
            Choice(TYPE_NEMA_650P, 'NEMA 6-50P'),
            Choice(TYPE_NEMA_1030P, 'NEMA 10-30P'),
            Choice(TYPE_NEMA_1050P, 'NEMA 10-50P'),
            Choice(TYPE_NEMA_1420P, 'NEMA 14-20P'),
            Choice(TYPE_NEMA_1430P, 'NEMA 14-30P'),
            Choice(TYPE_NEMA_1450P, 'NEMA 14-50P'),
            Choice(TYPE_NEMA_1460P, 'NEMA 14-60P'),
            Choice(TYPE_NEMA_1515P, 'NEMA 15-15P'),
            Choice(TYPE_NEMA_1520P, 'NEMA 15-20P'),
            Choice(TYPE_NEMA_1530P, 'NEMA 15-30P'),
            Choice(TYPE_NEMA_1550P, 'NEMA 15-50P'),
            Choice(TYPE_NEMA_1560P, 'NEMA 15-60P'),
        )),
        (_('NEMA (Locking)'), (
            Choice(TYPE_NEMA_L115P, 'NEMA L1-15P'),
            Choice(TYPE_NEMA_L515P, 'NEMA L5-15P'),
            Choice(TYPE_NEMA_L520P, 'NEMA L5-20P'),
            Choice(TYPE_NEMA_L530P, 'NEMA L5-30P'),
            Choice(TYPE_NEMA_L550P, 'NEMA L5-50P'),
            Choice(TYPE_NEMA_L615P, 'NEMA L6-15P'),
            Choice(TYPE_NEMA_L620P, 'NEMA L6-20P'),
            Choice(TYPE_NEMA_L630P, 'NEMA L6-30P'),
            Choice(TYPE_NEMA_L650P, 'NEMA L6-50P'),
            Choice(TYPE_NEMA_L1030P, 'NEMA L10-30P'),
            Choice(TYPE_NEMA_L1420P, 'NEMA L14-20P'),
            Choice(TYPE_NEMA_L1430P, 'NEMA L14-30P'),
            Choice(TYPE_NEMA_L1450P, 'NEMA L14-50P'),
            Choice(TYPE_NEMA_L1460P, 'NEMA L14-60P'),
            Choice(TYPE_NEMA_L1520P, 'NEMA L15-20P'),
            Choice(TYPE_NEMA_L1530P, 'NEMA L15-30P'),
            Choice(TYPE_NEMA_L1550P, 'NEMA L15-50P'),
            Choice(TYPE_NEMA_L1560P, 'NEMA L15-60P'),
            Choice(TYPE_NEMA_L2120P, 'NEMA L21-20P'),
            Choice(TYPE_NEMA_L2130P, 'NEMA L21-30P'),
            Choice(TYPE_NEMA_L2220P, 'NEMA L22-20P'),
            Choice(TYPE_NEMA_L2230P, 'NEMA L22-30P'),
        )),
        (_('California Style'), (
            Choice(TYPE_CS6361C, 'CS6361C'),
            Choice(TYPE_CS6365C, 'CS6365C'),
            Choice(TYPE_CS8165C, 'CS8165C'),
            Choice(TYPE_CS8265C, 'CS8265C'),
            Choice(TYPE_CS8365C, 'CS8365C'),
            Choice(TYPE_CS8465C, 'CS8465C'),
        )),
        (_('International/ITA'), (
            Choice(TYPE_ITA_C, 'ITA Type C (CEE 7/16)'),
            Choice(TYPE_ITA_E, 'ITA Type E (CEE 7/6)'),
            Choice(TYPE_ITA_F, 'ITA Type F (CEE 7/4)'),
            Choice(TYPE_ITA_EF, 'ITA Type E/F (CEE 7/7)'),
            Choice(TYPE_ITA_G, 'ITA Type G (BS 1363)'),
            Choice(TYPE_ITA_H, 'ITA Type H'),
            Choice(TYPE_ITA_I, 'ITA Type I'),
            Choice(TYPE_ITA_J, 'ITA Type J'),
            Choice(TYPE_ITA_K, 'ITA Type K'),
            Choice(TYPE_ITA_L, 'ITA Type L (CEI 23-50)'),
            Choice(TYPE_ITA_M, 'ITA Type M (BS 546)'),
            Choice(TYPE_ITA_N, 'ITA Type N'),
            Choice(TYPE_ITA_O, 'ITA Type O'),
        )),
        ('USB', (
            Choice(TYPE_USB_A, 'USB Type A'),
            Choice(TYPE_USB_B, 'USB Type B'),
            Choice(TYPE_USB_C, 'USB Type C'),
            Choice(TYPE_USB_MINI_A, 'USB Mini A'),
            Choice(TYPE_USB_MINI_B, 'USB Mini B'),
            Choice(TYPE_USB_MICRO_A, 'USB Micro A'),
            Choice(TYPE_USB_MICRO_B, 'USB Micro B'),
            Choice(TYPE_USB_MICRO_AB, 'USB Micro AB'),
            Choice(TYPE_USB_3_B, 'USB 3.0 Type B'),
            Choice(TYPE_USB_3_MICROB, 'USB 3.0 Micro B'),
        )),
        ('Molex', (
            Choice(TYPE_MOLEX_MICRO_FIT_1X2, 'Molex Micro-Fit 1x2'),
            Choice(TYPE_MOLEX_MICRO_FIT_2X2, 'Molex Micro-Fit 2x2'),
            Choice(TYPE_MOLEX_MICRO_FIT_2X3, 'Molex Micro-Fit 2x3'),
            Choice(TYPE_MOLEX_MICRO_FIT_2X4, 'Molex Micro-Fit 2x4'),
        )),
        ('DC', (
            Choice(TYPE_DC, 'DC Terminal'),
        )),
        (_('Proprietary'), (
            Choice(TYPE_SAF_D_GRID, 'Saf-D-Grid'),
            Choice(TYPE_NEUTRIK_POWERCON_20A, 'Neutrik powerCON (20A)'),
            Choice(TYPE_NEUTRIK_POWERCON_32A, 'Neutrik powerCON (32A)'),
            Choice(TYPE_NEUTRIK_POWERCON_TRUE1, 'Neutrik powerCON TRUE1'),
            Choice(TYPE_NEUTRIK_POWERCON_TRUE1_TOP, 'Neutrik powerCON TRUE1 TOP'),
            Choice(TYPE_UBIQUITI_SMARTPOWER, 'Ubiquiti SmartPower'),
        )),
        (_('Other'), (
            Choice(TYPE_HARDWIRED, 'Hardwired'),
            Choice(TYPE_OTHER, 'Other'),
        )),
    )


#
# PowerOutlets
#

class PowerOutletTypeChoices(ChoiceSet):

    # IEC 60320
    TYPE_IEC_C5 = 'iec-60320-c5'
    TYPE_IEC_C7 = 'iec-60320-c7'
    TYPE_IEC_C13 = 'iec-60320-c13'
    TYPE_IEC_C15 = 'iec-60320-c15'
    TYPE_IEC_C17 = 'iec-60320-c17'
    TYPE_IEC_C19 = 'iec-60320-c19'
    TYPE_IEC_C21 = 'iec-60320-c21'
    # IEC 60309
    TYPE_IEC_PNE4H = 'iec-60309-p-n-e-4h'
    TYPE_IEC_PNE6H = 'iec-60309-p-n-e-6h'
    TYPE_IEC_PNE9H = 'iec-60309-p-n-e-9h'
    TYPE_IEC_2PE4H = 'iec-60309-2p-e-4h'
    TYPE_IEC_2PE6H = 'iec-60309-2p-e-6h'
    TYPE_IEC_2PE9H = 'iec-60309-2p-e-9h'
    TYPE_IEC_3PE4H = 'iec-60309-3p-e-4h'
    TYPE_IEC_3PE6H = 'iec-60309-3p-e-6h'
    TYPE_IEC_3PE9H = 'iec-60309-3p-e-9h'
    TYPE_IEC_3PNE4H = 'iec-60309-3p-n-e-4h'
    TYPE_IEC_3PNE6H = 'iec-60309-3p-n-e-6h'
    TYPE_IEC_3PNE9H = 'iec-60309-3p-n-e-9h'
    # IEC 60906-1
    TYPE_IEC_60906_1 = 'iec-60906-1'
    TYPE_NBR_14136_10A = 'nbr-14136-10a'
    TYPE_NBR_14136_20A = 'nbr-14136-20a'
    # NEMA non-locking
    TYPE_NEMA_115R = 'nema-1-15r'
    TYPE_NEMA_515R = 'nema-5-15r'
    TYPE_NEMA_520R = 'nema-5-20r'
    TYPE_NEMA_530R = 'nema-5-30r'
    TYPE_NEMA_550R = 'nema-5-50r'
    TYPE_NEMA_615R = 'nema-6-15r'
    TYPE_NEMA_620R = 'nema-6-20r'
    TYPE_NEMA_630R = 'nema-6-30r'
    TYPE_NEMA_650R = 'nema-6-50r'
    TYPE_NEMA_1030R = 'nema-10-30r'
    TYPE_NEMA_1050R = 'nema-10-50r'
    TYPE_NEMA_1420R = 'nema-14-20r'
    TYPE_NEMA_1430R = 'nema-14-30r'
    TYPE_NEMA_1450R = 'nema-14-50r'
    TYPE_NEMA_1460R = 'nema-14-60r'
    TYPE_NEMA_1515R = 'nema-15-15r'
    TYPE_NEMA_1520R = 'nema-15-20r'
    TYPE_NEMA_1530R = 'nema-15-30r'
    TYPE_NEMA_1550R = 'nema-15-50r'
    TYPE_NEMA_1560R = 'nema-15-60r'
    # NEMA locking
    TYPE_NEMA_L115R = 'nema-l1-15r'
    TYPE_NEMA_L515R = 'nema-l5-15r'
    TYPE_NEMA_L520R = 'nema-l5-20r'
    TYPE_NEMA_L530R = 'nema-l5-30r'
    TYPE_NEMA_L550R = 'nema-l5-50r'
    TYPE_NEMA_L615R = 'nema-l6-15r'
    TYPE_NEMA_L620R = 'nema-l6-20r'
    TYPE_NEMA_L630R = 'nema-l6-30r'
    TYPE_NEMA_L650R = 'nema-l6-50r'
    TYPE_NEMA_L1030R = 'nema-l10-30r'
    TYPE_NEMA_L1420R = 'nema-l14-20r'
    TYPE_NEMA_L1430R = 'nema-l14-30r'
    TYPE_NEMA_L1450R = 'nema-l14-50r'
    TYPE_NEMA_L1460R = 'nema-l14-60r'
    TYPE_NEMA_L1520R = 'nema-l15-20r'
    TYPE_NEMA_L1530R = 'nema-l15-30r'
    TYPE_NEMA_L1550R = 'nema-l15-50r'
    TYPE_NEMA_L1560R = 'nema-l15-60r'
    TYPE_NEMA_L2120R = 'nema-l21-20r'
    TYPE_NEMA_L2130R = 'nema-l21-30r'
    TYPE_NEMA_L2220R = 'nema-l22-20r'
    TYPE_NEMA_L2230R = 'nema-l22-30r'
    # California style
    TYPE_CS6360C = 'CS6360C'
    TYPE_CS6364C = 'CS6364C'
    TYPE_CS8164C = 'CS8164C'
    TYPE_CS8264C = 'CS8264C'
    TYPE_CS8364C = 'CS8364C'
    TYPE_CS8464C = 'CS8464C'
    # ITA/international
    TYPE_ITA_E = 'ita-e'
    TYPE_ITA_F = 'ita-f'
    TYPE_ITA_G = 'ita-g'
    TYPE_ITA_H = 'ita-h'
    TYPE_ITA_I = 'ita-i'
    TYPE_ITA_J = 'ita-j'
    TYPE_ITA_K = 'ita-k'
    TYPE_ITA_L = 'ita-l'
    TYPE_ITA_M = 'ita-m'
    TYPE_ITA_N = 'ita-n'
    TYPE_ITA_O = 'ita-o'
    TYPE_ITA_MULTISTANDARD = 'ita-multistandard'
    # USB
    TYPE_USB_A = 'usb-a'
    TYPE_USB_MICROB = 'usb-micro-b'
    TYPE_USB_C = 'usb-c'
    # Molex
    TYPE_MOLEX_MICRO_FIT_1X2 = 'molex-micro-fit-1x2'
    TYPE_MOLEX_MICRO_FIT_2X2 = 'molex-micro-fit-2x2'
    TYPE_MOLEX_MICRO_FIT_2X3 = 'molex-micro-fit-2x3'
    TYPE_MOLEX_MICRO_FIT_2X4 = 'molex-micro-fit-2x4'
    # Direct current (DC)
    TYPE_DC = 'dc-terminal'
    # Proprietary
    TYPE_EATON_C39 = 'eaton-c39'
    TYPE_HDOT_CX = 'hdot-cx'
    TYPE_SAF_D_GRID = 'saf-d-grid'
    TYPE_NEUTRIK_POWERCON_20A = 'neutrik-powercon-20a'
    TYPE_NEUTRIK_POWERCON_32A = 'neutrik-powercon-32a'
    TYPE_NEUTRIK_POWERCON_TRUE1 = 'neutrik-powercon-true1'
    TYPE_NEUTRIK_POWERCON_TRUE1_TOP = 'neutrik-powercon-true1-top'
    TYPE_UBIQUITI_SMARTPOWER = 'ubiquiti-smartpower'
    # Other
    TYPE_HARDWIRED = 'hardwired'
    TYPE_OTHER = 'other'

    CHOICES = (
        ('IEC 60320', (
            Choice(TYPE_IEC_C5, 'C5'),
            Choice(TYPE_IEC_C7, 'C7'),
            Choice(TYPE_IEC_C13, 'C13'),
            Choice(TYPE_IEC_C15, 'C15'),
            Choice(TYPE_IEC_C17, 'C17'),
            Choice(TYPE_IEC_C19, 'C19'),
            Choice(TYPE_IEC_C21, 'C21'),
        )),
        ('IEC 60309', (
            Choice(TYPE_IEC_PNE4H, 'P+N+E 4H'),
            Choice(TYPE_IEC_PNE6H, 'P+N+E 6H'),
            Choice(TYPE_IEC_PNE9H, 'P+N+E 9H'),
            Choice(TYPE_IEC_2PE4H, '2P+E 4H'),
            Choice(TYPE_IEC_2PE6H, '2P+E 6H'),
            Choice(TYPE_IEC_2PE9H, '2P+E 9H'),
            Choice(TYPE_IEC_3PE4H, '3P+E 4H'),
            Choice(TYPE_IEC_3PE6H, '3P+E 6H'),
            Choice(TYPE_IEC_3PE9H, '3P+E 9H'),
            Choice(TYPE_IEC_3PNE4H, '3P+N+E 4H'),
            Choice(TYPE_IEC_3PNE6H, '3P+N+E 6H'),
            Choice(TYPE_IEC_3PNE9H, '3P+N+E 9H'),
        )),
        ('IEC 60906-1', (
            Choice(TYPE_IEC_60906_1, 'IEC 60906-1'),
            Choice(TYPE_NBR_14136_10A, '2P+T 10A (NBR 14136)'),
            Choice(TYPE_NBR_14136_20A, '2P+T 20A (NBR 14136)'),
        )),
        (_('NEMA (Non-locking)'), (
            Choice(TYPE_NEMA_115R, 'NEMA 1-15R'),
            Choice(TYPE_NEMA_515R, 'NEMA 5-15R'),
            Choice(TYPE_NEMA_520R, 'NEMA 5-20R'),
            Choice(TYPE_NEMA_530R, 'NEMA 5-30R'),
            Choice(TYPE_NEMA_550R, 'NEMA 5-50R'),
            Choice(TYPE_NEMA_615R, 'NEMA 6-15R'),
            Choice(TYPE_NEMA_620R, 'NEMA 6-20R'),
            Choice(TYPE_NEMA_630R, 'NEMA 6-30R'),
            Choice(TYPE_NEMA_650R, 'NEMA 6-50R'),
            Choice(TYPE_NEMA_1030R, 'NEMA 10-30R'),
            Choice(TYPE_NEMA_1050R, 'NEMA 10-50R'),
            Choice(TYPE_NEMA_1420R, 'NEMA 14-20R'),
            Choice(TYPE_NEMA_1430R, 'NEMA 14-30R'),
            Choice(TYPE_NEMA_1450R, 'NEMA 14-50R'),
            Choice(TYPE_NEMA_1460R, 'NEMA 14-60R'),
            Choice(TYPE_NEMA_1515R, 'NEMA 15-15R'),
            Choice(TYPE_NEMA_1520R, 'NEMA 15-20R'),
            Choice(TYPE_NEMA_1530R, 'NEMA 15-30R'),
            Choice(TYPE_NEMA_1550R, 'NEMA 15-50R'),
            Choice(TYPE_NEMA_1560R, 'NEMA 15-60R'),
        )),
        (_('NEMA (Locking)'), (
            Choice(TYPE_NEMA_L115R, 'NEMA L1-15R'),
            Choice(TYPE_NEMA_L515R, 'NEMA L5-15R'),
            Choice(TYPE_NEMA_L520R, 'NEMA L5-20R'),
            Choice(TYPE_NEMA_L530R, 'NEMA L5-30R'),
            Choice(TYPE_NEMA_L550R, 'NEMA L5-50R'),
            Choice(TYPE_NEMA_L615R, 'NEMA L6-15R'),
            Choice(TYPE_NEMA_L620R, 'NEMA L6-20R'),
            Choice(TYPE_NEMA_L630R, 'NEMA L6-30R'),
            Choice(TYPE_NEMA_L650R, 'NEMA L6-50R'),
            Choice(TYPE_NEMA_L1030R, 'NEMA L10-30R'),
            Choice(TYPE_NEMA_L1420R, 'NEMA L14-20R'),
            Choice(TYPE_NEMA_L1430R, 'NEMA L14-30R'),
            Choice(TYPE_NEMA_L1450R, 'NEMA L14-50R'),
            Choice(TYPE_NEMA_L1460R, 'NEMA L14-60R'),
            Choice(TYPE_NEMA_L1520R, 'NEMA L15-20R'),
            Choice(TYPE_NEMA_L1530R, 'NEMA L15-30R'),
            Choice(TYPE_NEMA_L1550R, 'NEMA L15-50R'),
            Choice(TYPE_NEMA_L1560R, 'NEMA L15-60R'),
            Choice(TYPE_NEMA_L2120R, 'NEMA L21-20R'),
            Choice(TYPE_NEMA_L2130R, 'NEMA L21-30R'),
            Choice(TYPE_NEMA_L2220R, 'NEMA L22-20R'),
            Choice(TYPE_NEMA_L2230R, 'NEMA L22-30R'),
        )),
        (_('California Style'), (
            Choice(TYPE_CS6360C, 'CS6360C'),
            Choice(TYPE_CS6364C, 'CS6364C'),
            Choice(TYPE_CS8164C, 'CS8164C'),
            Choice(TYPE_CS8264C, 'CS8264C'),
            Choice(TYPE_CS8364C, 'CS8364C'),
            Choice(TYPE_CS8464C, 'CS8464C'),
        )),
        (_('ITA/International'), (
            Choice(TYPE_ITA_E, 'ITA Type E (CEE 7/5)'),
            Choice(TYPE_ITA_F, 'ITA Type F (CEE 7/3)'),
            Choice(TYPE_ITA_G, 'ITA Type G (BS 1363)'),
            Choice(TYPE_ITA_H, 'ITA Type H'),
            Choice(TYPE_ITA_I, 'ITA Type I'),
            Choice(TYPE_ITA_J, 'ITA Type J'),
            Choice(TYPE_ITA_K, 'ITA Type K'),
            Choice(TYPE_ITA_L, 'ITA Type L (CEI 23-50)'),
            Choice(TYPE_ITA_M, 'ITA Type M (BS 546)'),
            Choice(TYPE_ITA_N, 'ITA Type N'),
            Choice(TYPE_ITA_O, 'ITA Type O'),
            Choice(TYPE_ITA_MULTISTANDARD, 'ITA Multistandard'),
        )),
        ('USB', (
            Choice(TYPE_USB_A, 'USB Type A'),
            Choice(TYPE_USB_MICROB, 'USB Micro B'),
            Choice(TYPE_USB_C, 'USB Type C'),
        )),
        ('Molex', (
            Choice(TYPE_MOLEX_MICRO_FIT_1X2, 'Molex Micro-Fit 1x2'),
            Choice(TYPE_MOLEX_MICRO_FIT_2X2, 'Molex Micro-Fit 2x2'),
            Choice(TYPE_MOLEX_MICRO_FIT_2X3, 'Molex Micro-Fit 2x3'),
            Choice(TYPE_MOLEX_MICRO_FIT_2X4, 'Molex Micro-Fit 2x4'),
        )),
        ('DC', (
            Choice(TYPE_DC, 'DC Terminal'),
        )),
        (_('Proprietary'), (
            Choice(TYPE_EATON_C39, 'Eaton C39'),
            Choice(TYPE_HDOT_CX, 'HDOT Cx'),
            Choice(TYPE_SAF_D_GRID, 'Saf-D-Grid'),
            Choice(TYPE_NEUTRIK_POWERCON_20A, 'Neutrik powerCON (20A)'),
            Choice(TYPE_NEUTRIK_POWERCON_32A, 'Neutrik powerCON (32A)'),
            Choice(TYPE_NEUTRIK_POWERCON_TRUE1, 'Neutrik powerCON TRUE1'),
            Choice(TYPE_NEUTRIK_POWERCON_TRUE1_TOP, 'Neutrik powerCON TRUE1 TOP'),
            Choice(TYPE_UBIQUITI_SMARTPOWER, 'Ubiquiti SmartPower'),
        )),
        (_('Other'), (
            Choice(TYPE_HARDWIRED, 'Hardwired'),
            Choice(TYPE_OTHER, 'Other'),
        )),
    )


class PowerOutletFeedLegChoices(ChoiceSet):

    FEED_LEG_A = 'A'
    FEED_LEG_B = 'B'
    FEED_LEG_C = 'C'

    CHOICES = (
        Choice(FEED_LEG_A, 'A'),
        Choice(FEED_LEG_B, 'B'),
        Choice(FEED_LEG_C, 'C'),
    )


#
# Interfaces
#

class InterfaceKindChoices(ChoiceSet):
    KIND_PHYSICAL = 'physical'
    KIND_VIRTUAL = 'virtual'
    KIND_WIRELESS = 'wireless'

    CHOICES = (
        Choice(KIND_PHYSICAL, _('Physical')),
        Choice(KIND_VIRTUAL, _('Virtual')),
        Choice(KIND_WIRELESS, _('Wireless')),
    )


class InterfaceTypeChoices(ChoiceSet):

    # Virtual
    TYPE_VIRTUAL = 'virtual'
    TYPE_BRIDGE = 'bridge'
    TYPE_LAG = 'lag'
    TYPE_CHANNEL = 'channel'

    # FastEthernet
    TYPE_100ME_FX = '100base-fx'
    TYPE_100ME_LFX = '100base-lfx'
    TYPE_100ME_FIXED = '100base-tx'  # TODO: Rename to _TX
    TYPE_100ME_T1 = '100base-t1'

    # GigabitEthernet
    TYPE_1GE_BX10_D = '1000base-bx10-d'
    TYPE_1GE_BX10_U = '1000base-bx10-u'
    TYPE_1GE_CWDM = '1000base-cwdm'
    TYPE_1GE_CX = '1000base-cx'
    TYPE_1GE_DWDM = '1000base-dwdm'
    TYPE_1GE_EX = '1000base-ex'
    TYPE_1GE_SX_FIXED = '1000base-sx'  # TODO: Drop _FIXED suffix
    TYPE_1GE_LSX = '1000base-lsx'
    TYPE_1GE_LX_FIXED = '1000base-lx'  # TODO: Drop _FIXED suffix
    TYPE_1GE_LX10 = '1000base-lx10'
    TYPE_1GE_FIXED = '1000base-t'  # TODO: Rename to _T
    TYPE_1GE_TX_FIXED = '1000base-tx'  # TODO: Drop _FIXED suffix
    TYPE_1GE_ZX = '1000base-zx'

    # 2.5/5 Gbps Ethernet
    TYPE_2GE_FIXED = '2.5gbase-t'  # TODO: Rename to _T
    TYPE_5GE_FIXED = '5gbase-t'  # TODO: Rename to _T

    # 10 Gbps Ethernet
    TYPE_10GE_BR_D = '10gbase-br-d'
    TYPE_10GE_BR_U = '10gbase-br-u'
    TYPE_10GE_CU = '10gbase-cu'
    TYPE_10GE_CX4 = '10gbase-cx4'
    TYPE_10GE_ER = '10gbase-er'
    TYPE_10GE_LR = '10gbase-lr'
    TYPE_10GE_LRM = '10gbase-lrm'
    TYPE_10GE_LX4 = '10gbase-lx4'
    TYPE_10GE_SR = '10gbase-sr'
    TYPE_10GE_FIXED = '10gbase-t'
    TYPE_10GE_ZR = '10gbase-zr'

    # 25 Gbps Ethernet
    TYPE_25GE_CR = '25gbase-cr'
    TYPE_25GE_ER = '25gbase-er'
    TYPE_25GE_LR = '25gbase-lr'
    TYPE_25GE_SR = '25gbase-sr'
    TYPE_25GE_T = '25gbase-t'

    # 40 Gbps Ethernet
    TYPE_40GE_CR4 = '40gbase-cr4'
    TYPE_40GE_ER4 = '40gbase-er4'
    TYPE_40GE_FR4 = '40gbase-fr4'
    TYPE_40GE_LR4 = '40gbase-lr4'
    TYPE_40GE_SR4 = '40gbase-sr4'
    TYPE_40GE_SR4_BD = '40gbase-sr4-bd'

    # 50 Gbps Ethernet
    TYPE_50GE_CR = '50gbase-cr'
    TYPE_50GE_ER = '50gbase-er'
    TYPE_50GE_FR = '50gbase-fr'
    TYPE_50GE_LR = '50gbase-lr'
    TYPE_50GE_SR = '50gbase-sr'

    # 100 Gbps Ethernet
    TYPE_100GE_CR1 = '100gbase-cr1'
    TYPE_100GE_CR2 = '100gbase-cr2'
    TYPE_100GE_CR4 = '100gbase-cr4'
    TYPE_100GE_CR10 = '100gbase-cr10'
    TYPE_100GE_CWDM4 = '100gbase-cwdm4'
    TYPE_100GE_DR = '100gbase-dr'
    TYPE_100GE_FR1 = '100gbase-fr1'
    TYPE_100GE_ER4 = '100gbase-er4'
    TYPE_100GE_LR1 = '100gbase-lr1'
    TYPE_100GE_LR4 = '100gbase-lr4'
    TYPE_100GE_SR1 = '100gbase-sr1'
    TYPE_100GE_SR1_2 = '100gbase-sr1.2'
    TYPE_100GE_SR2 = '100gbase-sr2'
    TYPE_100GE_SR4 = '100gbase-sr4'
    TYPE_100GE_SR10 = '100gbase-sr10'
    TYPE_100GE_ZR = '100gbase-zr'

    # 200 Gbps Ethernet
    TYPE_200GE_CR2 = '200gbase-cr2'
    TYPE_200GE_CR4 = '200gbase-cr4'
    TYPE_200GE_SR2 = '200gbase-sr2'
    TYPE_200GE_SR4 = '200gbase-sr4'
    TYPE_200GE_DR4 = '200gbase-dr4'
    TYPE_200GE_FR4 = '200gbase-fr4'
    TYPE_200GE_LR4 = '200gbase-lr4'
    TYPE_200GE_ER4 = '200gbase-er4'
    TYPE_200GE_VR2 = '200gbase-vr2'

    # 400 Gbps Ethernet
    TYPE_400GE_CR4 = '400gbase-cr4'
    TYPE_400GE_DR4 = '400gbase-dr4'
    TYPE_400GE_ER8 = '400gbase-er8'
    TYPE_400GE_FR4 = '400gbase-fr4'
    TYPE_400GE_FR8 = '400gbase-fr8'
    TYPE_400GE_LR4 = '400gbase-lr4'
    TYPE_400GE_LR8 = '400gbase-lr8'
    TYPE_400GE_SR4 = '400gbase-sr4'
    TYPE_400GE_SR4_2 = '400gbase-sr4_2'
    TYPE_400GE_SR8 = '400gbase-sr8'
    TYPE_400GE_SR16 = '400gbase-sr16'
    TYPE_400GE_VR4 = '400gbase-vr4'
    TYPE_400GE_ZR = '400gbase-zr'

    # 800 Gbps Ethernet
    TYPE_800GE_CR8 = '800gbase-cr8'
    TYPE_800GE_DR8 = '800gbase-dr8'
    TYPE_800GE_SR8 = '800gbase-sr8'
    TYPE_800GE_VR8 = '800gbase-vr8'

    # 1.6 Tbps Ethernet
    TYPE_1TE_CR8 = '1.6tbase-cr8'
    TYPE_1TE_DR8 = '1.6tbase-dr8'
    TYPE_1TE_DR8_2 = '1.6tbase-dr8-2'

    # Ethernet (modular)
    TYPE_100ME_SFP = '100base-x-sfp'
    TYPE_1GE_GBIC = '1000base-x-gbic'
    TYPE_1GE_SFP = '1000base-x-sfp'
    TYPE_2GE_SFP = '2.5gbase-x-sfp'
    TYPE_10GE_SFP_PLUS = '10gbase-x-sfpp'
    TYPE_10GE_XFP = '10gbase-x-xfp'
    TYPE_10GE_XENPAK = '10gbase-x-xenpak'
    TYPE_10GE_X2 = '10gbase-x-x2'
    TYPE_25GE_SFP28 = '25gbase-x-sfp28'
    TYPE_50GE_SFP56 = '50gbase-x-sfp56'
    TYPE_40GE_QSFP_PLUS = '40gbase-x-qsfpp'
    TYPE_50GE_QSFP28 = '50gbase-x-sfp28'
    TYPE_100GE_CFP = '100gbase-x-cfp'
    TYPE_100GE_CFP2 = '100gbase-x-cfp2'
    TYPE_100GE_CFP4 = '100gbase-x-cfp4'
    TYPE_100GE_CXP = '100gbase-x-cxp'
    TYPE_100GE_CPAK = '100gbase-x-cpak'
    TYPE_100GE_DSFP = '100gbase-x-dsfp'
    TYPE_100GE_SFP_DD = '100gbase-x-sfpdd'
    TYPE_100GE_QSFP28 = '100gbase-x-qsfp28'
    TYPE_100GE_QSFP_DD = '100gbase-x-qsfpdd'
    TYPE_200GE_CFP2 = '200gbase-x-cfp2'
    TYPE_200GE_QSFP56 = '200gbase-x-qsfp56'
    TYPE_200GE_QSFP_DD = '200gbase-x-qsfpdd'
    TYPE_400GE_CFP2 = '400gbase-x-cfp2'
    TYPE_400GE_QSFP112 = '400gbase-x-qsfp112'
    TYPE_400GE_QSFP_DD = '400gbase-x-qsfpdd'
    TYPE_400GE_OSFP = '400gbase-x-osfp'
    TYPE_400GE_OSFP_RHS = '400gbase-x-osfp-rhs'
    TYPE_400GE_CDFP = '400gbase-x-cdfp'
    TYPE_400GE_CFP8 = '400gbase-x-cfp8'
    TYPE_800GE_QSFP_DD = '800gbase-x-qsfpdd'  # TODO: Rename to _QSFP_DD800
    TYPE_800GE_OSFP = '800gbase-x-osfp'  # TODO: Rename to _OSFP800
    TYPE_1TE_OSFP1600 = '1.6tbase-x-osfp1600'
    TYPE_1TE_OSFP1600_RHS = '1.6tbase-x-osfp1600-rhs'
    TYPE_1TE_QSFP_DD1600 = '1.6tbase-x-qsfpdd1600'

    # Backplane Ethernet
    TYPE_1GE_KX = '1000base-kx'
    TYPE_2GE_KX = '2.5gbase-kx'
    TYPE_5GE_KR = '5gbase-kr'
    TYPE_10GE_KR = '10gbase-kr'
    TYPE_10GE_KX4 = '10gbase-kx4'
    TYPE_25GE_KR = '25gbase-kr'
    TYPE_40GE_KR4 = '40gbase-kr4'
    TYPE_50GE_KR = '50gbase-kr'
    TYPE_100GE_KP4 = '100gbase-kp4'
    TYPE_100GE_KR2 = '100gbase-kr2'
    TYPE_100GE_KR4 = '100gbase-kr4'
    TYPE_1TE_KR8 = '1.6tbase-kr8'

    # Wireless
    TYPE_80211A = 'ieee802.11a'
    TYPE_80211G = 'ieee802.11g'
    TYPE_80211N = 'ieee802.11n'
    TYPE_80211AC = 'ieee802.11ac'
    TYPE_80211AD = 'ieee802.11ad'
    TYPE_80211AX = 'ieee802.11ax'
    TYPE_80211AY = 'ieee802.11ay'
    TYPE_80211BE = 'ieee802.11be'
    TYPE_802151 = 'ieee802.15.1'
    TYPE_802154 = 'ieee802.15.4'
    TYPE_OTHER_WIRELESS = 'other-wireless'

    # Cellular
    TYPE_GSM = 'gsm'
    TYPE_CDMA = 'cdma'
    TYPE_LTE = 'lte'
    TYPE_4G = '4g'
    TYPE_5G = '5g'

    # SONET
    TYPE_SONET_OC3 = 'sonet-oc3'
    TYPE_SONET_OC12 = 'sonet-oc12'
    TYPE_SONET_OC48 = 'sonet-oc48'
    TYPE_SONET_OC192 = 'sonet-oc192'
    TYPE_SONET_OC768 = 'sonet-oc768'
    TYPE_SONET_OC1920 = 'sonet-oc1920'
    TYPE_SONET_OC3840 = 'sonet-oc3840'

    # Fibrechannel
    TYPE_1GFC_SFP = '1gfc-sfp'
    TYPE_2GFC_SFP = '2gfc-sfp'
    TYPE_4GFC_SFP = '4gfc-sfp'
    TYPE_8GFC_SFP_PLUS = '8gfc-sfpp'
    TYPE_16GFC_SFP_PLUS = '16gfc-sfpp'
    TYPE_32GFC_SFP28 = '32gfc-sfp28'
    TYPE_32GFC_SFP_PLUS = '32gfc-sfpp'
    TYPE_64GFC_QSFP_PLUS = '64gfc-qsfpp'
    TYPE_64GFC_SFP_DD = '64gfc-sfpdd'
    TYPE_64GFC_SFP_PLUS = '64gfc-sfpp'
    TYPE_128GFC_QSFP28 = '128gfc-qsfp28'

    # InfiniBand
    TYPE_INFINIBAND_SDR = 'infiniband-sdr'
    TYPE_INFINIBAND_DDR = 'infiniband-ddr'
    TYPE_INFINIBAND_QDR = 'infiniband-qdr'
    TYPE_INFINIBAND_FDR10 = 'infiniband-fdr10'
    TYPE_INFINIBAND_FDR = 'infiniband-fdr'
    TYPE_INFINIBAND_EDR = 'infiniband-edr'
    TYPE_INFINIBAND_HDR = 'infiniband-hdr'
    TYPE_INFINIBAND_NDR = 'infiniband-ndr'
    TYPE_INFINIBAND_XDR = 'infiniband-xdr'

    # Serial
    TYPE_T1 = 't1'
    TYPE_E1 = 'e1'
    TYPE_T3 = 't3'
    TYPE_E3 = 'e3'

    # ATM/DSL
    TYPE_XDSL = 'xdsl'

    # Coaxial
    TYPE_DOCSIS = 'docsis'
    TYPE_MOCA = 'moca'

    # PON
    TYPE_BPON = 'bpon'
    TYPE_EPON = 'epon'
    TYPE_10G_EPON = '10g-epon'
    TYPE_GPON = 'gpon'
    TYPE_XG_PON = 'xg-pon'
    TYPE_XGS_PON = 'xgs-pon'
    TYPE_NG_PON2 = 'ng-pon2'
    TYPE_25G_PON = '25g-pon'
    TYPE_50G_PON = '50g-pon'

    # Stacking
    TYPE_STACKWISE = 'cisco-stackwise'
    TYPE_STACKWISE_PLUS = 'cisco-stackwise-plus'
    TYPE_FLEXSTACK = 'cisco-flexstack'
    TYPE_FLEXSTACK_PLUS = 'cisco-flexstack-plus'
    TYPE_STACKWISE80 = 'cisco-stackwise-80'
    TYPE_STACKWISE160 = 'cisco-stackwise-160'
    TYPE_STACKWISE320 = 'cisco-stackwise-320'
    TYPE_STACKWISE480 = 'cisco-stackwise-480'
    TYPE_STACKWISE1T = 'cisco-stackwise-1t'
    TYPE_JUNIPER_VCP = 'juniper-vcp'
    TYPE_SUMMITSTACK = 'extreme-summitstack'
    TYPE_SUMMITSTACK128 = 'extreme-summitstack-128'
    TYPE_SUMMITSTACK256 = 'extreme-summitstack-256'
    TYPE_SUMMITSTACK512 = 'extreme-summitstack-512'

    # Other
    TYPE_OTHER = 'other'

    CHOICES = (
        (
            _('Virtual interfaces'),
            (
                Choice(TYPE_VIRTUAL, _('Virtual')),
                Choice(TYPE_BRIDGE, _('Bridge')),
                Choice(TYPE_LAG, _('Link Aggregation Group (LAG)')),
                Choice(TYPE_CHANNEL, _('Channel')),
            ),
        ),
        (
            _('FastEthernet (100 Mbps)'),
            (
                Choice(TYPE_100ME_FX, '100BASE-FX (10/100ME)'),
                Choice(TYPE_100ME_LFX, '100BASE-LFX (10/100ME)'),
                Choice(TYPE_100ME_FIXED, '100BASE-TX (10/100ME)'),
                Choice(TYPE_100ME_T1, '100BASE-T1 (10/100ME)'),
            ),
        ),
        (
            _('GigabitEthernet (1 Gbps)'),
            (
                Choice(TYPE_1GE_BX10_D, '1000BASE-BX10-D (1GE BiDi Down)'),
                Choice(TYPE_1GE_BX10_U, '1000BASE-BX10-U (1GE BiDi Up)'),
                Choice(TYPE_1GE_CWDM, '1000BASE-CWDM (1GE)'),
                Choice(TYPE_1GE_CX, '1000BASE-CX (1GE DAC)'),
                Choice(TYPE_1GE_DWDM, '1000BASE-DWDM (1GE)'),
                Choice(TYPE_1GE_EX, '1000BASE-EX (1GE)'),
                Choice(TYPE_1GE_LSX, '1000BASE-LSX (1GE)'),
                Choice(TYPE_1GE_LX_FIXED, '1000BASE-LX (1GE)'),
                Choice(TYPE_1GE_LX10, '1000BASE-LX10/LH (1GE)'),
                Choice(TYPE_1GE_SX_FIXED, '1000BASE-SX (1GE)'),
                Choice(TYPE_1GE_FIXED, '1000BASE-T (1GE)'),
                Choice(TYPE_1GE_TX_FIXED, '1000BASE-TX (1GE)'),
                Choice(TYPE_1GE_ZX, '1000BASE-ZX (1GE)'),
            ),
        ),
        (
            _('2.5/5 Gbps Ethernet'),
            (
                Choice(TYPE_2GE_FIXED, '2.5GBASE-T (2.5GE)'),
                Choice(TYPE_5GE_FIXED, '5GBASE-T (5GE)'),
            ),
        ),
        (
            _('10 Gbps Ethernet'),
            (
                Choice(TYPE_10GE_BR_D, '10GBASE-BR-D (10GE BiDi Down)'),
                Choice(TYPE_10GE_BR_U, '10GBASE-BR-U (10GE BiDi Up)'),
                Choice(TYPE_10GE_CU, '10GBASE-CU (10GE DAC Passive Twinax)'),
                Choice(TYPE_10GE_CX4, '10GBASE-CX4 (10GE DAC)'),
                Choice(TYPE_10GE_ER, '10GBASE-ER (10GE)'),
                Choice(TYPE_10GE_LR, '10GBASE-LR (10GE)'),
                Choice(TYPE_10GE_LRM, '10GBASE-LRM (10GE)'),
                Choice(TYPE_10GE_LX4, '10GBASE-LX4 (10GE)'),
                Choice(TYPE_10GE_SR, '10GBASE-SR (10GE)'),
                Choice(TYPE_10GE_FIXED, '10GBASE-T (10GE)'),
                Choice(TYPE_10GE_ZR, '10GBASE-ZR (10GE)'),
            )
        ),
        (
            _('25 Gbps Ethernet'),
            (
                Choice(TYPE_25GE_CR, '25GBASE-CR (25GE DAC)'),
                Choice(TYPE_25GE_ER, '25GBASE-ER (25GE)'),
                Choice(TYPE_25GE_LR, '25GBASE-LR (25GE)'),
                Choice(TYPE_25GE_SR, '25GBASE-SR (25GE)'),
                Choice(TYPE_25GE_T, '25GBASE-T (25GE)'),
            )
        ),
        (
            _('40 Gbps Ethernet'),
            (
                Choice(TYPE_40GE_CR4, '40GBASE-CR4 (40GE DAC)'),
                Choice(TYPE_40GE_ER4, '40GBASE-ER4 (40GE)'),
                Choice(TYPE_40GE_FR4, '40GBASE-FR4 (40GE)'),
                Choice(TYPE_40GE_LR4, '40GBASE-LR4 (40GE)'),
                Choice(TYPE_40GE_SR4, '40GBASE-SR4 (40GE)'),
                Choice(TYPE_40GE_SR4_BD, '40GBASE-SR4 (40GE BiDi)'),
            )
        ),
        (
            _('50 Gbps Ethernet'),
            (
                Choice(TYPE_50GE_CR, '50GBASE-CR (50GE DAC)'),
                Choice(TYPE_50GE_ER, '50GBASE-ER (50GE)'),
                Choice(TYPE_50GE_FR, '50GBASE-FR (50GE)'),
                Choice(TYPE_50GE_LR, '50GBASE-LR (50GE)'),
                Choice(TYPE_50GE_SR, '50GBASE-SR (50GE)'),
            )
        ),
        (
            _('100 Gbps Ethernet'),
            (
                Choice(TYPE_100GE_CR1, '100GBASE-CR1 (100GE DAC)'),
                Choice(TYPE_100GE_CR2, '100GBASE-CR2 (100GE DAC)'),
                Choice(TYPE_100GE_CR4, '100GBASE-CR4 (100GE DAC)'),
                Choice(TYPE_100GE_CR10, '100GBASE-CR10 (100GE DAC)'),
                Choice(TYPE_100GE_CWDM4, '100GBASE-CWDM4 (100GE)'),
                Choice(TYPE_100GE_DR, '100GBASE-DR (100GE)'),
                Choice(TYPE_100GE_ER4, '100GBASE-ER4 (100GE)'),
                Choice(TYPE_100GE_FR1, '100GBASE-FR1 (100GE)'),
                Choice(TYPE_100GE_LR1, '100GBASE-LR1 (100GE)'),
                Choice(TYPE_100GE_LR4, '100GBASE-LR4 (100GE)'),
                Choice(TYPE_100GE_SR1, '100GBASE-SR1 (100GE)'),
                Choice(TYPE_100GE_SR1_2, '100GBASE-SR1.2 (100GE BiDi)'),
                Choice(TYPE_100GE_SR2, '100GBASE-SR2 (100GE)'),
                Choice(TYPE_100GE_SR4, '100GBASE-SR4 (100GE)'),
                Choice(TYPE_100GE_SR10, '100GBASE-SR10 (100GE)'),
                Choice(TYPE_100GE_ZR, '100GBASE-ZR (100GE)'),
            )
        ),
        (
            _('200 Gbps Ethernet'),
            (
                Choice(TYPE_200GE_CR2, '200GBASE-CR2 (200GE)'),
                Choice(TYPE_200GE_CR4, '200GBASE-CR4 (200GE)'),
                Choice(TYPE_200GE_DR4, '200GBASE-DR4 (200GE)'),
                Choice(TYPE_200GE_ER4, '200GBASE-ER4 (200GE)'),
                Choice(TYPE_200GE_FR4, '200GBASE-FR4 (200GE)'),
                Choice(TYPE_200GE_LR4, '200GBASE-LR4 (200GE)'),
                Choice(TYPE_200GE_SR2, '200GBASE-SR2 (200GE)'),
                Choice(TYPE_200GE_SR4, '200GBASE-SR4 (200GE)'),
                Choice(TYPE_200GE_VR2, '200GBASE-VR2 (200GE)'),
            )
        ),
        (
            _('400 Gbps Ethernet'),
            (
                Choice(TYPE_400GE_CR4, '400GBASE-CR4 (400GE)'),
                Choice(TYPE_400GE_DR4, '400GBASE-DR4 (400GE)'),
                Choice(TYPE_400GE_ER8, '400GBASE-ER8 (400GE)'),
                Choice(TYPE_400GE_FR4, '400GBASE-FR4 (400GE)'),
                Choice(TYPE_400GE_FR8, '400GBASE-FR8 (400GE)'),
                Choice(TYPE_400GE_LR4, '400GBASE-LR4 (400GE)'),
                Choice(TYPE_400GE_LR8, '400GBASE-LR8 (400GE)'),
                Choice(TYPE_400GE_SR4, '400GBASE-SR4 (400GE)'),
                Choice(TYPE_400GE_SR4_2, '400GBASE-SR4.2 (400GE BiDi)'),
                Choice(TYPE_400GE_SR8, '400GBASE-SR8 (400GE)'),
                Choice(TYPE_400GE_SR16, '400GBASE-SR16 (400GE)'),
                Choice(TYPE_400GE_VR4, '400GBASE-VR4 (400GE)'),
                Choice(TYPE_400GE_ZR, '400GBASE-ZR (400GE)'),
            )
        ),
        (
            _('800 Gbps Ethernet'),
            (
                Choice(TYPE_800GE_CR8, '800GBASE-CR8 (800GE)'),
                Choice(TYPE_800GE_DR8, '800GBASE-DR8 (800GE)'),
                Choice(TYPE_800GE_SR8, '800GBASE-SR8 (800GE)'),
                Choice(TYPE_800GE_VR8, '800GBASE-VR8 (800GE)'),
            )
        ),
        (
            _('1.6 Tbps Ethernet'),
            (
                Choice(TYPE_1TE_CR8, '1.6TBASE-CR8 (1.6TE)'),
                Choice(TYPE_1TE_DR8, '1.6TBASE-DR8 (1.6TE)'),
                Choice(TYPE_1TE_DR8_2, '1.6TBASE-DR8-2 (1.6TE)'),
            )
        ),
        (
            _('Pluggable transceivers'),
            (
                Choice(TYPE_100ME_SFP, 'SFP (100ME)'),
                Choice(TYPE_1GE_GBIC, 'GBIC (1GE)'),
                Choice(TYPE_1GE_SFP, 'SFP (1GE)'),
                Choice(TYPE_2GE_SFP, 'SFP (2.5GE)'),
                Choice(TYPE_10GE_SFP_PLUS, 'SFP+ (10GE)'),
                Choice(TYPE_10GE_XENPAK, 'XENPAK (10GE)'),
                Choice(TYPE_10GE_XFP, 'XFP (10GE)'),
                Choice(TYPE_10GE_X2, 'X2 (10GE)'),
                Choice(TYPE_25GE_SFP28, 'SFP28 (25GE)'),
                Choice(TYPE_40GE_QSFP_PLUS, 'QSFP+ (40GE)'),
                Choice(TYPE_50GE_QSFP28, 'QSFP28 (50GE)'),
                Choice(TYPE_50GE_SFP56, 'SFP56 (50GE)'),
                Choice(TYPE_100GE_CFP, 'CFP (100GE)'),
                Choice(TYPE_100GE_CFP2, 'CFP2 (100GE)'),
                Choice(TYPE_100GE_CFP4, 'CFP4 (100GE)'),
                Choice(TYPE_100GE_CXP, 'CXP (100GE)'),
                Choice(TYPE_100GE_CPAK, 'Cisco CPAK (100GE)'),
                Choice(TYPE_100GE_DSFP, 'DSFP (100GE)'),
                Choice(TYPE_100GE_QSFP28, 'QSFP28 (100GE)'),
                Choice(TYPE_100GE_QSFP_DD, 'QSFP-DD (100GE)'),
                Choice(TYPE_100GE_SFP_DD, 'SFP-DD (100GE)'),
                Choice(TYPE_200GE_CFP2, 'CFP2 (200GE)'),
                Choice(TYPE_200GE_QSFP56, 'QSFP56 (200GE)'),
                Choice(TYPE_200GE_QSFP_DD, 'QSFP-DD (200GE)'),
                Choice(TYPE_400GE_QSFP112, 'QSFP112 (400GE)'),
                Choice(TYPE_400GE_QSFP_DD, 'QSFP-DD (400GE)'),
                Choice(TYPE_400GE_CDFP, 'CDFP (400GE)'),
                Choice(TYPE_400GE_CFP2, 'CFP2 (400GE)'),
                Choice(TYPE_400GE_CFP8, 'CPF8 (400GE)'),
                Choice(TYPE_400GE_OSFP, 'OSFP (400GE)'),
                Choice(TYPE_400GE_OSFP_RHS, 'OSFP-RHS (400GE)'),
                Choice(TYPE_800GE_OSFP, 'OSFP (800GE)'),
                Choice(TYPE_800GE_QSFP_DD, 'QSFP-DD (800GE)'),
                Choice(TYPE_1TE_OSFP1600, 'OSFP1600 (1.6TE)'),
                Choice(TYPE_1TE_OSFP1600_RHS, 'OSFP1600-RHS (1.6TE)'),
                Choice(TYPE_1TE_QSFP_DD1600, 'QSFP-DD1600 (1.6TE)'),
            )
        ),
        (
            _('Backplane Ethernet'),
            (
                Choice(TYPE_1GE_KX, '1000BASE-KX (1GE)'),
                Choice(TYPE_2GE_KX, '2.5GBASE-KX (2.5GE)'),
                Choice(TYPE_5GE_KR, '5GBASE-KR (5GE)'),
                Choice(TYPE_10GE_KR, '10GBASE-KR (10GE)'),
                Choice(TYPE_10GE_KX4, '10GBASE-KX4 (10GE)'),
                Choice(TYPE_25GE_KR, '25GBASE-KR (25GE)'),
                Choice(TYPE_40GE_KR4, '40GBASE-KR4 (40GE)'),
                Choice(TYPE_50GE_KR, '50GBASE-KR (50GE)'),
                Choice(TYPE_100GE_KP4, '100GBASE-KP4 (100GE)'),
                Choice(TYPE_100GE_KR2, '100GBASE-KR2 (100GE)'),
                Choice(TYPE_100GE_KR4, '100GBASE-KR4 (100GE)'),
                Choice(TYPE_1TE_KR8, '1.6TBASE-KR8 (1.6TE)'),
            )
        ),
        (
            _('Wireless'),
            (
                Choice(TYPE_80211A, 'IEEE 802.11a'),
                Choice(TYPE_80211G, 'IEEE 802.11b/g'),
                Choice(TYPE_80211N, 'IEEE 802.11n (Wi-Fi 4)'),
                Choice(TYPE_80211AC, 'IEEE 802.11ac (Wi-Fi 5)'),
                Choice(TYPE_80211AD, 'IEEE 802.11ad (WiGig)'),
                Choice(TYPE_80211AX, 'IEEE 802.11ax (Wi-Fi 6)'),
                Choice(TYPE_80211AY, 'IEEE 802.11ay (WiGig)'),
                Choice(TYPE_80211BE, 'IEEE 802.11be (Wi-Fi 7)'),
                Choice(TYPE_802151, 'IEEE 802.15.1 (Bluetooth)'),
                Choice(TYPE_802154, 'IEEE 802.15.4 (LR-WPAN)'),
                Choice(TYPE_OTHER_WIRELESS, 'Other (Wireless)'),
            )
        ),
        (
            _('Cellular'),
            (
                Choice(TYPE_GSM, 'GSM'),
                Choice(TYPE_CDMA, 'CDMA'),
                Choice(TYPE_LTE, 'LTE'),
                Choice(TYPE_4G, '4G'),
                Choice(TYPE_5G, '5G'),
            )
        ),
        (
            'SONET',
            (
                Choice(TYPE_SONET_OC3, 'OC-3/STM-1'),
                Choice(TYPE_SONET_OC12, 'OC-12/STM-4'),
                Choice(TYPE_SONET_OC48, 'OC-48/STM-16'),
                Choice(TYPE_SONET_OC192, 'OC-192/STM-64'),
                Choice(TYPE_SONET_OC768, 'OC-768/STM-256'),
                Choice(TYPE_SONET_OC1920, 'OC-1920/STM-640'),
                Choice(TYPE_SONET_OC3840, 'OC-3840/STM-1234'),
            )
        ),
        (
            'FibreChannel',
            (
                Choice(TYPE_1GFC_SFP, 'SFP (1GFC)'),
                Choice(TYPE_2GFC_SFP, 'SFP (2GFC)'),
                Choice(TYPE_4GFC_SFP, 'SFP (4GFC)'),
                Choice(TYPE_8GFC_SFP_PLUS, 'SFP+ (8GFC)'),
                Choice(TYPE_16GFC_SFP_PLUS, 'SFP+ (16GFC)'),
                Choice(TYPE_32GFC_SFP28, 'SFP28 (32GFC)'),
                Choice(TYPE_32GFC_SFP_PLUS, 'SFP+ (32GFC)'),
                Choice(TYPE_64GFC_QSFP_PLUS, 'QSFP+ (64GFC)'),
                Choice(TYPE_64GFC_SFP_DD, 'SFP-DD (64GFC)'),
                Choice(TYPE_64GFC_SFP_PLUS, 'SFP+ (64GFC)'),
                Choice(TYPE_128GFC_QSFP28, 'QSFP28 (128GFC)'),
            )
        ),
        (
            'InfiniBand',
            (
                Choice(TYPE_INFINIBAND_SDR, 'SDR (2 Gbps)'),
                Choice(TYPE_INFINIBAND_DDR, 'DDR (4 Gbps)'),
                Choice(TYPE_INFINIBAND_QDR, 'QDR (8 Gbps)'),
                Choice(TYPE_INFINIBAND_FDR10, 'FDR10 (10 Gbps)'),
                Choice(TYPE_INFINIBAND_FDR, 'FDR (13.5 Gbps)'),
                Choice(TYPE_INFINIBAND_EDR, 'EDR (25 Gbps)'),
                Choice(TYPE_INFINIBAND_HDR, 'HDR (50 Gbps)'),
                Choice(TYPE_INFINIBAND_NDR, 'NDR (100 Gbps)'),
                Choice(TYPE_INFINIBAND_XDR, 'XDR (250 Gbps)'),
            )
        ),
        (
            _('Serial'),
            (
                Choice(TYPE_T1, 'T1 (1.544 Mbps)'),
                Choice(TYPE_E1, 'E1 (2.048 Mbps)'),
                Choice(TYPE_T3, 'T3 (45 Mbps)'),
                Choice(TYPE_E3, 'E3 (34 Mbps)'),
            )
        ),
        (
            'ATM',
            (
                Choice(TYPE_XDSL, 'xDSL'),
            )
        ),
        (
            _('Coaxial'),
            (
                Choice(TYPE_DOCSIS, 'DOCSIS'),
                Choice(TYPE_MOCA, 'MoCA'),
            )
        ),
        (
            'PON',
            (
                Choice(TYPE_BPON, 'BPON (622 Mbps / 155 Mbps)'),
                Choice(TYPE_EPON, 'EPON (1 Gbps)'),
                Choice(TYPE_10G_EPON, '10G-EPON (10 Gbps)'),
                Choice(TYPE_GPON, 'GPON (2.5 Gbps / 1.25 Gbps)'),
                Choice(TYPE_XG_PON, 'XG-PON (10 Gbps / 2.5 Gbps)'),
                Choice(TYPE_XGS_PON, 'XGS-PON (10 Gbps)'),
                Choice(TYPE_NG_PON2, 'NG-PON2 (TWDM-PON) (4x10 Gbps)'),
                Choice(TYPE_25G_PON, '25G-PON (25 Gbps)'),
                Choice(TYPE_50G_PON, '50G-PON (50 Gbps)'),
            )
        ),
        (
            _('Stacking'),
            (
                Choice(TYPE_STACKWISE, 'Cisco StackWise'),
                Choice(TYPE_STACKWISE_PLUS, 'Cisco StackWise Plus'),
                Choice(TYPE_FLEXSTACK, 'Cisco FlexStack'),
                Choice(TYPE_FLEXSTACK_PLUS, 'Cisco FlexStack Plus'),
                Choice(TYPE_STACKWISE80, 'Cisco StackWise-80'),
                Choice(TYPE_STACKWISE160, 'Cisco StackWise-160'),
                Choice(TYPE_STACKWISE320, 'Cisco StackWise-320'),
                Choice(TYPE_STACKWISE480, 'Cisco StackWise-480'),
                Choice(TYPE_STACKWISE1T, 'Cisco StackWise-1T'),
                Choice(TYPE_JUNIPER_VCP, 'Juniper VCP'),
                Choice(TYPE_SUMMITSTACK, 'Extreme SummitStack'),
                Choice(TYPE_SUMMITSTACK128, 'Extreme SummitStack-128'),
                Choice(TYPE_SUMMITSTACK256, 'Extreme SummitStack-256'),
                Choice(TYPE_SUMMITSTACK512, 'Extreme SummitStack-512'),
            )
        ),
        (
            _('Other'),
            (
                Choice(TYPE_OTHER, _('Other')),
            )
        ),
    )


class InterfaceSpeedChoices(ChoiceSet):
    key = 'Interface.speed'

    CHOICES = [
        Choice(10000, '10 Mbps'),
        Choice(100000, '100 Mbps'),
        Choice(1000000, '1 Gbps'),
        Choice(2500000, '2.5 Gbps'),
        Choice(5000000, '5 Gbps'),
        Choice(10000000, '10 Gbps'),
        Choice(25000000, '25 Gbps'),
        Choice(40000000, '40 Gbps'),
        Choice(50000000, '50 Gbps'),
        Choice(100000000, '100 Gbps'),
        Choice(200000000, '200 Gbps'),
        Choice(400000000, '400 Gbps'),
        Choice(800000000, '800 Gbps'),
        Choice(1600000000, '1.6 Tbps'),
    ]


class InterfaceDuplexChoices(ChoiceSet):

    DUPLEX_HALF = 'half'
    DUPLEX_FULL = 'full'
    DUPLEX_AUTO = 'auto'

    CHOICES = (
        Choice(DUPLEX_HALF, _('Half')),
        Choice(DUPLEX_FULL, _('Full')),
        Choice(DUPLEX_AUTO, _('Auto')),
    )


class InterfaceModeChoices(ChoiceSet):

    MODE_ACCESS = 'access'
    MODE_TAGGED = 'tagged'
    MODE_TAGGED_ALL = 'tagged-all'
    MODE_Q_IN_Q = 'q-in-q'

    CHOICES = (
        Choice(MODE_ACCESS, _('Access'), description=_('Untagged traffic for a single VLAN')),
        Choice(MODE_TAGGED, _('Tagged'), description=_('One untagged VLAN plus one or more tagged VLANs')),
        Choice(MODE_TAGGED_ALL, _('Tagged (All)'), description=_('Untagged VLAN plus all tagged VLANs')),
        Choice(MODE_Q_IN_Q, _('Q-in-Q (802.1ad)'), description=_('802.1ad service VLAN encapsulating customer VLANs')),
    )


class InterfacePoEModeChoices(ChoiceSet):

    MODE_PD = 'pd'
    MODE_PSE = 'pse'

    CHOICES = (
        Choice(MODE_PD, 'PD', description=_('Powered device that receives power over Ethernet')),
        Choice(MODE_PSE, 'PSE', description=_('Power sourcing equipment that supplies power over Ethernet')),
    )


class InterfacePoETypeChoices(ChoiceSet):

    TYPE_1_8023AF = 'type1-ieee802.3af'
    TYPE_2_8023AT = 'type2-ieee802.3at'
    TYPE_3_8023BT = 'type3-ieee802.3bt'
    TYPE_4_8023BT = 'type4-ieee802.3bt'

    PASSIVE_24V_2PAIR = 'passive-24v-2pair'
    PASSIVE_24V_4PAIR = 'passive-24v-4pair'
    PASSIVE_48V_2PAIR = 'passive-48v-2pair'
    PASSIVE_48V_4PAIR = 'passive-48v-4pair'

    CHOICES = (
        (
            _('IEEE Standard'),
            (
                Choice(TYPE_1_8023AF, '802.3af (Type 1)'),
                Choice(TYPE_2_8023AT, '802.3at (Type 2)'),
                Choice(TYPE_3_8023BT, '802.3bt (Type 3)'),
                Choice(TYPE_4_8023BT, '802.3bt (Type 4)'),
            )
        ),
        (
            _('Passive'),
            (
                Choice(PASSIVE_24V_2PAIR, _('Passive 24V (2-pair)')),
                Choice(PASSIVE_24V_4PAIR, _('Passive 24V (4-pair)')),
                Choice(PASSIVE_48V_2PAIR, _('Passive 48V (2-pair)')),
                Choice(PASSIVE_48V_4PAIR, _('Passive 48V (4-pair)')),
            )
        ),
    )


#
# FrontPorts/RearPorts
#

class PortTypeChoices(ChoiceSet):

    TYPE_8P8C = '8p8c'
    TYPE_8P6C = '8p6c'
    TYPE_8P4C = '8p4c'
    TYPE_8P2C = '8p2c'
    TYPE_6P6C = '6p6c'
    TYPE_6P4C = '6p4c'
    TYPE_6P2C = '6p2c'
    TYPE_4P4C = '4p4c'
    TYPE_4P2C = '4p2c'
    TYPE_GG45 = 'gg45'
    TYPE_TERA4P = 'tera-4p'
    TYPE_TERA2P = 'tera-2p'
    TYPE_TERA1P = 'tera-1p'
    TYPE_110_PUNCH = '110-punch'
    TYPE_BNC = 'bnc'
    TYPE_F = 'f'
    TYPE_N = 'n'
    TYPE_MRJ21 = 'mrj21'
    TYPE_ST = 'st'
    TYPE_SC = 'sc'
    TYPE_SC_PC = 'sc-pc'
    TYPE_SC_UPC = 'sc-upc'
    TYPE_SC_APC = 'sc-apc'
    TYPE_FC = 'fc'
    TYPE_FC_PC = 'fc-pc'
    TYPE_FC_UPC = 'fc-upc'
    TYPE_FC_APC = 'fc-apc'
    TYPE_LC = 'lc'
    TYPE_LC_PC = 'lc-pc'
    TYPE_LC_UPC = 'lc-upc'
    TYPE_LC_APC = 'lc-apc'
    TYPE_MU = 'mu'
    TYPE_MU_PC = 'mu-pc'
    TYPE_MU_UPC = 'mu-upc'
    TYPE_MU_APC = 'mu-apc'
    TYPE_MTRJ = 'mtrj'
    TYPE_MPO = 'mpo'
    TYPE_LSH = 'lsh'
    TYPE_LSH_PC = 'lsh-pc'
    TYPE_LSH_UPC = 'lsh-upc'
    TYPE_LSH_APC = 'lsh-apc'
    TYPE_LX5 = 'lx5'
    TYPE_LX5_PC = 'lx5-pc'
    TYPE_LX5_UPC = 'lx5-upc'
    TYPE_LX5_APC = 'lx5-apc'
    TYPE_SPLICE = 'splice'
    TYPE_CS = 'cs'
    TYPE_SN = 'sn'
    TYPE_MDC = 'mdc'
    TYPE_SMA_905 = 'sma-905'
    TYPE_SMA_906 = 'sma-906'
    TYPE_URM_P2 = 'urm-p2'
    TYPE_URM_P4 = 'urm-p4'
    TYPE_URM_P8 = 'urm-p8'
    TYPE_USB_A = 'usb-a'
    TYPE_USB_B = 'usb-b'
    TYPE_USB_C = 'usb-c'
    TYPE_USB_MINI_A = 'usb-mini-a'
    TYPE_USB_MINI_B = 'usb-mini-b'
    TYPE_USB_MICRO_A = 'usb-micro-a'
    TYPE_USB_MICRO_B = 'usb-micro-b'
    TYPE_USB_MICRO_AB = 'usb-micro-ab'
    TYPE_OTHER = 'other'

    CHOICES = (
        (
            _('Copper'),
            (
                Choice(TYPE_8P8C, '8P8C'),
                Choice(TYPE_8P6C, '8P6C'),
                Choice(TYPE_8P4C, '8P4C'),
                Choice(TYPE_8P2C, '8P2C'),
                Choice(TYPE_6P6C, '6P6C'),
                Choice(TYPE_6P4C, '6P4C'),
                Choice(TYPE_6P2C, '6P2C'),
                Choice(TYPE_4P4C, '4P4C'),
                Choice(TYPE_4P2C, '4P2C'),
                Choice(TYPE_GG45, 'GG45'),
                Choice(TYPE_TERA4P, 'TERA 4P'),
                Choice(TYPE_TERA2P, 'TERA 2P'),
                Choice(TYPE_TERA1P, 'TERA 1P'),
                Choice(TYPE_110_PUNCH, '110 Punch'),
                Choice(TYPE_BNC, 'BNC'),
                Choice(TYPE_F, 'F Connector'),
                Choice(TYPE_N, 'N Connector'),
                Choice(TYPE_MRJ21, 'MRJ21'),
            ),
        ),
        (
            _('Fiber Optic'),
            (
                Choice(TYPE_FC, 'FC'),
                Choice(TYPE_FC_PC, 'FC/PC'),
                Choice(TYPE_FC_UPC, 'FC/UPC'),
                Choice(TYPE_FC_APC, 'FC/APC'),
                Choice(TYPE_LC, 'LC'),
                Choice(TYPE_LC_PC, 'LC/PC'),
                Choice(TYPE_LC_UPC, 'LC/UPC'),
                Choice(TYPE_LC_APC, 'LC/APC'),
                Choice(TYPE_MU, 'MU'),
                Choice(TYPE_MU_PC, 'MU/PC'),
                Choice(TYPE_MU_UPC, 'MU/UPC'),
                Choice(TYPE_MU_APC, 'MU/APC'),
                Choice(TYPE_LSH, 'LSH'),
                Choice(TYPE_LSH_PC, 'LSH/PC'),
                Choice(TYPE_LSH_UPC, 'LSH/UPC'),
                Choice(TYPE_LSH_APC, 'LSH/APC'),
                Choice(TYPE_LX5, 'LX.5'),
                Choice(TYPE_LX5_PC, 'LX.5/PC'),
                Choice(TYPE_LX5_UPC, 'LX.5/UPC'),
                Choice(TYPE_LX5_APC, 'LX.5/APC'),
                Choice(TYPE_MPO, 'MPO'),
                Choice(TYPE_MTRJ, 'MTRJ'),
                Choice(TYPE_SC, 'SC'),
                Choice(TYPE_SC_PC, 'SC/PC'),
                Choice(TYPE_SC_UPC, 'SC/UPC'),
                Choice(TYPE_SC_APC, 'SC/APC'),
                Choice(TYPE_ST, 'ST'),
                Choice(TYPE_CS, 'CS'),
                Choice(TYPE_SN, 'SN'),
                Choice(TYPE_MDC, 'MDC'),
                Choice(TYPE_SMA_905, 'SMA 905'),
                Choice(TYPE_SMA_906, 'SMA 906'),
                Choice(TYPE_URM_P2, 'URM-P2'),
                Choice(TYPE_URM_P4, 'URM-P4'),
                Choice(TYPE_URM_P8, 'URM-P8'),
                Choice(TYPE_SPLICE, 'Splice'),
            ),
        ),
        (
            _('USB'),
            (
                Choice(TYPE_USB_A, 'USB Type A'),
                Choice(TYPE_USB_B, 'USB Type B'),
                Choice(TYPE_USB_C, 'USB Type C'),
                Choice(TYPE_USB_MINI_A, 'USB Mini A'),
                Choice(TYPE_USB_MINI_B, 'USB Mini B'),
                Choice(TYPE_USB_MICRO_A, 'USB Micro A'),
                Choice(TYPE_USB_MICRO_B, 'USB Micro B'),
                Choice(TYPE_USB_MICRO_AB, 'USB Micro AB'),
            ),
        ),
        (
            _('Other'),
            (
                Choice(TYPE_OTHER, _('Other')),
            )
        )
    )


#
# Cables/links
#

class CableProfileChoices(ChoiceSet):
    # Singles
    SINGLE_1C1P = 'single-1c1p'
    SINGLE_1C2P = 'single-1c2p'
    SINGLE_1C4P = 'single-1c4p'
    SINGLE_1C6P = 'single-1c6p'
    SINGLE_1C8P = 'single-1c8p'
    SINGLE_1C12P = 'single-1c12p'
    SINGLE_1C16P = 'single-1c16p'
    # Trunks
    TRUNK_2C1P = 'trunk-2c1p'
    TRUNK_2C2P = 'trunk-2c2p'
    TRUNK_2C4P = 'trunk-2c4p'
    TRUNK_2C4P_SHUFFLE = 'trunk-2c4p-shuffle'
    TRUNK_2C6P = 'trunk-2c6p'
    TRUNK_2C8P = 'trunk-2c8p'
    TRUNK_2C12P = 'trunk-2c12p'
    TRUNK_4C1P = 'trunk-4c1p'
    TRUNK_4C2P = 'trunk-4c2p'
    TRUNK_4C4P = 'trunk-4c4p'
    TRUNK_4C4P_SHUFFLE = 'trunk-4c4p-shuffle'
    TRUNK_4C6P = 'trunk-4c6p'
    TRUNK_4C8P = 'trunk-4c8p'
    TRUNK_8C4P = 'trunk-8c4p'
    # Breakouts
    BREAKOUT_1C2P_2C1P = 'breakout-1c2p-2c1p'
    BREAKOUT_1C4P_4C1P = 'breakout-1c4p-4c1p'
    BREAKOUT_1C6P_6C1P = 'breakout-1c6p-6c1p'
    BREAKOUT_1C8P_8C1P = 'breakout-1c8p-8c1p'
    BREAKOUT_2C4P_8C1P_SHUFFLE = 'breakout-2c4p-8c1p-shuffle'

    CHOICES = (
        (
            _('Single'),
            (
                Choice(SINGLE_1C1P, _('1C1P')),
                Choice(SINGLE_1C2P, _('1C2P')),
                Choice(SINGLE_1C4P, _('1C4P')),
                Choice(SINGLE_1C6P, _('1C6P')),
                Choice(SINGLE_1C8P, _('1C8P')),
                Choice(SINGLE_1C12P, _('1C12P')),
                Choice(SINGLE_1C16P, _('1C16P')),
            ),
        ),
        (
            _('Trunk'),
            (
                Choice(TRUNK_2C1P, _('2C1P trunk')),
                Choice(TRUNK_2C2P, _('2C2P trunk')),
                Choice(TRUNK_2C4P, _('2C4P trunk')),
                Choice(TRUNK_2C4P_SHUFFLE, _('2C4P trunk (shuffle)')),
                Choice(TRUNK_2C6P, _('2C6P trunk')),
                Choice(TRUNK_2C8P, _('2C8P trunk')),
                Choice(TRUNK_2C12P, _('2C12P trunk')),
                Choice(TRUNK_4C1P, _('4C1P trunk')),
                Choice(TRUNK_4C2P, _('4C2P trunk')),
                Choice(TRUNK_4C4P, _('4C4P trunk')),
                Choice(TRUNK_4C4P_SHUFFLE, _('4C4P trunk (shuffle)')),
                Choice(TRUNK_4C6P, _('4C6P trunk')),
                Choice(TRUNK_4C8P, _('4C8P trunk')),
                Choice(TRUNK_8C4P, _('8C4P trunk')),
            ),
        ),
        (
            _('Breakout'),
            (
                Choice(BREAKOUT_1C2P_2C1P, _('1C2P:2C1P breakout')),
                Choice(BREAKOUT_1C4P_4C1P, _('1C4P:4C1P breakout')),
                Choice(BREAKOUT_1C6P_6C1P, _('1C6P:6C1P breakout')),
                Choice(BREAKOUT_1C8P_8C1P, _('1C8P:8C1P breakout')),
                Choice(BREAKOUT_2C4P_8C1P_SHUFFLE, _('2C4P:8C1P breakout (shuffle)')),
            ),
        ),
    )


class CableTypeChoices(ChoiceSet):
    # Copper - Twisted Pair (UTP/STP)
    TYPE_CAT3 = 'cat3'
    TYPE_CAT5 = 'cat5'
    TYPE_CAT5E = 'cat5e'
    TYPE_CAT6 = 'cat6'
    TYPE_CAT6A = 'cat6a'
    TYPE_CAT7 = 'cat7'
    TYPE_CAT7A = 'cat7a'
    TYPE_CAT8 = 'cat8'
    TYPE_MRJ21_TRUNK = 'mrj21-trunk'

    # Copper - Twinax (DAC)
    TYPE_DAC_ACTIVE = 'dac-active'
    TYPE_DAC_PASSIVE = 'dac-passive'

    # Copper - Coaxial
    TYPE_COAXIAL = 'coaxial'
    TYPE_RG_6 = 'rg-6'
    TYPE_RG_8 = 'rg-8'
    TYPE_RG_11 = 'rg-11'
    TYPE_RG_59 = 'rg-59'
    TYPE_RG_62 = 'rg-62'
    TYPE_RG_213 = 'rg-213'
    TYPE_LMR_100 = 'lmr-100'
    TYPE_LMR_200 = 'lmr-200'
    TYPE_LMR_400 = 'lmr-400'

    # Fiber Optic - Multimode
    TYPE_MMF = 'mmf'
    TYPE_MMF_OM1 = 'mmf-om1'
    TYPE_MMF_OM2 = 'mmf-om2'
    TYPE_MMF_OM3 = 'mmf-om3'
    TYPE_MMF_OM4 = 'mmf-om4'
    TYPE_MMF_OM5 = 'mmf-om5'

    # Fiber Optic - Single-mode
    TYPE_SMF = 'smf'
    TYPE_SMF_OS1 = 'smf-os1'
    TYPE_SMF_OS2 = 'smf-os2'

    # Fiber Optic - Other
    TYPE_AOC = 'aoc'

    # Power
    TYPE_POWER = 'power'

    # USB
    TYPE_USB = 'usb'

    CHOICES = (
        (
            _('Copper - Twisted Pair (UTP/STP)'),
            (
                Choice(TYPE_CAT3, 'CAT3'),
                Choice(TYPE_CAT5, 'CAT5'),
                Choice(TYPE_CAT5E, 'CAT5e'),
                Choice(TYPE_CAT6, 'CAT6'),
                Choice(TYPE_CAT6A, 'CAT6a'),
                Choice(TYPE_CAT7, 'CAT7'),
                Choice(TYPE_CAT7A, 'CAT7a'),
                Choice(TYPE_CAT8, 'CAT8'),
                Choice(TYPE_MRJ21_TRUNK, 'MRJ21 Trunk'),
            ),
        ),
        (
            _('Copper - Twinax (DAC)'),
            (
                Choice(TYPE_DAC_ACTIVE, 'Direct Attach Copper (Active)'),
                Choice(TYPE_DAC_PASSIVE, 'Direct Attach Copper (Passive)'),
            ),
        ),
        (
            _('Copper - Coaxial'),
            (
                Choice(TYPE_COAXIAL, 'Coaxial'),
                Choice(TYPE_RG_6, 'RG-6'),
                Choice(TYPE_RG_8, 'RG-8'),
                Choice(TYPE_RG_11, 'RG-11'),
                Choice(TYPE_RG_59, 'RG-59'),
                Choice(TYPE_RG_62, 'RG-62'),
                Choice(TYPE_RG_213, 'RG-213'),
                Choice(TYPE_LMR_100, 'LMR-100'),
                Choice(TYPE_LMR_200, 'LMR-200'),
                Choice(TYPE_LMR_400, 'LMR-400'),
            ),
        ),
        (
            _('Fiber - Multimode'),
            (
                Choice(TYPE_MMF, 'Multimode Fiber'),
                Choice(TYPE_MMF_OM1, 'Multimode Fiber (OM1)'),
                Choice(TYPE_MMF_OM2, 'Multimode Fiber (OM2)'),
                Choice(TYPE_MMF_OM3, 'Multimode Fiber (OM3)'),
                Choice(TYPE_MMF_OM4, 'Multimode Fiber (OM4)'),
                Choice(TYPE_MMF_OM5, 'Multimode Fiber (OM5)'),
            ),
        ),
        (
            _('Fiber - Single-mode'),
            (
                Choice(TYPE_SMF, 'Single-mode Fiber'),
                Choice(TYPE_SMF_OS1, 'Single-mode Fiber (OS1)'),
                Choice(TYPE_SMF_OS2, 'Single-mode Fiber (OS2)'),
            ),
        ),
        (
            _('Fiber - Other'),
            (Choice(TYPE_AOC, 'Active Optical Cabling (AOC)'),),
        ),
        (
            _('Power'),
            (
                Choice(TYPE_POWER, 'Power'),
            ),
        ),
        (
            _('USB'),
            (
                Choice(TYPE_USB, 'USB'),
            ),
        ),
    )


class LinkStatusChoices(ChoiceSet):

    STATUS_CONNECTED = 'connected'
    STATUS_PLANNED = 'planned'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = (
        Choice(STATUS_CONNECTED, _('Connected'), color='green', description=_('Link is connected and in service')),
        Choice(STATUS_PLANNED, _('Planned'), color='blue', description=_('Planned for future connection')),
        Choice(
            STATUS_DECOMMISSIONING,
            _('Decommissioning'),
            color='yellow',
            description=_('Being removed from service'),
        ),
    )


class CableLengthUnitChoices(ChoiceSet):

    # Metric
    UNIT_KILOMETER = 'km'
    UNIT_METER = 'm'
    UNIT_CENTIMETER = 'cm'

    # Imperial
    UNIT_MILE = 'mi'
    UNIT_FOOT = 'ft'
    UNIT_INCH = 'in'

    CHOICES = (
        Choice(UNIT_KILOMETER, _('Kilometers')),
        Choice(UNIT_METER, _('Meters')),
        Choice(UNIT_CENTIMETER, _('Centimeters')),
        Choice(UNIT_MILE, _('Miles')),
        Choice(UNIT_FOOT, _('Feet')),
        Choice(UNIT_INCH, _('Inches')),
    )


#
# CableTerminations
#

class CableEndChoices(ChoiceSet):

    SIDE_A = 'A'
    SIDE_B = 'B'

    CHOICES = (
        Choice(SIDE_A, 'A'),
        Choice(SIDE_B, 'B'),
    )


#
# PowerFeeds
#

class PowerFeedStatusChoices(ChoiceSet):
    key = 'PowerFeed.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'

    CHOICES = [
        Choice(
            STATUS_OFFLINE,
            _('Offline'),
            color='gray',
            description=_('Installed but not currently supplying power'),
        ),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Supplying power and in service')),
        Choice(STATUS_PLANNED, _('Planned'), color='blue', description=_('Planned for future deployment')),
        Choice(STATUS_FAILED, _('Failed'), color='red', description=_('Malfunctioning or out of service')),
    ]


class PowerFeedTypeChoices(ChoiceSet):

    TYPE_PRIMARY = 'primary'
    TYPE_REDUNDANT = 'redundant'

    CHOICES = (
        Choice(TYPE_PRIMARY, _('Primary'), color='green'),
        Choice(TYPE_REDUNDANT, _('Redundant'), color='cyan'),
    )


class PowerFeedSupplyChoices(ChoiceSet):

    SUPPLY_AC = 'ac'
    SUPPLY_DC = 'dc'

    CHOICES = (
        Choice(SUPPLY_AC, 'AC'),
        Choice(SUPPLY_DC, 'DC'),
    )


class PowerFeedPhaseChoices(ChoiceSet):

    PHASE_SINGLE = 'single-phase'
    PHASE_3PHASE = 'three-phase'

    CHOICES = (
        Choice(PHASE_SINGLE, _('Single phase')),
        Choice(PHASE_3PHASE, _('Three-phase')),
    )


#
# PowerOutlets
#
class PowerOutletStatusChoices(ChoiceSet):
    key = 'PowerOutlet.status'

    STATUS_ENABLED = 'enabled'
    STATUS_DISABLED = 'disabled'
    STATUS_FAULTY = 'faulty'

    CHOICES = [
        Choice(STATUS_ENABLED, _('Enabled'), color='green', description=_('Powered on and supplying power')),
        Choice(STATUS_DISABLED, _('Disabled'), color='red', description=_('Powered off and not supplying power')),
        Choice(STATUS_FAULTY, _('Faulty'), color='gray', description=_('Malfunctioning or in an error state')),
    ]


#
# Cooling
#

class CoolingMethodChoices(ChoiceSet):
    key = 'Device.cooling_method'

    METHOD_AIR = 'air'
    METHOD_LIQUID = 'liquid'
    METHOD_HYBRID = 'hybrid'
    METHOD_IMMERSION = 'immersion'

    CHOICES = [
        (METHOD_AIR, _('Air'), 'cyan'),
        (METHOD_LIQUID, _('Liquid'), 'blue'),
        (METHOD_HYBRID, _('Hybrid'), 'purple'),
        (METHOD_IMMERSION, _('Immersion'), 'indigo'),
    ]


class CoolingSourceTypeChoices(ChoiceSet):

    TYPE_CHILLER = 'chiller'
    TYPE_COOLING_TOWER = 'cooling-tower'
    TYPE_DRY_COOLER = 'dry-cooler'
    TYPE_CRAC = 'crac'
    TYPE_CRAH = 'crah'

    CHOICES = [
        (TYPE_CHILLER, _('Chiller')),
        (TYPE_COOLING_TOWER, _('Cooling tower')),
        (TYPE_DRY_COOLER, _('Dry cooler')),
        (TYPE_CRAC, _('CRAC')),
        (TYPE_CRAH, _('CRAH')),
    ]


class CoolingSourceStatusChoices(ChoiceSet):
    key = 'CoolingSource.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'

    CHOICES = [
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
    ]


class CoolingFeedStatusChoices(ChoiceSet):
    key = 'CoolingFeed.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'

    CHOICES = [
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
    ]


class CoolingFlowDirectionChoices(ChoiceSet):

    TYPE_SUPPLY = 'supply'
    TYPE_RETURN = 'return'

    CHOICES = [
        (TYPE_SUPPLY, _('Supply'), 'blue'),
        (TYPE_RETURN, _('Return'), 'red'),
    ]


class FluidTypeChoices(ChoiceSet):

    FLUID_WATER = 'water'
    FLUID_WATER_GLYCOL = 'water-glycol'
    FLUID_DIELECTRIC = 'dielectric'
    FLUID_REFRIGERANT = 'refrigerant'
    FLUID_OTHER = 'other'

    CHOICES = [
        (FLUID_WATER, _('Water')),
        (FLUID_WATER_GLYCOL, _('Water/glycol')),
        (FLUID_DIELECTRIC, _('Dielectric')),
        (FLUID_REFRIGERANT, _('Refrigerant')),
        (FLUID_OTHER, _('Other')),
    ]


class RackCoolingCapabilityChoices(ChoiceSet):

    AIR_ONLY = 'air-only'
    LIQUID_CAPABLE = 'liquid-capable'
    LIQUID_REQUIRED = 'liquid-required'

    CHOICES = [
        (AIR_ONLY, _('Air only'), 'cyan'),
        (LIQUID_CAPABLE, _('Liquid capable'), 'blue'),
        (LIQUID_REQUIRED, _('Liquid required'), 'purple'),
    ]


class CoolingConnectorTypeChoices(ChoiceSet):

    TYPE_UQD = 'uqd'
    TYPE_UQDB = 'uqdb'
    TYPE_QDC = 'qdc'
    TYPE_CAMLOCK = 'camlock'
    TYPE_NPT = 'npt'
    TYPE_BSP = 'bsp'
    TYPE_PROPRIETARY = 'proprietary'

    CHOICES = [
        (TYPE_UQD, _('UQD (Universal Quick Disconnect)')),
        (TYPE_UQDB, _('UQDB (Universal Quick Disconnect, Blind-mate)')),
        (TYPE_QDC, _('QDC (Quick Disconnect Coupling)')),
        (TYPE_CAMLOCK, _('Camlock (cam-and-groove)')),
        (TYPE_NPT, _('NPT (threaded)')),
        (TYPE_BSP, _('BSP (threaded)')),
        (TYPE_PROPRIETARY, _('Proprietary')),
    ]


#
# VDC
#
class VirtualDeviceContextStatusChoices(ChoiceSet):
    key = 'VirtualDeviceContext.status'

    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_OFFLINE = 'offline'

    CHOICES = [
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Fully operational and in service')),
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_OFFLINE, _('Offline'), color='red', description=_('Configured but not currently in service')),
    ]


#
# InventoryItem
#

class InventoryItemStatusChoices(ChoiceSet):
    key = 'InventoryItem.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = [
        Choice(STATUS_OFFLINE, _('Offline'), color='gray', description=_('Installed but not currently in service')),
        Choice(STATUS_ACTIVE, _('Active'), color='green', description=_('Fully operational and in service')),
        Choice(STATUS_PLANNED, _('Planned'), color='cyan', description=_('Planned for future deployment')),
        Choice(STATUS_STAGED, _('Staged'), color='blue', description=_('Installed and being prepared for service')),
        Choice(STATUS_FAILED, _('Failed'), color='red', description=_('Malfunctioning or out of service')),
        Choice(
            STATUS_DECOMMISSIONING,
            _('Decommissioning'),
            color='yellow',
            description=_('Being removed from service'),
        ),
    ]
