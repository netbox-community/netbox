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
        (STATUS_PLANNED, _('Planned'), 'cyan'),
        (STATUS_STAGING, _('Staging'), 'blue'),
        (STATUS_ACTIVE, _('Active'), 'green'),
        (STATUS_DECOMMISSIONING, _('Decommissioning'), 'yellow'),
        (STATUS_RETIRED, _('Retired'), 'red'),
    ]


#
# Racks
#

class RackTypeChoices(ChoiceSet):

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
        (WIDTH_10IN, _('10 inches')),
        (WIDTH_19IN, _('19 inches')),
        (WIDTH_21IN, _('21 inches')),
        (WIDTH_23IN, _('23 inches')),
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
        (RENDER_JSON, _('json')),
        (RENDER_SVG, _('svg'))
    )


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

    AIRFLOW_FRONT_TO_REAR = 'front-to-rear'
    AIRFLOW_REAR_TO_FRONT = 'rear-to-front'
    AIRFLOW_LEFT_TO_RIGHT = 'left-to-right'
    AIRFLOW_RIGHT_TO_LEFT = 'right-to-left'
    AIRFLOW_SIDE_TO_REAR = 'side-to-rear'
    AIRFLOW_PASSIVE = 'passive'
    AIRFLOW_MIXED = 'mixed'

    CHOICES = (
        (AIRFLOW_FRONT_TO_REAR, _('Front to rear')),
        (AIRFLOW_REAR_TO_FRONT, _('Rear to front')),
        (AIRFLOW_LEFT_TO_RIGHT, _('Left to right')),
        (AIRFLOW_RIGHT_TO_LEFT, _('Right to left')),
        (AIRFLOW_SIDE_TO_REAR, _('Side to rear')),
        (AIRFLOW_PASSIVE, _('Passive')),
        (AIRFLOW_MIXED, _('Mixed')),
    )


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
        (_('Serial'), (
            (TYPE_DE9, _('DE-9')),
            (TYPE_DB25, _('DB-25')),
            (TYPE_RJ11, _('RJ-11')),
            (TYPE_RJ12, _('RJ-12')),
            (TYPE_RJ45, _('RJ-45')),
            (TYPE_MINI_DIN_8, _('Mini-DIN 8')),
        )),
        (_('USB'), (
            (TYPE_USB_A, _('USB Type A')),
            (TYPE_USB_B, _('USB Type B')),
            (TYPE_USB_C, _('USB Type C')),
            (TYPE_USB_MINI_A, _('USB Mini A')),
            (TYPE_USB_MINI_B, _('USB Mini B')),
            (TYPE_USB_MICRO_A, _('USB Micro A')),
            (TYPE_USB_MICRO_B, _('USB Micro B')),
            (TYPE_USB_MICRO_AB, _('USB Micro AB')),
        )),
        (_('Other'), (
            (TYPE_OTHER, _('Other')),
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
        (SPEED_1200, _('1200 bps')),
        (SPEED_2400, _('2400 bps')),
        (SPEED_4800, _('4800 bps')),
        (SPEED_9600, _('9600 bps')),
        (SPEED_19200, _('19.2 kbps')),
        (SPEED_38400, _('38.4 kbps')),
        (SPEED_57600, _('57.6 kbps')),
        (SPEED_115200, _('115.2 kbps')),
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
        (_('IEC 60320'), (
            (TYPE_IEC_C6, _('C6')),
            (TYPE_IEC_C8, _('C8')),
            (TYPE_IEC_C14, _('C14')),
            (TYPE_IEC_C16, _('C16')),
            (TYPE_IEC_C20, _('C20')),
            (TYPE_IEC_C22, _('C22')),
        )),
        (_('IEC 60309'), (
            (TYPE_IEC_PNE4H, _('P+N+E 4H')),
            (TYPE_IEC_PNE6H, _('P+N+E 6H')),
            (TYPE_IEC_PNE9H, _('P+N+E 9H')),
            (TYPE_IEC_2PE4H, _('2P+E 4H')),
            (TYPE_IEC_2PE6H, _('2P+E 6H')),
            (TYPE_IEC_2PE9H, _('2P+E 9H')),
            (TYPE_IEC_3PE4H, _('3P+E 4H')),
            (TYPE_IEC_3PE6H, _('3P+E 6H')),
            (TYPE_IEC_3PE9H, _('3P+E 9H')),
            (TYPE_IEC_3PNE4H, _('3P+N+E 4H')),
            (TYPE_IEC_3PNE6H, _('3P+N+E 6H')),
            (TYPE_IEC_3PNE9H, _('3P+N+E 9H')),
        )),
        ('IEC 60906-1', (
            (TYPE_IEC_60906_1, _('IEC 60906-1')),
            (TYPE_NBR_14136_10A, _('2P+T 10A (NBR 14136)')),
            (TYPE_NBR_14136_20A, _('2P+T 20A (NBR 14136)')),
        )),
        (_('NEMA (Non-locking)'), (
            (TYPE_NEMA_115P, _('NEMA 1-15P')),
            (TYPE_NEMA_515P, _('NEMA 5-15P')),
            (TYPE_NEMA_520P, _('NEMA 5-20P')),
            (TYPE_NEMA_530P, _('NEMA 5-30P')),
            (TYPE_NEMA_550P, _('NEMA 5-50P')),
            (TYPE_NEMA_615P, _('NEMA 6-15P')),
            (TYPE_NEMA_620P, _('NEMA 6-20P')),
            (TYPE_NEMA_630P, _('NEMA 6-30P')),
            (TYPE_NEMA_650P, _('NEMA 6-50P')),
            (TYPE_NEMA_1030P, _('NEMA 10-30P')),
            (TYPE_NEMA_1050P, _('NEMA 10-50P')),
            (TYPE_NEMA_1420P, _('NEMA 14-20P')),
            (TYPE_NEMA_1430P, _('NEMA 14-30P')),
            (TYPE_NEMA_1450P, _('NEMA 14-50P')),
            (TYPE_NEMA_1460P, _('NEMA 14-60P')),
            (TYPE_NEMA_1515P, _('NEMA 15-15P')),
            (TYPE_NEMA_1520P, _('NEMA 15-20P')),
            (TYPE_NEMA_1530P, _('NEMA 15-30P')),
            (TYPE_NEMA_1550P, _('NEMA 15-50P')),
            (TYPE_NEMA_1560P, _('NEMA 15-60P')),
        )),
        (_('NEMA (Locking)'), (
            (TYPE_NEMA_L115P, _('NEMA L1-15P')),
            (TYPE_NEMA_L515P, _('NEMA L5-15P')),
            (TYPE_NEMA_L520P, _('NEMA L5-20P')),
            (TYPE_NEMA_L530P, _('NEMA L5-30P')),
            (TYPE_NEMA_L550P, _('NEMA L5-50P')),
            (TYPE_NEMA_L615P, _('NEMA L6-15P')),
            (TYPE_NEMA_L620P, _('NEMA L6-20P')),
            (TYPE_NEMA_L630P, _('NEMA L6-30P')),
            (TYPE_NEMA_L650P, _('NEMA L6-50P')),
            (TYPE_NEMA_L1030P, _('NEMA L10-30P')),
            (TYPE_NEMA_L1420P, _('NEMA L14-20P')),
            (TYPE_NEMA_L1430P, _('NEMA L14-30P')),
            (TYPE_NEMA_L1450P, _('NEMA L14-50P')),
            (TYPE_NEMA_L1460P, _('NEMA L14-60P')),
            (TYPE_NEMA_L1520P, _('NEMA L15-20P')),
            (TYPE_NEMA_L1530P, _('NEMA L15-30P')),
            (TYPE_NEMA_L1550P, _('NEMA L15-50P')),
            (TYPE_NEMA_L1560P, _('NEMA L15-60P')),
            (TYPE_NEMA_L2120P, _('NEMA L21-20P')),
            (TYPE_NEMA_L2130P, _('NEMA L21-30P')),
            (TYPE_NEMA_L2230P, _('NEMA L22-30P')),
        )),
        (_('California Style'), (
            (TYPE_CS6361C, _('CS6361C')),
            (TYPE_CS6365C, _('CS6365C')),
            (TYPE_CS8165C, _('CS8165C')),
            (TYPE_CS8265C, _('CS8265C')),
            (TYPE_CS8365C, _('CS8365C')),
            (TYPE_CS8465C, _('CS8465C')),
        )),
        (_('International/ITA'), (
            (TYPE_ITA_C, _('ITA Type C (CEE 7/16)')),
            (TYPE_ITA_E, _('ITA Type E (CEE 7/6)')),
            (TYPE_ITA_F, _('ITA Type F (CEE 7/4)')),
            (TYPE_ITA_EF, _('ITA Type E/F (CEE 7/7)')),
            (TYPE_ITA_G, _('ITA Type G (BS 1363)')),
            (TYPE_ITA_H, _('ITA Type H')),
            (TYPE_ITA_I, _('ITA Type I')),
            (TYPE_ITA_J, _('ITA Type J')),
            (TYPE_ITA_K, _('ITA Type K')),
            (TYPE_ITA_L, _('ITA Type L (CEI 23-50)')),
            (TYPE_ITA_M, _('ITA Type M (BS 546)')),
            (TYPE_ITA_N, _('ITA Type N')),
            (TYPE_ITA_O, _('ITA Type O')),
        )),
        (_('USB'), (
            (TYPE_USB_A, _('USB Type A')),
            (TYPE_USB_B, _('USB Type B')),
            (TYPE_USB_C, _('USB Type C')),
            (TYPE_USB_MINI_A, _('USB Mini A')),
            (TYPE_USB_MINI_B, _('USB Mini B')),
            (TYPE_USB_MICRO_A, _('USB Micro A')),
            (TYPE_USB_MICRO_B, _('USB Micro B')),
            (TYPE_USB_MICRO_AB, _('USB Micro AB')),
            (TYPE_USB_3_B, _('USB 3.0 Type B')),
            (TYPE_USB_3_MICROB, _('USB 3.0 Micro B')),
        )),
        (_('DC'), (
            (TYPE_DC, _('DC Terminal')),
        )),
        (_('Proprietary'), (
            (TYPE_SAF_D_GRID, _('Saf-D-Grid')),
            (TYPE_NEUTRIK_POWERCON_20A, _('Neutrik powerCON (20A)')),
            (TYPE_NEUTRIK_POWERCON_32A, _('Neutrik powerCON (32A)')),
            (TYPE_NEUTRIK_POWERCON_TRUE1, _('Neutrik powerCON TRUE1')),
            (TYPE_NEUTRIK_POWERCON_TRUE1_TOP, _('Neutrik powerCON TRUE1 TOP')),
            (TYPE_UBIQUITI_SMARTPOWER, _('Ubiquiti SmartPower')),
        )),
        (_('Other'), (
            (TYPE_HARDWIRED, _('Hardwired')),
            (TYPE_OTHER, _('Other')),
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
    # Direct current (DC)
    TYPE_DC = 'dc-terminal'
    # Proprietary
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
        (_('IEC 60320'), (
            (TYPE_IEC_C5, _('C5')),
            (TYPE_IEC_C7, _('C7')),
            (TYPE_IEC_C13, _('C13')),
            (TYPE_IEC_C15, _('C15')),
            (TYPE_IEC_C19, _('C19')),
            (TYPE_IEC_C21, _('C21')),
        )),
        (_('IEC 60309'), (
            (TYPE_IEC_PNE4H, _('P+N+E 4H')),
            (TYPE_IEC_PNE6H, _('P+N+E 6H')),
            (TYPE_IEC_PNE9H, _('P+N+E 9H')),
            (TYPE_IEC_2PE4H, _('2P+E 4H')),
            (TYPE_IEC_2PE6H, _('2P+E 6H')),
            (TYPE_IEC_2PE9H, _('2P+E 9H')),
            (TYPE_IEC_3PE4H, _('3P+E 4H')),
            (TYPE_IEC_3PE6H, _('3P+E 6H')),
            (TYPE_IEC_3PE9H, _('3P+E 9H')),
            (TYPE_IEC_3PNE4H, _('3P+N+E 4H')),
            (TYPE_IEC_3PNE6H, _('3P+N+E 6H')),
            (TYPE_IEC_3PNE9H, _('3P+N+E 9H')),
        )),
        ('IEC 60906-1', (
            (TYPE_IEC_60906_1, _('IEC 60906-1')),
            (TYPE_NBR_14136_10A, _('2P+T 10A (NBR 14136)')),
            (TYPE_NBR_14136_20A, _('2P+T 20A (NBR 14136)')),
        )),
        (_('NEMA (Non-locking)'), (
            (TYPE_NEMA_115R, _('NEMA 1-15R')),
            (TYPE_NEMA_515R, _('NEMA 5-15R')),
            (TYPE_NEMA_520R, _('NEMA 5-20R')),
            (TYPE_NEMA_530R, _('NEMA 5-30R')),
            (TYPE_NEMA_550R, _('NEMA 5-50R')),
            (TYPE_NEMA_615R, _('NEMA 6-15R')),
            (TYPE_NEMA_620R, _('NEMA 6-20R')),
            (TYPE_NEMA_630R, _('NEMA 6-30R')),
            (TYPE_NEMA_650R, _('NEMA 6-50R')),
            (TYPE_NEMA_1030R, _('NEMA 10-30R')),
            (TYPE_NEMA_1050R, _('NEMA 10-50R')),
            (TYPE_NEMA_1420R, _('NEMA 14-20R')),
            (TYPE_NEMA_1430R, _('NEMA 14-30R')),
            (TYPE_NEMA_1450R, _('NEMA 14-50R')),
            (TYPE_NEMA_1460R, _('NEMA 14-60R')),
            (TYPE_NEMA_1515R, _('NEMA 15-15R')),
            (TYPE_NEMA_1520R, _('NEMA 15-20R')),
            (TYPE_NEMA_1530R, _('NEMA 15-30R')),
            (TYPE_NEMA_1550R, _('NEMA 15-50R')),
            (TYPE_NEMA_1560R, _('NEMA 15-60R')),
        )),
        (_('NEMA (Locking)'), (
            (TYPE_NEMA_L115R, _('NEMA L1-15R')),
            (TYPE_NEMA_L515R, _('NEMA L5-15R')),
            (TYPE_NEMA_L520R, _('NEMA L5-20R')),
            (TYPE_NEMA_L530R, _('NEMA L5-30R')),
            (TYPE_NEMA_L550R, _('NEMA L5-50R')),
            (TYPE_NEMA_L615R, _('NEMA L6-15R')),
            (TYPE_NEMA_L620R, _('NEMA L6-20R')),
            (TYPE_NEMA_L630R, _('NEMA L6-30R')),
            (TYPE_NEMA_L650R, _('NEMA L6-50R')),
            (TYPE_NEMA_L1030R, _('NEMA L10-30R')),
            (TYPE_NEMA_L1420R, _('NEMA L14-20R')),
            (TYPE_NEMA_L1430R, _('NEMA L14-30R')),
            (TYPE_NEMA_L1450R, _('NEMA L14-50R')),
            (TYPE_NEMA_L1460R, _('NEMA L14-60R')),
            (TYPE_NEMA_L1520R, _('NEMA L15-20R')),
            (TYPE_NEMA_L1530R, _('NEMA L15-30R')),
            (TYPE_NEMA_L1550R, _('NEMA L15-50R')),
            (TYPE_NEMA_L1560R, _('NEMA L15-60R')),
            (TYPE_NEMA_L2120R, _('NEMA L21-20R')),
            (TYPE_NEMA_L2130R, _('NEMA L21-30R')),
            (TYPE_NEMA_L2230R, _('NEMA L22-30R')),
        )),
        (_('California Style'), (
            (TYPE_CS6360C, _('CS6360C')),
            (TYPE_CS6364C, _('CS6364C')),
            (TYPE_CS8164C, _('CS8164C')),
            (TYPE_CS8264C, _('CS8264C')),
            (TYPE_CS8364C, _('CS8364C')),
            (TYPE_CS8464C, _('CS8464C')),
        )),
        (_('ITA/International'), (
            (TYPE_ITA_E, _('ITA Type E (CEE 7/5)')),
            (TYPE_ITA_F, _('ITA Type F (CEE 7/3)')),
            (TYPE_ITA_G, _('ITA Type G (BS 1363)')),
            (TYPE_ITA_H, _('ITA Type H')),
            (TYPE_ITA_I, _('ITA Type I')),
            (TYPE_ITA_J, _('ITA Type J')),
            (TYPE_ITA_K, _('ITA Type K')),
            (TYPE_ITA_L, _('ITA Type L (CEI 23-50)')),
            (TYPE_ITA_M, _('ITA Type M (BS 546)')),
            (TYPE_ITA_N, _('ITA Type N')),
            (TYPE_ITA_O, _('ITA Type O')),
            (TYPE_ITA_MULTISTANDARD, _('ITA Multistandard')),
        )),
        (_('USB'), (
            (TYPE_USB_A, _('USB Type A')),
            (TYPE_USB_MICROB, _('USB Micro B')),
            (TYPE_USB_C, _('USB Type C')),
        )),
        (_('DC'), (
            (TYPE_DC, _('DC Terminal')),
        )),
        (_('Proprietary'), (
            (TYPE_HDOT_CX, _('HDOT Cx')),
            (TYPE_SAF_D_GRID, _('Saf-D-Grid')),
            (TYPE_NEUTRIK_POWERCON_20A, _('Neutrik powerCON (20A)')),
            (TYPE_NEUTRIK_POWERCON_32A, _('Neutrik powerCON (32A)')),
            (TYPE_NEUTRIK_POWERCON_TRUE1, _('Neutrik powerCON TRUE1')),
            (TYPE_NEUTRIK_POWERCON_TRUE1_TOP, _('Neutrik powerCON TRUE1 TOP')),
            (TYPE_UBIQUITI_SMARTPOWER, _('Ubiquiti SmartPower')),
        )),
        (_('Other'), (
            (TYPE_HARDWIRED, _('Hardwired')),
            (TYPE_OTHER, _('Other')),
        )),
    )


class PowerOutletFeedLegChoices(ChoiceSet):

    FEED_LEG_A = 'A'
    FEED_LEG_B = 'B'
    FEED_LEG_C = 'C'

    CHOICES = (
        (FEED_LEG_A, _('A')),
        (FEED_LEG_B, _('B')),
        (FEED_LEG_C, _('C')),
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

    # Ethernet
    TYPE_100ME_FX = '100base-fx'
    TYPE_100ME_LFX = '100base-lfx'
    TYPE_100ME_FIXED = '100base-tx'
    TYPE_100ME_T1 = '100base-t1'
    TYPE_1GE_FIXED = '1000base-t'
    TYPE_1GE_GBIC = '1000base-x-gbic'
    TYPE_1GE_SFP = '1000base-x-sfp'
    TYPE_2GE_FIXED = '2.5gbase-t'
    TYPE_5GE_FIXED = '5gbase-t'
    TYPE_10GE_FIXED = '10gbase-t'
    TYPE_10GE_CX4 = '10gbase-cx4'
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
    TYPE_400GE_QSFP_DD = '400gbase-x-qsfpdd'
    TYPE_400GE_OSFP = '400gbase-x-osfp'
    TYPE_400GE_CDFP = '400gbase-x-cdfp'
    TYPE_400GE_CFP8 = '400gbase-x-cfp8'
    TYPE_800GE_QSFP_DD = '800gbase-x-qsfpdd'
    TYPE_800GE_OSFP = '800gbase-x-osfp'

    # Ethernet Backplane
    TYPE_1GE_KX = '1000base-kx'
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
    TYPE_802151 = 'ieee802.15.1'
    TYPE_OTHER_WIRELESS = 'other-wireless'

    # Cellular
    TYPE_GSM = 'gsm'
    TYPE_CDMA = 'cdma'
    TYPE_LTE = 'lte'

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
    TYPE_64GFC_QSFP_PLUS = '64gfc-qsfpp'
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

    # PON
    TYPE_GPON = 'gpon'
    TYPE_XG_PON = 'xg-pon'
    TYPE_XGS_PON = 'xgs-pon'
    TYPE_NG_PON2 = 'ng-pon2'
    TYPE_EPON = 'epon'
    TYPE_10G_EPON = '10g-epon'

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
            _('Ethernet (fixed)'),
            (
                (TYPE_100ME_FX, _('100BASE-FX (10/100ME FIBER)')),
                (TYPE_100ME_LFX, _('100BASE-LFX (10/100ME FIBER)')),
                (TYPE_100ME_FIXED, _('100BASE-TX (10/100ME)')),
                (TYPE_100ME_T1, _('100BASE-T1 (10/100ME Single Pair)')),
                (TYPE_1GE_FIXED, _('1000BASE-T (1GE)')),
                (TYPE_2GE_FIXED, _('2.5GBASE-T (2.5GE)')),
                (TYPE_5GE_FIXED, _('5GBASE-T (5GE)')),
                (TYPE_10GE_FIXED, _('10GBASE-T (10GE)')),
                (TYPE_10GE_CX4, _('10GBASE-CX4 (10GE)')),
            )
        ),
        (
            _('Ethernet (modular)'),
            (
                (TYPE_1GE_GBIC, _('GBIC (1GE)')),
                (TYPE_1GE_SFP, _('SFP (1GE)')),
                (TYPE_10GE_SFP_PLUS, _('SFP+ (10GE)')),
                (TYPE_10GE_XFP, _('XFP (10GE)')),
                (TYPE_10GE_XENPAK, _('XENPAK (10GE)')),
                (TYPE_10GE_X2, _('X2 (10GE)')),
                (TYPE_25GE_SFP28, _('SFP28 (25GE)')),
                (TYPE_50GE_SFP56, _('SFP56 (50GE)')),
                (TYPE_40GE_QSFP_PLUS, _('QSFP+ (40GE)')),
                (TYPE_50GE_QSFP28, _('QSFP28 (50GE)')),
                (TYPE_100GE_CFP, _('CFP (100GE)')),
                (TYPE_100GE_CFP2, _('CFP2 (100GE)')),
                (TYPE_200GE_CFP2, _('CFP2 (200GE)')),
                (TYPE_100GE_CFP4, _('CFP4 (100GE)')),
                (TYPE_100GE_CXP, _('CXP (100GE)')),
                (TYPE_100GE_CPAK, _('Cisco CPAK (100GE)')),
                (TYPE_100GE_DSFP, _('DSFP (100GE)')),
                (TYPE_100GE_SFP_DD, _('SFP-DD (100GE)')),
                (TYPE_100GE_QSFP28, _('QSFP28 (100GE)')),
                (TYPE_100GE_QSFP_DD, _('QSFP-DD (100GE)')),
                (TYPE_200GE_QSFP56, _('QSFP56 (200GE)')),
                (TYPE_200GE_QSFP_DD, _('QSFP-DD (200GE)')),
                (TYPE_400GE_QSFP_DD, _('QSFP-DD (400GE)')),
                (TYPE_400GE_OSFP, _('OSFP (400GE)')),
                (TYPE_400GE_CDFP, _('CDFP (400GE)')),
                (TYPE_400GE_CFP8, _('CPF8 (400GE)')),
                (TYPE_800GE_QSFP_DD, _('QSFP-DD (800GE)')),
                (TYPE_800GE_OSFP, _('OSFP (800GE)')),
            )
        ),
        (
            _('Ethernet (backplane)'),
            (
                (TYPE_1GE_KX, _('1000BASE-KX (1GE)')),
                (TYPE_10GE_KR, _('10GBASE-KR (10GE)')),
                (TYPE_10GE_KX4, _('10GBASE-KX4 (10GE)')),
                (TYPE_25GE_KR, _('25GBASE-KR (25GE)')),
                (TYPE_40GE_KR4, _('40GBASE-KR4 (40GE)')),
                (TYPE_50GE_KR, _('50GBASE-KR (50GE)')),
                (TYPE_100GE_KP4, _('100GBASE-KP4 (100GE)')),
                (TYPE_100GE_KR2, _('100GBASE-KR2 (100GE)')),
                (TYPE_100GE_KR4, _('100GBASE-KR4 (100GE)')),
            )
        ),
        (
            _('Wireless'),
            (
                (TYPE_80211A, _('IEEE 802.11a')),
                (TYPE_80211G, _('IEEE 802.11b/g')),
                (TYPE_80211N, _('IEEE 802.11n')),
                (TYPE_80211AC, _('IEEE 802.11ac')),
                (TYPE_80211AD, _('IEEE 802.11ad')),
                (TYPE_80211AX, _('IEEE 802.11ax')),
                (TYPE_80211AY, _('IEEE 802.11ay')),
                (TYPE_802151, _('IEEE 802.15.1 (Bluetooth)')),
                (TYPE_OTHER_WIRELESS, _('Other (Wireless)')),
            )
        ),
        (
            _('Cellular'),
            (
                (TYPE_GSM, _('GSM')),
                (TYPE_CDMA, _('CDMA')),
                (TYPE_LTE, _('LTE')),
            )
        ),
        (
            _('SONET'),
            (
                (TYPE_SONET_OC3, _('OC-3/STM-1')),
                (TYPE_SONET_OC12, _('OC-12/STM-4')),
                (TYPE_SONET_OC48, _('OC-48/STM-16')),
                (TYPE_SONET_OC192, _('OC-192/STM-64')),
                (TYPE_SONET_OC768, _('OC-768/STM-256')),
                (TYPE_SONET_OC1920, _('OC-1920/STM-640')),
                (TYPE_SONET_OC3840, _('OC-3840/STM-1234')),
            )
        ),
        (
            _('FibreChannel'),
            (
                (TYPE_1GFC_SFP, _('SFP (1GFC)')),
                (TYPE_2GFC_SFP, _('SFP (2GFC)')),
                (TYPE_4GFC_SFP, _('SFP (4GFC)')),
                (TYPE_8GFC_SFP_PLUS, _('SFP+ (8GFC)')),
                (TYPE_16GFC_SFP_PLUS, _('SFP+ (16GFC)')),
                (TYPE_32GFC_SFP28, _('SFP28 (32GFC)')),
                (TYPE_64GFC_QSFP_PLUS, _('QSFP+ (64GFC)')),
                (TYPE_128GFC_QSFP28, _('QSFP28 (128GFC)')),
            )
        ),
        (
            _('InfiniBand'),
            (
                (TYPE_INFINIBAND_SDR, _('SDR (2 Gbps)')),
                (TYPE_INFINIBAND_DDR, _('DDR (4 Gbps)')),
                (TYPE_INFINIBAND_QDR, _('QDR (8 Gbps)')),
                (TYPE_INFINIBAND_FDR10, _('FDR10 (10 Gbps)')),
                (TYPE_INFINIBAND_FDR, _('FDR (13.5 Gbps)')),
                (TYPE_INFINIBAND_EDR, _('EDR (25 Gbps)')),
                (TYPE_INFINIBAND_HDR, _('HDR (50 Gbps)')),
                (TYPE_INFINIBAND_NDR, _('NDR (100 Gbps)')),
                (TYPE_INFINIBAND_XDR, _('XDR (250 Gbps)')),
            )
        ),
        (
            _('Serial'),
            (
                (TYPE_T1, _('T1 (1.544 Mbps)')),
                (TYPE_E1, _('E1 (2.048 Mbps)')),
                (TYPE_T3, _('T3 (45 Mbps)')),
                (TYPE_E3, _('E3 (34 Mbps)')),
            )
        ),
        (
            _('ATM'),
            (
                (TYPE_XDSL, _('xDSL')),
            )
        ),
        (
            _('Coaxial'),
            (
                (TYPE_DOCSIS, _('DOCSIS')),
            )
        ),
        (
            _('PON'),
            (
                (TYPE_GPON, _('GPON (2.5 Gbps / 1.25 Gps)')),
                (TYPE_XG_PON, _('XG-PON (10 Gbps / 2.5 Gbps)')),
                (TYPE_XGS_PON, _('XGS-PON (10 Gbps)')),
                (TYPE_NG_PON2, _('NG-PON2 (TWDM-PON) (4x10 Gbps)')),
                (TYPE_EPON, _('EPON (1 Gbps)')),
                (TYPE_10G_EPON, _('10G-EPON (10 Gbps)')),
            )
        ),
        (
            _('Stacking'),
            (
                (TYPE_STACKWISE, _('Cisco StackWise')),
                (TYPE_STACKWISE_PLUS, _('Cisco StackWise Plus')),
                (TYPE_FLEXSTACK, _('Cisco FlexStack')),
                (TYPE_FLEXSTACK_PLUS, _('Cisco FlexStack Plus')),
                (TYPE_STACKWISE80, _('Cisco StackWise-80')),
                (TYPE_STACKWISE160, _('Cisco StackWise-160')),
                (TYPE_STACKWISE320, _('Cisco StackWise-320')),
                (TYPE_STACKWISE480, _('Cisco StackWise-480')),
                (TYPE_STACKWISE1T, _('Cisco StackWise-1T')),
                (TYPE_JUNIPER_VCP, _('Juniper VCP')),
                (TYPE_SUMMITSTACK, _('Extreme SummitStack')),
                (TYPE_SUMMITSTACK128, _('Extreme SummitStack-128')),
                (TYPE_SUMMITSTACK256, _('Extreme SummitStack-256')),
                (TYPE_SUMMITSTACK512, _('Extreme SummitStack-512')),
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
        (10000, _('10 Mbps')),
        (100000, _('100 Mbps')),
        (1000000, _('1 Gbps')),
        (10000000, _('10 Gbps')),
        (25000000, _('25 Gbps')),
        (40000000, _('40 Gbps')),
        (100000000, _('100 Gbps')),
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

    CHOICES = (
        (MODE_ACCESS, _('Access')),
        (MODE_TAGGED, _('Tagged')),
        (MODE_TAGGED_ALL, _('Tagged (All)')),
    )


class InterfacePoEModeChoices(ChoiceSet):

    MODE_PD = 'pd'
    MODE_PSE = 'pse'

    CHOICES = (
        (MODE_PD, _('PD')),
        (MODE_PSE, _('PSE')),
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
                (TYPE_1_8023AF, _('802.3af (Type 1)')),
                (TYPE_2_8023AT, _('802.3at (Type 2)')),
                (TYPE_3_8023BT, _('802.3bt (Type 3)')),
                (TYPE_4_8023BT, _('802.3bt (Type 4)')),
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
    TYPE_OTHER = 'other'

    CHOICES = (
        (
            _('Copper'),
            (
                (TYPE_8P8C, _('8P8C')),
                (TYPE_8P6C, _('8P6C')),
                (TYPE_8P4C, _('8P4C')),
                (TYPE_8P2C, _('8P2C')),
                (TYPE_6P6C, _('6P6C')),
                (TYPE_6P4C, _('6P4C')),
                (TYPE_6P2C, _('6P2C')),
                (TYPE_4P4C, _('4P4C')),
                (TYPE_4P2C, _('4P2C')),
                (TYPE_GG45, _('GG45')),
                (TYPE_TERA4P, _('TERA 4P')),
                (TYPE_TERA2P, _('TERA 2P')),
                (TYPE_TERA1P, _('TERA 1P')),
                (TYPE_110_PUNCH, _('110 Punch')),
                (TYPE_BNC, _('BNC')),
                (TYPE_F, _('F Connector')),
                (TYPE_N, _('N Connector')),
                (TYPE_MRJ21, _('MRJ21')),
            ),
        ),
        (
            _('Fiber Optic'),
            (
                (TYPE_FC, _('FC')),
                (TYPE_LC, _('LC')),
                (TYPE_LC_PC, _('LC/PC')),
                (TYPE_LC_UPC, _('LC/UPC')),
                (TYPE_LC_APC, _('LC/APC')),
                (TYPE_LSH, _('LSH')),
                (TYPE_LSH_PC, _('LSH/PC')),
                (TYPE_LSH_UPC, _('LSH/UPC')),
                (TYPE_LSH_APC, _('LSH/APC')),
                (TYPE_LX5, _('LX.5')),
                (TYPE_LX5_PC, _('LX.5/PC')),
                (TYPE_LX5_UPC, _('LX.5/UPC')),
                (TYPE_LX5_APC, _('LX.5/APC')),
                (TYPE_MPO, _('MPO')),
                (TYPE_MTRJ, _('MTRJ')),
                (TYPE_SC, _('SC')),
                (TYPE_SC_PC, _('SC/PC')),
                (TYPE_SC_UPC, _('SC/UPC')),
                (TYPE_SC_APC, _('SC/APC')),
                (TYPE_ST, _('ST')),
                (TYPE_CS, _('CS')),
                (TYPE_SN, _('SN')),
                (TYPE_SMA_905, _('SMA 905')),
                (TYPE_SMA_906, _('SMA 906')),
                (TYPE_URM_P2, _('URM-P2')),
                (TYPE_URM_P4, _('URM-P4')),
                (TYPE_URM_P8, _('URM-P8')),
                (TYPE_SPLICE, _('Splice')),
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

    TYPE_CAT3 = 'cat3'
    TYPE_CAT5 = 'cat5'
    TYPE_CAT5E = 'cat5e'
    TYPE_CAT6 = 'cat6'
    TYPE_CAT6A = 'cat6a'
    TYPE_CAT7 = 'cat7'
    TYPE_CAT7A = 'cat7a'
    TYPE_CAT8 = 'cat8'
    TYPE_DAC_ACTIVE = 'dac-active'
    TYPE_DAC_PASSIVE = 'dac-passive'
    TYPE_MRJ21_TRUNK = 'mrj21-trunk'
    TYPE_COAXIAL = 'coaxial'
    TYPE_MMF = 'mmf'
    TYPE_MMF_OM1 = 'mmf-om1'
    TYPE_MMF_OM2 = 'mmf-om2'
    TYPE_MMF_OM3 = 'mmf-om3'
    TYPE_MMF_OM4 = 'mmf-om4'
    TYPE_MMF_OM5 = 'mmf-om5'
    TYPE_SMF = 'smf'
    TYPE_SMF_OS1 = 'smf-os1'
    TYPE_SMF_OS2 = 'smf-os2'
    TYPE_AOC = 'aoc'
    TYPE_POWER = 'power'

    CHOICES = (
        (
            _('Copper'), (
                (TYPE_CAT3, _('CAT3')),
                (TYPE_CAT5, _('CAT5')),
                (TYPE_CAT5E, _('CAT5e')),
                (TYPE_CAT6, _('CAT6')),
                (TYPE_CAT6A, _('CAT6a')),
                (TYPE_CAT7, _('CAT7')),
                (TYPE_CAT7A, _('CAT7a')),
                (TYPE_CAT8, _('CAT8')),
                (TYPE_DAC_ACTIVE, _('Direct Attach Copper (Active)')),
                (TYPE_DAC_PASSIVE, _('Direct Attach Copper (Passive)')),
                (TYPE_MRJ21_TRUNK, _('MRJ21 Trunk')),
                (TYPE_COAXIAL, _('Coaxial')),
            ),
        ),
        (
            _('Fiber'), (
                (TYPE_MMF, _('Multimode Fiber')),
                (TYPE_MMF_OM1, _('Multimode Fiber (OM1)')),
                (TYPE_MMF_OM2, _('Multimode Fiber (OM2)')),
                (TYPE_MMF_OM3, _('Multimode Fiber (OM3)')),
                (TYPE_MMF_OM4, _('Multimode Fiber (OM4)')),
                (TYPE_MMF_OM5, _('Multimode Fiber (OM5)')),
                (TYPE_SMF, _('Singlemode Fiber')),
                (TYPE_SMF_OS1, _('Singlemode Fiber (OS1)')),
                (TYPE_SMF_OS2, _('Singlemode Fiber (OS2)')),
                (TYPE_AOC, _('Active Optical Cabling (AOC)')),
            ),
        ),
        (TYPE_POWER, _('Power')),
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


class WeightUnitChoices(ChoiceSet):

    # Metric
    UNIT_KILOGRAM = 'kg'
    UNIT_GRAM = 'g'

    # Imperial
    UNIT_POUND = 'lb'
    UNIT_OUNCE = 'oz'

    CHOICES = (
        (UNIT_KILOGRAM, _('Kilograms')),
        (UNIT_GRAM, _('Grams')),
        (UNIT_POUND, _('Pounds')),
        (UNIT_OUNCE, _('Ounces')),
    )


#
# CableTerminations
#

class CableEndChoices(ChoiceSet):

    SIDE_A = 'A'
    SIDE_B = 'B'

    CHOICES = (
        (SIDE_A, _('A')),
        (SIDE_B, _('B')),
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
        (SUPPLY_AC, _('AC')),
        (SUPPLY_DC, _('DC')),
    )


class PowerFeedPhaseChoices(ChoiceSet):

    PHASE_SINGLE = 'single-phase'
    PHASE_3PHASE = 'three-phase'

    CHOICES = (
        (PHASE_SINGLE, _('Single phase')),
        (PHASE_3PHASE, _('Three-phase')),
    )


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
