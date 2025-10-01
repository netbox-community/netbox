from django.utils.translation import gettext_lazy as _

from utilities.choices import ChoiceSet


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
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGING, _('Staging'), 'blue'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
        (STATUS_RETIRED, _('Retired'), 'red'),
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
        (STATUS_PLANNED, 'Planned', 'cyan'),
        (STATUS_STAGING, 'Staging', 'blue'),
        (STATUS_ACTIVE, 'Active', 'green'),
        (STATUS_DECOMMISSIONING, 'Decommissioning', 'yellow'),
        (STATUS_RETIRED, 'Retired', 'red'),
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
        (TYPE_2POST, _('2-post frame')),
        (TYPE_4POST, _('4-post frame')),
        (TYPE_CABINET, _('4-post cabinet')),
        (TYPE_WALLFRAME, _('Wall-mounted frame')),
        (TYPE_WALLFRAME_VERTICAL, _('Wall-mounted frame (vertical)')),
        (TYPE_WALLCABINET, _('Wall-mounted cabinet')),
        (TYPE_WALLCABINET_VERTICAL, _('Wall-mounted cabinet (vertical)')),
    )


class RackWidthChoices(ChoiceSet):

    WIDTH_10IN = 10
    WIDTH_19IN = 19
    WIDTH_21IN = 21
    WIDTH_23IN = 23

    CHOICES = (
        (WIDTH_10IN, _('{n} inches').format(n=10)),
        (WIDTH_19IN, _('{n} inches').format(n=19)),
        (WIDTH_21IN, _('{n} inches').format(n=21)),
        (WIDTH_23IN, _('{n} inches').format(n=23)),
    )


class RackStatusChoices(ChoiceSet):
    key = 'Rack.status'

    STATUS_RESERVED = 'reserved'
    STATUS_AVAILABLE = 'available'
    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = [
        (STATUS_RESERVED, _('Reserved'), 'yellow'),
        (STATUS_AVAILABLE, _('Available'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_ACTIVE, _('Active'), 'blue'),
        (STATUS_DEPRECATED, _('Deprecated'), 'red'),
    ]


class RackDimensionUnitChoices(ChoiceSet):

    UNIT_MILLIMETER = 'mm'
    UNIT_INCH = 'in'

    CHOICES = (
        (UNIT_MILLIMETER, _('Millimeters')),
        (UNIT_INCH, _('Inches')),
    )


class RackElevationDetailRenderChoices(ChoiceSet):

    RENDER_JSON = 'json'
    RENDER_SVG = 'svg'

    CHOICES = (
        (RENDER_JSON, 'json'),
        (RENDER_SVG, 'svg')
    )


class RackAirflowChoices(ChoiceSet):
    key = 'Rack.airflow'

    FRONT_TO_REAR = 'front-to-rear'
    REAR_TO_FRONT = 'rear-to-front'

    CHOICES = [
        (FRONT_TO_REAR, _('Front to rear')),
        (REAR_TO_FRONT, _('Rear to front')),
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
        (STATUS_PENDING, _('Pending'), 'cyan'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_STALE, _('Stale'), 'orange'),
    ]


#
# DeviceTypes
#

class SubdeviceRoleChoices(ChoiceSet):

    ROLE_PARENT = 'parent'
    ROLE_CHILD = 'child'

    CHOICES = (
        (ROLE_PARENT, _('Parent')),
        (ROLE_CHILD, _('Child')),
    )


#
# Devices
#

class DeviceFaceChoices(ChoiceSet):

    FACE_FRONT = 'front'
    FACE_REAR = 'rear'

    CHOICES = (
        (FACE_FRONT, _('Front')),
        (FACE_REAR, _('Rear')),
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
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGED, _('Staged'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
        (STATUS_INVENTORY, _('Inventory'), 'purple'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
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
        (AIRFLOW_FRONT_TO_REAR, _('Front to rear')),
        (AIRFLOW_REAR_TO_FRONT, _('Rear to front')),
        (AIRFLOW_LEFT_TO_RIGHT, _('Left to right')),
        (AIRFLOW_RIGHT_TO_LEFT, _('Right to left')),
        (AIRFLOW_SIDE_TO_REAR, _('Side to rear')),
        (AIRFLOW_REAR_TO_SIDE, _('Rear to side')),
        (AIRFLOW_BOTTOM_TO_TOP, _('Bottom to top')),
        (AIRFLOW_TOP_TO_BOTTOM, _('Top to bottom')),
        (AIRFLOW_PASSIVE, _('Passive')),
        (AIRFLOW_MIXED, _('Mixed')),
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
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGED, _('Staged'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
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
        (FRONT_TO_REAR, _('Front to rear')),
        (REAR_TO_FRONT, _('Rear to front')),
        (LEFT_TO_RIGHT, _('Left to right')),
        (RIGHT_TO_LEFT, _('Right to left')),
        (SIDE_TO_REAR, _('Side to rear')),
        (PASSIVE, _('Passive')),
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
            (TYPE_DE9, 'DE-9'),
            (TYPE_DB25, 'DB-25'),
            (TYPE_RJ11, 'RJ-11'),
            (TYPE_RJ12, 'RJ-12'),
            (TYPE_RJ45, 'RJ-45'),
            (TYPE_MINI_DIN_8, 'Mini-DIN 8'),
        )),
        ('USB', (
            (TYPE_USB_A, 'USB Type A'),
            (TYPE_USB_B, 'USB Type B'),
            (TYPE_USB_C, 'USB Type C'),
            (TYPE_USB_MINI_A, 'USB Mini A'),
            (TYPE_USB_MINI_B, 'USB Mini B'),
            (TYPE_USB_MICRO_A, 'USB Micro A'),
            (TYPE_USB_MICRO_B, 'USB Micro B'),
            (TYPE_USB_MICRO_AB, 'USB Micro AB'),
        )),
        ('Other', (
            (TYPE_OTHER, 'Other'),
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
        (SPEED_1200, '1200 bps'),
        (SPEED_2400, '2400 bps'),
        (SPEED_4800, '4800 bps'),
        (SPEED_9600, '9600 bps'),
        (SPEED_19200, '19.2 kbps'),
        (SPEED_38400, '38.4 kbps'),
        (SPEED_57600, '57.6 kbps'),
        (SPEED_115200, '115.2 kbps'),
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
            (TYPE_IEC_C6, 'C6'),
            (TYPE_IEC_C8, 'C8'),
            (TYPE_IEC_C14, 'C14'),
            (TYPE_IEC_C16, 'C16'),
            (TYPE_IEC_C18, 'C18'),
            (TYPE_IEC_C20, 'C20'),
            (TYPE_IEC_C22, 'C22'),
        )),
        ('IEC 60309', (
            (TYPE_IEC_PNE4H, 'P+N+E 4H'),
            (TYPE_IEC_PNE6H, 'P+N+E 6H'),
            (TYPE_IEC_PNE9H, 'P+N+E 9H'),
            (TYPE_IEC_2PE4H, '2P+E 4H'),
            (TYPE_IEC_2PE6H, '2P+E 6H'),
            (TYPE_IEC_2PE9H, '2P+E 9H'),
            (TYPE_IEC_3PE4H, '3P+E 4H'),
            (TYPE_IEC_3PE6H, '3P+E 6H'),
            (TYPE_IEC_3PE9H, '3P+E 9H'),
            (TYPE_IEC_3PNE4H, '3P+N+E 4H'),
            (TYPE_IEC_3PNE6H, '3P+N+E 6H'),
            (TYPE_IEC_3PNE9H, '3P+N+E 9H'),
        )),
        ('IEC 60906-1', (
            (TYPE_IEC_60906_1, 'IEC 60906-1'),
            (TYPE_NBR_14136_10A, '2P+T 10A (NBR 14136)'),
            (TYPE_NBR_14136_20A, '2P+T 20A (NBR 14136)'),
        )),
        (_('NEMA (Non-locking)'), (
            (TYPE_NEMA_115P, 'NEMA 1-15P'),
            (TYPE_NEMA_515P, 'NEMA 5-15P'),
            (TYPE_NEMA_520P, 'NEMA 5-20P'),
            (TYPE_NEMA_530P, 'NEMA 5-30P'),
            (TYPE_NEMA_550P, 'NEMA 5-50P'),
            (TYPE_NEMA_615P, 'NEMA 6-15P'),
            (TYPE_NEMA_620P, 'NEMA 6-20P'),
            (TYPE_NEMA_630P, 'NEMA 6-30P'),
            (TYPE_NEMA_650P, 'NEMA 6-50P'),
            (TYPE_NEMA_1030P, 'NEMA 10-30P'),
            (TYPE_NEMA_1050P, 'NEMA 10-50P'),
            (TYPE_NEMA_1420P, 'NEMA 14-20P'),
            (TYPE_NEMA_1430P, 'NEMA 14-30P'),
            (TYPE_NEMA_1450P, 'NEMA 14-50P'),
            (TYPE_NEMA_1460P, 'NEMA 14-60P'),
            (TYPE_NEMA_1515P, 'NEMA 15-15P'),
            (TYPE_NEMA_1520P, 'NEMA 15-20P'),
            (TYPE_NEMA_1530P, 'NEMA 15-30P'),
            (TYPE_NEMA_1550P, 'NEMA 15-50P'),
            (TYPE_NEMA_1560P, 'NEMA 15-60P'),
        )),
        (_('NEMA (Locking)'), (
            (TYPE_NEMA_L115P, 'NEMA L1-15P'),
            (TYPE_NEMA_L515P, 'NEMA L5-15P'),
            (TYPE_NEMA_L520P, 'NEMA L5-20P'),
            (TYPE_NEMA_L530P, 'NEMA L5-30P'),
            (TYPE_NEMA_L550P, 'NEMA L5-50P'),
            (TYPE_NEMA_L615P, 'NEMA L6-15P'),
            (TYPE_NEMA_L620P, 'NEMA L6-20P'),
            (TYPE_NEMA_L630P, 'NEMA L6-30P'),
            (TYPE_NEMA_L650P, 'NEMA L6-50P'),
            (TYPE_NEMA_L1030P, 'NEMA L10-30P'),
            (TYPE_NEMA_L1420P, 'NEMA L14-20P'),
            (TYPE_NEMA_L1430P, 'NEMA L14-30P'),
            (TYPE_NEMA_L1450P, 'NEMA L14-50P'),
            (TYPE_NEMA_L1460P, 'NEMA L14-60P'),
            (TYPE_NEMA_L1520P, 'NEMA L15-20P'),
            (TYPE_NEMA_L1530P, 'NEMA L15-30P'),
            (TYPE_NEMA_L1550P, 'NEMA L15-50P'),
            (TYPE_NEMA_L1560P, 'NEMA L15-60P'),
            (TYPE_NEMA_L2120P, 'NEMA L21-20P'),
            (TYPE_NEMA_L2130P, 'NEMA L21-30P'),
            (TYPE_NEMA_L2220P, 'NEMA L22-20P'),
            (TYPE_NEMA_L2230P, 'NEMA L22-30P'),
        )),
        (_('California Style'), (
            (TYPE_CS6361C, 'CS6361C'),
            (TYPE_CS6365C, 'CS6365C'),
            (TYPE_CS8165C, 'CS8165C'),
            (TYPE_CS8265C, 'CS8265C'),
            (TYPE_CS8365C, 'CS8365C'),
            (TYPE_CS8465C, 'CS8465C'),
        )),
        (_('International/ITA'), (
            (TYPE_ITA_C, 'ITA Type C (CEE 7/16)'),
            (TYPE_ITA_E, 'ITA Type E (CEE 7/6)'),
            (TYPE_ITA_F, 'ITA Type F (CEE 7/4)'),
            (TYPE_ITA_EF, 'ITA Type E/F (CEE 7/7)'),
            (TYPE_ITA_G, 'ITA Type G (BS 1363)'),
            (TYPE_ITA_H, 'ITA Type H'),
            (TYPE_ITA_I, 'ITA Type I'),
            (TYPE_ITA_J, 'ITA Type J'),
            (TYPE_ITA_K, 'ITA Type K'),
            (TYPE_ITA_L, 'ITA Type L (CEI 23-50)'),
            (TYPE_ITA_M, 'ITA Type M (BS 546)'),
            (TYPE_ITA_N, 'ITA Type N'),
            (TYPE_ITA_O, 'ITA Type O'),
        )),
        ('USB', (
            (TYPE_USB_A, 'USB Type A'),
            (TYPE_USB_B, 'USB Type B'),
            (TYPE_USB_C, 'USB Type C'),
            (TYPE_USB_MINI_A, 'USB Mini A'),
            (TYPE_USB_MINI_B, 'USB Mini B'),
            (TYPE_USB_MICRO_A, 'USB Micro A'),
            (TYPE_USB_MICRO_B, 'USB Micro B'),
            (TYPE_USB_MICRO_AB, 'USB Micro AB'),
            (TYPE_USB_3_B, 'USB 3.0 Type B'),
            (TYPE_USB_3_MICROB, 'USB 3.0 Micro B'),
        )),
        ('Molex', (
            (TYPE_MOLEX_MICRO_FIT_1X2, 'Molex Micro-Fit 1x2'),
            (TYPE_MOLEX_MICRO_FIT_2X2, 'Molex Micro-Fit 2x2'),
            (TYPE_MOLEX_MICRO_FIT_2X4, 'Molex Micro-Fit 2x4'),
        )),
        ('DC', (
            (TYPE_DC, 'DC Terminal'),
        )),
        (_('Proprietary'), (
            (TYPE_SAF_D_GRID, 'Saf-D-Grid'),
            (TYPE_NEUTRIK_POWERCON_20A, 'Neutrik powerCON (20A)'),
            (TYPE_NEUTRIK_POWERCON_32A, 'Neutrik powerCON (32A)'),
            (TYPE_NEUTRIK_POWERCON_TRUE1, 'Neutrik powerCON TRUE1'),
            (TYPE_NEUTRIK_POWERCON_TRUE1_TOP, 'Neutrik powerCON TRUE1 TOP'),
            (TYPE_UBIQUITI_SMARTPOWER, 'Ubiquiti SmartPower'),
        )),
        (_('Other'), (
            (TYPE_HARDWIRED, 'Hardwired'),
            (TYPE_OTHER, 'Other'),
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
            (TYPE_IEC_C5, 'C5'),
            (TYPE_IEC_C7, 'C7'),
            (TYPE_IEC_C13, 'C13'),
            (TYPE_IEC_C15, 'C15'),
            (TYPE_IEC_C17, 'C17'),
            (TYPE_IEC_C19, 'C19'),
            (TYPE_IEC_C21, 'C21'),
        )),
        ('IEC 60309', (
            (TYPE_IEC_PNE4H, 'P+N+E 4H'),
            (TYPE_IEC_PNE6H, 'P+N+E 6H'),
            (TYPE_IEC_PNE9H, 'P+N+E 9H'),
            (TYPE_IEC_2PE4H, '2P+E 4H'),
            (TYPE_IEC_2PE6H, '2P+E 6H'),
            (TYPE_IEC_2PE9H, '2P+E 9H'),
            (TYPE_IEC_3PE4H, '3P+E 4H'),
            (TYPE_IEC_3PE6H, '3P+E 6H'),
            (TYPE_IEC_3PE9H, '3P+E 9H'),
            (TYPE_IEC_3PNE4H, '3P+N+E 4H'),
            (TYPE_IEC_3PNE6H, '3P+N+E 6H'),
            (TYPE_IEC_3PNE9H, '3P+N+E 9H'),
        )),
        ('IEC 60906-1', (
            (TYPE_IEC_60906_1, 'IEC 60906-1'),
            (TYPE_NBR_14136_10A, '2P+T 10A (NBR 14136)'),
            (TYPE_NBR_14136_20A, '2P+T 20A (NBR 14136)'),
        )),
        (_('NEMA (Non-locking)'), (
            (TYPE_NEMA_115R, 'NEMA 1-15R'),
            (TYPE_NEMA_515R, 'NEMA 5-15R'),
            (TYPE_NEMA_520R, 'NEMA 5-20R'),
            (TYPE_NEMA_530R, 'NEMA 5-30R'),
            (TYPE_NEMA_550R, 'NEMA 5-50R'),
            (TYPE_NEMA_615R, 'NEMA 6-15R'),
            (TYPE_NEMA_620R, 'NEMA 6-20R'),
            (TYPE_NEMA_630R, 'NEMA 6-30R'),
            (TYPE_NEMA_650R, 'NEMA 6-50R'),
            (TYPE_NEMA_1030R, 'NEMA 10-30R'),
            (TYPE_NEMA_1050R, 'NEMA 10-50R'),
            (TYPE_NEMA_1420R, 'NEMA 14-20R'),
            (TYPE_NEMA_1430R, 'NEMA 14-30R'),
            (TYPE_NEMA_1450R, 'NEMA 14-50R'),
            (TYPE_NEMA_1460R, 'NEMA 14-60R'),
            (TYPE_NEMA_1515R, 'NEMA 15-15R'),
            (TYPE_NEMA_1520R, 'NEMA 15-20R'),
            (TYPE_NEMA_1530R, 'NEMA 15-30R'),
            (TYPE_NEMA_1550R, 'NEMA 15-50R'),
            (TYPE_NEMA_1560R, 'NEMA 15-60R'),
        )),
        (_('NEMA (Locking)'), (
            (TYPE_NEMA_L115R, 'NEMA L1-15R'),
            (TYPE_NEMA_L515R, 'NEMA L5-15R'),
            (TYPE_NEMA_L520R, 'NEMA L5-20R'),
            (TYPE_NEMA_L530R, 'NEMA L5-30R'),
            (TYPE_NEMA_L550R, 'NEMA L5-50R'),
            (TYPE_NEMA_L615R, 'NEMA L6-15R'),
            (TYPE_NEMA_L620R, 'NEMA L6-20R'),
            (TYPE_NEMA_L630R, 'NEMA L6-30R'),
            (TYPE_NEMA_L650R, 'NEMA L6-50R'),
            (TYPE_NEMA_L1030R, 'NEMA L10-30R'),
            (TYPE_NEMA_L1420R, 'NEMA L14-20R'),
            (TYPE_NEMA_L1430R, 'NEMA L14-30R'),
            (TYPE_NEMA_L1450R, 'NEMA L14-50R'),
            (TYPE_NEMA_L1460R, 'NEMA L14-60R'),
            (TYPE_NEMA_L1520R, 'NEMA L15-20R'),
            (TYPE_NEMA_L1530R, 'NEMA L15-30R'),
            (TYPE_NEMA_L1550R, 'NEMA L15-50R'),
            (TYPE_NEMA_L1560R, 'NEMA L15-60R'),
            (TYPE_NEMA_L2120R, 'NEMA L21-20R'),
            (TYPE_NEMA_L2130R, 'NEMA L21-30R'),
            (TYPE_NEMA_L2220R, 'NEMA L22-20R'),
            (TYPE_NEMA_L2230R, 'NEMA L22-30R'),
        )),
        (_('California Style'), (
            (TYPE_CS6360C, 'CS6360C'),
            (TYPE_CS6364C, 'CS6364C'),
            (TYPE_CS8164C, 'CS8164C'),
            (TYPE_CS8264C, 'CS8264C'),
            (TYPE_CS8364C, 'CS8364C'),
            (TYPE_CS8464C, 'CS8464C'),
        )),
        (_('ITA/International'), (
            (TYPE_ITA_E, 'ITA Type E (CEE 7/5)'),
            (TYPE_ITA_F, 'ITA Type F (CEE 7/3)'),
            (TYPE_ITA_G, 'ITA Type G (BS 1363)'),
            (TYPE_ITA_H, 'ITA Type H'),
            (TYPE_ITA_I, 'ITA Type I'),
            (TYPE_ITA_J, 'ITA Type J'),
            (TYPE_ITA_K, 'ITA Type K'),
            (TYPE_ITA_L, 'ITA Type L (CEI 23-50)'),
            (TYPE_ITA_M, 'ITA Type M (BS 546)'),
            (TYPE_ITA_N, 'ITA Type N'),
            (TYPE_ITA_O, 'ITA Type O'),
            (TYPE_ITA_MULTISTANDARD, 'ITA Multistandard'),
        )),
        ('USB', (
            (TYPE_USB_A, 'USB Type A'),
            (TYPE_USB_MICROB, 'USB Micro B'),
            (TYPE_USB_C, 'USB Type C'),
        )),
        ('Molex', (
            (TYPE_MOLEX_MICRO_FIT_1X2, 'Molex Micro-Fit 1x2'),
            (TYPE_MOLEX_MICRO_FIT_2X2, 'Molex Micro-Fit 2x2'),
            (TYPE_MOLEX_MICRO_FIT_2X4, 'Molex Micro-Fit 2x4'),
        )),
        ('DC', (
            (TYPE_DC, 'DC Terminal'),
        )),
        (_('Proprietary'), (
            (TYPE_EATON_C39, 'Eaton C39'),
            (TYPE_HDOT_CX, 'HDOT Cx'),
            (TYPE_SAF_D_GRID, 'Saf-D-Grid'),
            (TYPE_NEUTRIK_POWERCON_20A, 'Neutrik powerCON (20A)'),
            (TYPE_NEUTRIK_POWERCON_32A, 'Neutrik powerCON (32A)'),
            (TYPE_NEUTRIK_POWERCON_TRUE1, 'Neutrik powerCON TRUE1'),
            (TYPE_NEUTRIK_POWERCON_TRUE1_TOP, 'Neutrik powerCON TRUE1 TOP'),
            (TYPE_UBIQUITI_SMARTPOWER, 'Ubiquiti SmartPower'),
        )),
        (_('Other'), (
            (TYPE_HARDWIRED, 'Hardwired'),
            (TYPE_OTHER, 'Other'),
        )),
    )


class PowerOutletFeedLegChoices(ChoiceSet):

    FEED_LEG_A = 'A'
    FEED_LEG_B = 'B'
    FEED_LEG_C = 'C'

    CHOICES = (
        (FEED_LEG_A, 'A'),
        (FEED_LEG_B, 'B'),
        (FEED_LEG_C, 'C'),
    )


#
# Interfaces
#

class InterfaceKindChoices(ChoiceSet):
    KIND_PHYSICAL = 'physical'
    KIND_VIRTUAL = 'virtual'
    KIND_WIRELESS = 'wireless'

    CHOICES = (
        (KIND_PHYSICAL, _('Physical')),
        (KIND_VIRTUAL, _('Virtual')),
        (KIND_WIRELESS, _('Wireless')),
    )


class InterfaceTypeChoices(ChoiceSet):

    # Virtual
    TYPE_VIRTUAL = 'virtual'
    TYPE_BRIDGE = 'bridge'
    TYPE_LAG = 'lag'

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

    # Ethernet (modular)
    TYPE_100ME_SFP = '100base-x-sfp'
    TYPE_1GE_GBIC = '1000base-x-gbic'
    TYPE_1GE_SFP = '1000base-x-sfp'
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
    TYPE_800GE_QSFP_DD = '800gbase-x-qsfpdd'
    TYPE_800GE_OSFP = '800gbase-x-osfp'

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
                (TYPE_VIRTUAL, _('Virtual')),
                (TYPE_BRIDGE, _('Bridge')),
                (TYPE_LAG, _('Link Aggregation Group (LAG)')),
            ),
        ),
        (
            _('FastEthernet (100 Mbps)'),
            (
                (TYPE_100ME_FX, '100BASE-FX (10/100ME)'),
                (TYPE_100ME_LFX, '100BASE-LFX (10/100ME)'),
                (TYPE_100ME_FIXED, '100BASE-TX (10/100ME)'),
                (TYPE_100ME_T1, '100BASE-T1 (10/100ME)'),
            ),
        ),
        (
            _('GigabitEthernet (1 Gbps)'),
            (
                (TYPE_1GE_BX10_D, '1000BASE-BX10-D (1GE BiDi Down)'),
                (TYPE_1GE_BX10_U, '1000BASE-BX10-U (1GE BiDi Up)'),
                (TYPE_1GE_CWDM, '1000BASE-CWDM (1GE)'),
                (TYPE_1GE_CX, '1000BASE-CX (1GE DAC)'),
                (TYPE_1GE_DWDM, '1000BASE-DWDM (1GE)'),
                (TYPE_1GE_EX, '1000BASE-EX (1GE)'),
                (TYPE_1GE_LSX, '1000BASE-LSX (1GE)'),
                (TYPE_1GE_LX_FIXED, '1000BASE-LX (1GE)'),
                (TYPE_1GE_LX10, '1000BASE-LX10/LH (1GE)'),
                (TYPE_1GE_SX_FIXED, '1000BASE-SX (1GE)'),
                (TYPE_1GE_FIXED, '1000BASE-T (1GE)'),
                (TYPE_1GE_TX_FIXED, '1000BASE-TX (1GE)'),
                (TYPE_1GE_ZX, '1000BASE-ZX (1GE)'),
            ),
        ),
        (
            _('2.5/5 Gbps Ethernet'),
            (
                (TYPE_2GE_FIXED, '2.5GBASE-T (2.5GE)'),
                (TYPE_5GE_FIXED, '5GBASE-T (5GE)'),
            ),
        ),
        (
            _('10 Gbps Ethernet'),
            (
                (TYPE_10GE_BR_D, '10GBASE-BR-D (10GE BiDi Down)'),
                (TYPE_10GE_BR_U, '10GBASE-BR-U (10GE BiDi Up)'),
                (TYPE_10GE_CX4, '10GBASE-CX4 (10GE DAC)'),
                (TYPE_10GE_ER, '10GBASE-ER (10GE)'),
                (TYPE_10GE_LR, '10GBASE-LR (10GE)'),
                (TYPE_10GE_LRM, '10GBASE-LRM (10GE)'),
                (TYPE_10GE_LX4, '10GBASE-LX4 (10GE)'),
                (TYPE_10GE_SR, '10GBASE-SR (10GE)'),
                (TYPE_10GE_FIXED, '10GBASE-T (10GE)'),
                (TYPE_10GE_ZR, '10GBASE-ZR (10GE)'),
            )
        ),
        (
            _('25 Gbps Ethernet'),
            (
                (TYPE_25GE_CR, '25GBASE-CR (25GE DAC)'),
                (TYPE_25GE_ER, '25GBASE-ER (25GE)'),
                (TYPE_25GE_LR, '25GBASE-LR (25GE)'),
                (TYPE_25GE_SR, '25GBASE-SR (25GE)'),
                (TYPE_25GE_T, '25GBASE-T (25GE)'),
            )
        ),
        (
            _('40 Gbps Ethernet'),
            (
                (TYPE_40GE_CR4, '40GBASE-CR4 (40GE DAC)'),
                (TYPE_40GE_ER4, '40GBASE-ER4 (40GE)'),
                (TYPE_40GE_FR4, '40GBASE-FR4 (40GE)'),
                (TYPE_40GE_LR4, '40GBASE-LR4 (40GE)'),
                (TYPE_40GE_SR4, '40GBASE-SR4 (40GE)'),
            )
        ),
        (
            _('50 Gbps Ethernet'),
            (
                (TYPE_50GE_CR, '50GBASE-CR (50GE DAC)'),
                (TYPE_50GE_ER, '50GBASE-ER (50GE)'),
                (TYPE_50GE_FR, '50GBASE-FR (50GE)'),
                (TYPE_50GE_LR, '50GBASE-LR (50GE)'),
                (TYPE_50GE_SR, '50GBASE-SR (50GE)'),
            )
        ),
        (
            _('100 Gbps Ethernet'),
            (
                (TYPE_100GE_CR1, '100GBASE-CR1 (100GE DAC)'),
                (TYPE_100GE_CR2, '100GBASE-CR2 (100GE DAC)'),
                (TYPE_100GE_CR4, '100GBASE-CR4 (100GE DAC)'),
                (TYPE_100GE_CR10, '100GBASE-CR10 (100GE DAC)'),
                (TYPE_100GE_CWDM4, '100GBASE-CWDM4 (100GE)'),
                (TYPE_100GE_DR, '100GBASE-DR (100GE)'),
                (TYPE_100GE_ER4, '100GBASE-ER4 (100GE)'),
                (TYPE_100GE_FR1, '100GBASE-FR1 (100GE)'),
                (TYPE_100GE_LR1, '100GBASE-LR1 (100GE)'),
                (TYPE_100GE_LR4, '100GBASE-LR4 (100GE)'),
                (TYPE_100GE_SR1, '100GBASE-SR1 (100GE)'),
                (TYPE_100GE_SR1_2, '100GBASE-SR1.2 (100GE BiDi)'),
                (TYPE_100GE_SR2, '100GBASE-SR2 (100GE)'),
                (TYPE_100GE_SR4, '100GBASE-SR4 (100GE)'),
                (TYPE_100GE_SR10, '100GBASE-SR10 (100GE)'),
                (TYPE_100GE_ZR, '100GBASE-ZR (100GE)'),
            )
        ),
        (
            _('200 Gbps Ethernet'),
            (
                (TYPE_200GE_CR2, '200GBASE-CR2 (200GE)'),
                (TYPE_200GE_CR4, '200GBASE-CR4 (200GE)'),
                (TYPE_200GE_DR4, '200GBASE-DR4 (200GE)'),
                (TYPE_200GE_ER4, '200GBASE-ER4 (200GE)'),
                (TYPE_200GE_FR4, '200GBASE-FR4 (200GE)'),
                (TYPE_200GE_LR4, '200GBASE-LR4 (200GE)'),
                (TYPE_200GE_SR2, '200GBASE-SR2 (200GE)'),
                (TYPE_200GE_SR4, '200GBASE-SR4 (200GE)'),
                (TYPE_200GE_VR2, '200GBASE-VR2 (200GE)'),
            )
        ),
        (
            _('400 Gbps Ethernet'),
            (
                (TYPE_400GE_CR4, '400GBASE-CR4 (400GE)'),
                (TYPE_400GE_DR4, '400GBASE-DR4 (400GE)'),
                (TYPE_400GE_ER8, '400GBASE-ER8 (400GE)'),
                (TYPE_400GE_FR4, '400GBASE-FR4 (400GE)'),
                (TYPE_400GE_FR8, '400GBASE-FR8 (400GE)'),
                (TYPE_400GE_LR4, '400GBASE-LR4 (400GE)'),
                (TYPE_400GE_LR8, '400GBASE-LR8 (400GE)'),
                (TYPE_400GE_SR4, '400GBASE-SR4 (400GE)'),
                (TYPE_400GE_SR4_2, '400GBASE-SR4.2 (400GE BiDi)'),
                (TYPE_400GE_SR8, '400GBASE-SR8 (400GE)'),
                (TYPE_400GE_SR16, '400GBASE-SR16 (400GE)'),
                (TYPE_400GE_VR4, '400GBASE-VR4 (400GE)'),
                (TYPE_400GE_ZR, '400GBASE-ZR (400GE)'),
            )
        ),
        (
            _('800 Gbps Ethernet'),
            (
                (TYPE_800GE_CR8, '800GBASE-CR8 (800GE)'),
                (TYPE_800GE_DR8, '800GBASE-DR8 (800GE)'),
                (TYPE_800GE_SR8, '800GBASE-SR8 (800GE)'),
                (TYPE_800GE_VR8, '800GBASE-VR8 (800GE)'),
            )
        ),
        (
            _('Pluggable transceivers'),
            (
                (TYPE_100ME_SFP, 'SFP (100ME)'),
                (TYPE_1GE_GBIC, 'GBIC (1GE)'),
                (TYPE_1GE_SFP, 'SFP (1GE)'),
                (TYPE_10GE_SFP_PLUS, 'SFP+ (10GE)'),
                (TYPE_10GE_XENPAK, 'XENPAK (10GE)'),
                (TYPE_10GE_XFP, 'XFP (10GE)'),
                (TYPE_10GE_X2, 'X2 (10GE)'),
                (TYPE_25GE_SFP28, 'SFP28 (25GE)'),
                (TYPE_40GE_QSFP_PLUS, 'QSFP+ (40GE)'),
                (TYPE_50GE_QSFP28, 'QSFP28 (50GE)'),
                (TYPE_50GE_SFP56, 'SFP56 (50GE)'),
                (TYPE_100GE_CFP, 'CFP (100GE)'),
                (TYPE_100GE_CFP2, 'CFP2 (100GE)'),
                (TYPE_100GE_CFP4, 'CFP4 (100GE)'),
                (TYPE_100GE_CXP, 'CXP (100GE)'),
                (TYPE_100GE_CPAK, 'Cisco CPAK (100GE)'),
                (TYPE_100GE_DSFP, 'DSFP (100GE)'),
                (TYPE_100GE_QSFP28, 'QSFP28 (100GE)'),
                (TYPE_100GE_QSFP_DD, 'QSFP-DD (100GE)'),
                (TYPE_100GE_SFP_DD, 'SFP-DD (100GE)'),
                (TYPE_200GE_CFP2, 'CFP2 (200GE)'),
                (TYPE_200GE_QSFP56, 'QSFP56 (200GE)'),
                (TYPE_200GE_QSFP_DD, 'QSFP-DD (200GE)'),
                (TYPE_400GE_QSFP112, 'QSFP112 (400GE)'),
                (TYPE_400GE_QSFP_DD, 'QSFP-DD (400GE)'),
                (TYPE_400GE_CDFP, 'CDFP (400GE)'),
                (TYPE_400GE_CFP2, 'CFP2 (400GE)'),
                (TYPE_400GE_CFP8, 'CPF8 (400GE)'),
                (TYPE_400GE_OSFP, 'OSFP (400GE)'),
                (TYPE_400GE_OSFP_RHS, 'OSFP-RHS (400GE)'),
                (TYPE_800GE_OSFP, 'OSFP (800GE)'),
                (TYPE_800GE_QSFP_DD, 'QSFP-DD (800GE)'),
            )
        ),
        (
            _('Backplane Ethernet'),
            (
                (TYPE_1GE_KX, '1000BASE-KX (1GE)'),
                (TYPE_2GE_KX, '2.5GBASE-KX (2.5GE)'),
                (TYPE_5GE_KR, '5GBASE-KR (5GE)'),
                (TYPE_10GE_KR, '10GBASE-KR (10GE)'),
                (TYPE_10GE_KX4, '10GBASE-KX4 (10GE)'),
                (TYPE_25GE_KR, '25GBASE-KR (25GE)'),
                (TYPE_40GE_KR4, '40GBASE-KR4 (40GE)'),
                (TYPE_50GE_KR, '50GBASE-KR (50GE)'),
                (TYPE_100GE_KP4, '100GBASE-KP4 (100GE)'),
                (TYPE_100GE_KR2, '100GBASE-KR2 (100GE)'),
                (TYPE_100GE_KR4, '100GBASE-KR4 (100GE)'),
            )
        ),
        (
            _('Wireless'),
            (
                (TYPE_80211A, 'IEEE 802.11a'),
                (TYPE_80211G, 'IEEE 802.11b/g'),
                (TYPE_80211N, 'IEEE 802.11n (Wi-Fi 4)'),
                (TYPE_80211AC, 'IEEE 802.11ac (Wi-Fi 5)'),
                (TYPE_80211AD, 'IEEE 802.11ad (WiGig)'),
                (TYPE_80211AX, 'IEEE 802.11ax (Wi-Fi 6)'),
                (TYPE_80211AY, 'IEEE 802.11ay (WiGig)'),
                (TYPE_80211BE, 'IEEE 802.11be (Wi-Fi 7)'),
                (TYPE_802151, 'IEEE 802.15.1 (Bluetooth)'),
                (TYPE_802154, 'IEEE 802.15.4 (LR-WPAN)'),
                (TYPE_OTHER_WIRELESS, 'Other (Wireless)'),
            )
        ),
        (
            _('Cellular'),
            (
                (TYPE_GSM, 'GSM'),
                (TYPE_CDMA, 'CDMA'),
                (TYPE_LTE, 'LTE'),
                (TYPE_4G, '4G'),
                (TYPE_5G, '5G'),
            )
        ),
        (
            'SONET',
            (
                (TYPE_SONET_OC3, 'OC-3/STM-1'),
                (TYPE_SONET_OC12, 'OC-12/STM-4'),
                (TYPE_SONET_OC48, 'OC-48/STM-16'),
                (TYPE_SONET_OC192, 'OC-192/STM-64'),
                (TYPE_SONET_OC768, 'OC-768/STM-256'),
                (TYPE_SONET_OC1920, 'OC-1920/STM-640'),
                (TYPE_SONET_OC3840, 'OC-3840/STM-1234'),
            )
        ),
        (
            'FibreChannel',
            (
                (TYPE_1GFC_SFP, 'SFP (1GFC)'),
                (TYPE_2GFC_SFP, 'SFP (2GFC)'),
                (TYPE_4GFC_SFP, 'SFP (4GFC)'),
                (TYPE_8GFC_SFP_PLUS, 'SFP+ (8GFC)'),
                (TYPE_16GFC_SFP_PLUS, 'SFP+ (16GFC)'),
                (TYPE_32GFC_SFP28, 'SFP28 (32GFC)'),
                (TYPE_32GFC_SFP_PLUS, 'SFP+ (32GFC)'),
                (TYPE_64GFC_QSFP_PLUS, 'QSFP+ (64GFC)'),
                (TYPE_64GFC_SFP_DD, 'SFP-DD (64GFC)'),
                (TYPE_64GFC_SFP_PLUS, 'SFP+ (64GFC)'),
                (TYPE_128GFC_QSFP28, 'QSFP28 (128GFC)'),
            )
        ),
        (
            'InfiniBand',
            (
                (TYPE_INFINIBAND_SDR, 'SDR (2 Gbps)'),
                (TYPE_INFINIBAND_DDR, 'DDR (4 Gbps)'),
                (TYPE_INFINIBAND_QDR, 'QDR (8 Gbps)'),
                (TYPE_INFINIBAND_FDR10, 'FDR10 (10 Gbps)'),
                (TYPE_INFINIBAND_FDR, 'FDR (13.5 Gbps)'),
                (TYPE_INFINIBAND_EDR, 'EDR (25 Gbps)'),
                (TYPE_INFINIBAND_HDR, 'HDR (50 Gbps)'),
                (TYPE_INFINIBAND_NDR, 'NDR (100 Gbps)'),
                (TYPE_INFINIBAND_XDR, 'XDR (250 Gbps)'),
            )
        ),
        (
            _('Serial'),
            (
                (TYPE_T1, 'T1 (1.544 Mbps)'),
                (TYPE_E1, 'E1 (2.048 Mbps)'),
                (TYPE_T3, 'T3 (45 Mbps)'),
                (TYPE_E3, 'E3 (34 Mbps)'),
            )
        ),
        (
            'ATM',
            (
                (TYPE_XDSL, 'xDSL'),
            )
        ),
        (
            _('Coaxial'),
            (
                (TYPE_DOCSIS, 'DOCSIS'),
                (TYPE_MOCA, 'MoCA'),
            )
        ),
        (
            'PON',
            (
                (TYPE_BPON, 'BPON (622 Mbps / 155 Mbps)'),
                (TYPE_EPON, 'EPON (1 Gbps)'),
                (TYPE_10G_EPON, '10G-EPON (10 Gbps)'),
                (TYPE_GPON, 'GPON (2.5 Gbps / 1.25 Gbps)'),
                (TYPE_XG_PON, 'XG-PON (10 Gbps / 2.5 Gbps)'),
                (TYPE_XGS_PON, 'XGS-PON (10 Gbps)'),
                (TYPE_NG_PON2, 'NG-PON2 (TWDM-PON) (4x10 Gbps)'),
                (TYPE_25G_PON, '25G-PON (25 Gbps)'),
                (TYPE_50G_PON, '50G-PON (50 Gbps)'),
            )
        ),
        (
            _('Stacking'),
            (
                (TYPE_STACKWISE, 'Cisco StackWise'),
                (TYPE_STACKWISE_PLUS, 'Cisco StackWise Plus'),
                (TYPE_FLEXSTACK, 'Cisco FlexStack'),
                (TYPE_FLEXSTACK_PLUS, 'Cisco FlexStack Plus'),
                (TYPE_STACKWISE80, 'Cisco StackWise-80'),
                (TYPE_STACKWISE160, 'Cisco StackWise-160'),
                (TYPE_STACKWISE320, 'Cisco StackWise-320'),
                (TYPE_STACKWISE480, 'Cisco StackWise-480'),
                (TYPE_STACKWISE1T, 'Cisco StackWise-1T'),
                (TYPE_JUNIPER_VCP, 'Juniper VCP'),
                (TYPE_SUMMITSTACK, 'Extreme SummitStack'),
                (TYPE_SUMMITSTACK128, 'Extreme SummitStack-128'),
                (TYPE_SUMMITSTACK256, 'Extreme SummitStack-256'),
                (TYPE_SUMMITSTACK512, 'Extreme SummitStack-512'),
            )
        ),
        (
            _('Other'),
            (
                (TYPE_OTHER, _('Other')),
            )
        ),
    )


class InterfaceSpeedChoices(ChoiceSet):
    key = 'Interface.speed'

    CHOICES = [
        (10000, '10 Mbps'),
        (100000, '100 Mbps'),
        (1000000, '1 Gbps'),
        (2500000, '2.5 Gbps'),
        (5000000, '5 Gbps'),
        (10000000, '10 Gbps'),
        (25000000, '25 Gbps'),
        (40000000, '40 Gbps'),
        (100000000, '100 Gbps'),
        (200000000, '200 Gbps'),
        (400000000, '400 Gbps'),
    ]


class InterfaceDuplexChoices(ChoiceSet):

    DUPLEX_HALF = 'half'
    DUPLEX_FULL = 'full'
    DUPLEX_AUTO = 'auto'

    CHOICES = (
        (DUPLEX_HALF, _('Half')),
        (DUPLEX_FULL, _('Full')),
        (DUPLEX_AUTO, _('Auto')),
    )


class InterfaceModeChoices(ChoiceSet):

    MODE_ACCESS = 'access'
    MODE_TAGGED = 'tagged'
    MODE_TAGGED_ALL = 'tagged-all'
    MODE_Q_IN_Q = 'q-in-q'

    CHOICES = (
        (MODE_ACCESS, _('Access')),
        (MODE_TAGGED, _('Tagged')),
        (MODE_TAGGED_ALL, _('Tagged (All)')),
        (MODE_Q_IN_Q, _('Q-in-Q (802.1ad)')),
    )


class InterfacePoEModeChoices(ChoiceSet):

    MODE_PD = 'pd'
    MODE_PSE = 'pse'

    CHOICES = (
        (MODE_PD, 'PD'),
        (MODE_PSE, 'PSE'),
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
                (TYPE_1_8023AF, '802.3af (Type 1)'),
                (TYPE_2_8023AT, '802.3at (Type 2)'),
                (TYPE_3_8023BT, '802.3bt (Type 3)'),
                (TYPE_4_8023BT, '802.3bt (Type 4)'),
            )
        ),
        (
            _('Passive'),
            (
                (PASSIVE_24V_2PAIR, _('Passive 24V (2-pair)')),
                (PASSIVE_24V_4PAIR, _('Passive 24V (4-pair)')),
                (PASSIVE_48V_2PAIR, _('Passive 48V (2-pair)')),
                (PASSIVE_48V_4PAIR, _('Passive 48V (4-pair)')),
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
                (TYPE_8P8C, '8P8C'),
                (TYPE_8P6C, '8P6C'),
                (TYPE_8P4C, '8P4C'),
                (TYPE_8P2C, '8P2C'),
                (TYPE_6P6C, '6P6C'),
                (TYPE_6P4C, '6P4C'),
                (TYPE_6P2C, '6P2C'),
                (TYPE_4P4C, '4P4C'),
                (TYPE_4P2C, '4P2C'),
                (TYPE_GG45, 'GG45'),
                (TYPE_TERA4P, 'TERA 4P'),
                (TYPE_TERA2P, 'TERA 2P'),
                (TYPE_TERA1P, 'TERA 1P'),
                (TYPE_110_PUNCH, '110 Punch'),
                (TYPE_BNC, 'BNC'),
                (TYPE_F, 'F Connector'),
                (TYPE_N, 'N Connector'),
                (TYPE_MRJ21, 'MRJ21'),
            ),
        ),
        (
            _('Fiber Optic'),
            (
                (TYPE_FC, 'FC'),
                (TYPE_FC_PC, 'FC/PC'),
                (TYPE_FC_UPC, 'FC/UPC'),
                (TYPE_FC_APC, 'FC/APC'),
                (TYPE_LC, 'LC'),
                (TYPE_LC_PC, 'LC/PC'),
                (TYPE_LC_UPC, 'LC/UPC'),
                (TYPE_LC_APC, 'LC/APC'),
                (TYPE_LSH, 'LSH'),
                (TYPE_LSH_PC, 'LSH/PC'),
                (TYPE_LSH_UPC, 'LSH/UPC'),
                (TYPE_LSH_APC, 'LSH/APC'),
                (TYPE_LX5, 'LX.5'),
                (TYPE_LX5_PC, 'LX.5/PC'),
                (TYPE_LX5_UPC, 'LX.5/UPC'),
                (TYPE_LX5_APC, 'LX.5/APC'),
                (TYPE_MPO, 'MPO'),
                (TYPE_MTRJ, 'MTRJ'),
                (TYPE_SC, 'SC'),
                (TYPE_SC_PC, 'SC/PC'),
                (TYPE_SC_UPC, 'SC/UPC'),
                (TYPE_SC_APC, 'SC/APC'),
                (TYPE_ST, 'ST'),
                (TYPE_CS, 'CS'),
                (TYPE_SN, 'SN'),
                (TYPE_SMA_905, 'SMA 905'),
                (TYPE_SMA_906, 'SMA 906'),
                (TYPE_URM_P2, 'URM-P2'),
                (TYPE_URM_P4, 'URM-P4'),
                (TYPE_URM_P8, 'URM-P8'),
                (TYPE_SPLICE, 'Splice'),
            ),
        ),
        (
            _('USB'),
            (
                (TYPE_USB_A, 'USB Type A'),
                (TYPE_USB_B, 'USB Type B'),
                (TYPE_USB_C, 'USB Type C'),
                (TYPE_USB_MINI_A, 'USB Mini A'),
                (TYPE_USB_MINI_B, 'USB Mini B'),
                (TYPE_USB_MICRO_A, 'USB Micro A'),
                (TYPE_USB_MICRO_B, 'USB Micro B'),
                (TYPE_USB_MICRO_AB, 'USB Micro AB'),
            ),
        ),
        (
            _('Other'),
            (
                (TYPE_OTHER, _('Other')),
            )
        )
    )


#
# Cables/links
#


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
                (TYPE_CAT3, 'CAT3'),
                (TYPE_CAT5, 'CAT5'),
                (TYPE_CAT5E, 'CAT5e'),
                (TYPE_CAT6, 'CAT6'),
                (TYPE_CAT6A, 'CAT6a'),
                (TYPE_CAT7, 'CAT7'),
                (TYPE_CAT7A, 'CAT7a'),
                (TYPE_CAT8, 'CAT8'),
                (TYPE_MRJ21_TRUNK, 'MRJ21 Trunk'),
            ),
        ),
        (
            _('Copper - Twinax (DAC)'),
            (
                (TYPE_DAC_ACTIVE, 'Direct Attach Copper (Active)'),
                (TYPE_DAC_PASSIVE, 'Direct Attach Copper (Passive)'),
            ),
        ),
        (
            _('Copper - Coaxial'),
            (
                (TYPE_COAXIAL, 'Coaxial'),
            ),
        ),
        (
            _('Fiber - Multimode'),
            (
                (TYPE_MMF, 'Multimode Fiber'),
                (TYPE_MMF_OM1, 'Multimode Fiber (OM1)'),
                (TYPE_MMF_OM2, 'Multimode Fiber (OM2)'),
                (TYPE_MMF_OM3, 'Multimode Fiber (OM3)'),
                (TYPE_MMF_OM4, 'Multimode Fiber (OM4)'),
                (TYPE_MMF_OM5, 'Multimode Fiber (OM5)'),
            ),
        ),
        (
            _('Fiber - Single-mode'),
            (
                (TYPE_SMF, 'Single-mode Fiber'),
                (TYPE_SMF_OS1, 'Single-mode Fiber (OS1)'),
                (TYPE_SMF_OS2, 'Single-mode Fiber (OS2)'),
            ),
        ),
        (
            _('Fiber - Other'),
            ((TYPE_AOC, 'Active Optical Cabling (AOC)'),),
        ),
        (
            _('Power'),
            (
                (TYPE_POWER, 'Power'),
            ),
        ),
        (
            _('USB'),
            (
                (TYPE_USB, 'USB'),
            ),
        ),
    )


class LinkStatusChoices(ChoiceSet):

    STATUS_CONNECTED = 'connected'
    STATUS_PLANNED = 'planned'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = (
        (STATUS_CONNECTED, _('Connected'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'blue'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
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
        (UNIT_KILOMETER, _('Kilometers')),
        (UNIT_METER, _('Meters')),
        (UNIT_CENTIMETER, _('Centimeters')),
        (UNIT_MILE, _('Miles')),
        (UNIT_FOOT, _('Feet')),
        (UNIT_INCH, _('Inches')),
    )


#
# CableTerminations
#

class CableEndChoices(ChoiceSet):

    SIDE_A = 'A'
    SIDE_B = 'B'

    CHOICES = (
        (SIDE_A, 'A'),
        (SIDE_B, 'B'),
        # ('', ''),
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
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
    ]


class PowerFeedTypeChoices(ChoiceSet):

    TYPE_PRIMARY = 'primary'
    TYPE_REDUNDANT = 'redundant'

    CHOICES = (
        (TYPE_PRIMARY, _('Primary'), 'green'),
        (TYPE_REDUNDANT, _('Redundant'), 'cyan'),
    )


class PowerFeedSupplyChoices(ChoiceSet):

    SUPPLY_AC = 'ac'
    SUPPLY_DC = 'dc'

    CHOICES = (
        (SUPPLY_AC, 'AC'),
        (SUPPLY_DC, 'DC'),
    )


class PowerFeedPhaseChoices(ChoiceSet):

    PHASE_SINGLE = 'single-phase'
    PHASE_3PHASE = 'three-phase'

    CHOICES = (
        (PHASE_SINGLE, _('Single phase')),
        (PHASE_3PHASE, _('Three-phase')),
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
        (STATUS_ENABLED, _('Enabled'), 'green'),
        (STATUS_DISABLED, _('Disabled'), 'red'),
        (STATUS_FAULTY, _('Faulty'), 'gray'),
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
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_OFFLINE, _('Offline'), 'red'),
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
        (STATUS_OFFLINE, _('Offline'), 'gray'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGED, _('Staged'), 'blue'),
        (STATUS_FAILED, _('Failed'), 'red'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
    ]
