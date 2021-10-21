from utilities.choices import ChoiceSet


#
# Sites
#

class SiteStatusChoices(ChoiceSet):

    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_RETIRED = 'retired'

    CHOICES = (
        (STATUS_PLANNED, 'Planned'),
        (STATUS_STAGING, 'Staging'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DECOMMISSIONING, 'Decommissioning'),
        (STATUS_RETIRED, 'Retired'),
    )

    CSS_CLASSES = {
        STATUS_PLANNED: 'info',
        STATUS_STAGING: 'primary',
        STATUS_ACTIVE: 'success',
        STATUS_DECOMMISSIONING: 'warning',
        STATUS_RETIRED: 'danger',
    }


#
# Racks
#

class RackTypeChoices(ChoiceSet):

    TYPE_2POST = '2-post-frame'
    TYPE_4POST = '4-post-frame'
    TYPE_CABINET = '4-post-cabinet'
    TYPE_WALLFRAME = 'wall-frame'
    TYPE_WALLCABINET = 'wall-cabinet'

    CHOICES = (
        (TYPE_2POST, '2-post frame'),
        (TYPE_4POST, '4-post frame'),
        (TYPE_CABINET, '4-post cabinet'),
        (TYPE_WALLFRAME, 'Wall-mounted frame'),
        (TYPE_WALLCABINET, 'Wall-mounted cabinet'),
    )


class RackWidthChoices(ChoiceSet):

    WIDTH_10IN = 10
    WIDTH_19IN = 19
    WIDTH_21IN = 21
    WIDTH_23IN = 23

    CHOICES = (
        (WIDTH_10IN, '10 inches'),
        (WIDTH_19IN, '19 inches'),
        (WIDTH_21IN, '21 inches'),
        (WIDTH_23IN, '23 inches'),
    )


class RackStatusChoices(ChoiceSet):

    STATUS_RESERVED = 'reserved'
    STATUS_AVAILABLE = 'available'
    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DEPRECATED = 'deprecated'

    CHOICES = (
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DEPRECATED, 'Deprecated'),
    )

    CSS_CLASSES = {
        STATUS_RESERVED: 'warning',
        STATUS_AVAILABLE: 'success',
        STATUS_PLANNED: 'info',
        STATUS_ACTIVE: 'primary',
        STATUS_DEPRECATED: 'danger',
    }


class RackDimensionUnitChoices(ChoiceSet):

    UNIT_MILLIMETER = 'mm'
    UNIT_INCH = 'in'

    CHOICES = (
        (UNIT_MILLIMETER, 'Millimeters'),
        (UNIT_INCH, 'Inches'),
    )


class RackElevationDetailRenderChoices(ChoiceSet):

    RENDER_JSON = 'json'
    RENDER_SVG = 'svg'

    CHOICES = (
        (RENDER_JSON, 'json'),
        (RENDER_SVG, 'svg')
    )


#
# DeviceTypes
#

class SubdeviceRoleChoices(ChoiceSet):

    ROLE_PARENT = 'parent'
    ROLE_CHILD = 'child'

    CHOICES = (
        (ROLE_PARENT, 'Parent'),
        (ROLE_CHILD, 'Child'),
    )


#
# Devices
#

class DeviceFaceChoices(ChoiceSet):

    FACE_FRONT = 'front'
    FACE_REAR = 'rear'

    CHOICES = (
        (FACE_FRONT, 'Front'),
        (FACE_REAR, 'Rear'),
    )


class DeviceStatusChoices(ChoiceSet):

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_INVENTORY = 'inventory'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = (
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_STAGED, 'Staged'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_INVENTORY, 'Inventory'),
        (STATUS_DECOMMISSIONING, 'Decommissioning'),
    )

    CSS_CLASSES = {
        STATUS_OFFLINE: 'warning',
        STATUS_ACTIVE: 'success',
        STATUS_PLANNED: 'info',
        STATUS_STAGED: 'primary',
        STATUS_FAILED: 'danger',
        STATUS_INVENTORY: 'secondary',
        STATUS_DECOMMISSIONING: 'warning',
    }


class DeviceAirflowChoices(ChoiceSet):

    AIRFLOW_FRONT_TO_REAR = 'front-to-rear'
    AIRFLOW_REAR_TO_FRONT = 'rear-to-front'
    AIRFLOW_LEFT_TO_RIGHT = 'left-to-right'
    AIRFLOW_RIGHT_TO_LEFT = 'right-to-left'
    AIRFLOW_SIDE_TO_REAR = 'side-to-rear'
    AIRFLOW_PASSIVE = 'passive'

    CHOICES = (
        (AIRFLOW_FRONT_TO_REAR, 'Front to rear'),
        (AIRFLOW_REAR_TO_FRONT, 'Rear to front'),
        (AIRFLOW_LEFT_TO_RIGHT, 'Left to right'),
        (AIRFLOW_RIGHT_TO_LEFT, 'Right to left'),
        (AIRFLOW_SIDE_TO_REAR, 'Side to rear'),
        (AIRFLOW_PASSIVE, 'Passive'),
    )


#
# ConsolePorts
#

class ConsolePortTypeChoices(ChoiceSet):

    TYPE_DE9 = 'de-9'
    TYPE_DB25 = 'db-25'
    TYPE_RJ11 = 'rj-11'
    TYPE_RJ12 = 'rj-12'
    TYPE_RJ45 = 'rj-45'
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
    # Other
    TYPE_HARDWIRED = 'hardwired'

    CHOICES = (
        ('IEC 60320', (
            (TYPE_IEC_C6, 'C6'),
            (TYPE_IEC_C8, 'C8'),
            (TYPE_IEC_C14, 'C14'),
            (TYPE_IEC_C16, 'C16'),
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
        ('NEMA (Non-locking)', (
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
        ('NEMA (Locking)', (
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
        )),
        ('California Style', (
            (TYPE_CS6361C, 'CS6361C'),
            (TYPE_CS6365C, 'CS6365C'),
            (TYPE_CS8165C, 'CS8165C'),
            (TYPE_CS8265C, 'CS8265C'),
            (TYPE_CS8365C, 'CS8365C'),
            (TYPE_CS8465C, 'CS8465C'),
        )),
        ('International/ITA', (
            (TYPE_ITA_C, 'ITA Type C (CEE 7/16)'),
            (TYPE_ITA_E, 'ITA Type E (CEE 7/5)'),
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
        ('DC', (
            (TYPE_DC, 'DC Terminal'),
        )),
        ('Proprietary', (
            (TYPE_SAF_D_GRID, 'Saf-D-Grid'),
        )),
        ('Other', (
            (TYPE_HARDWIRED, 'Hardwired'),
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
    # USB
    TYPE_USB_A = 'usb-a'
    TYPE_USB_MICROB = 'usb-micro-b'
    TYPE_USB_C = 'usb-c'
    # Direct current (DC)
    TYPE_DC = 'dc-terminal'
    # Proprietary
    TYPE_HDOT_CX = 'hdot-cx'
    TYPE_SAF_D_GRID = 'saf-d-grid'
    # Other
    TYPE_HARDWIRED = 'hardwired'

    CHOICES = (
        ('IEC 60320', (
            (TYPE_IEC_C5, 'C5'),
            (TYPE_IEC_C7, 'C7'),
            (TYPE_IEC_C13, 'C13'),
            (TYPE_IEC_C15, 'C15'),
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
        ('NEMA (Non-locking)', (
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
        ('NEMA (Locking)', (
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
        )),
        ('California Style', (
            (TYPE_CS6360C, 'CS6360C'),
            (TYPE_CS6364C, 'CS6364C'),
            (TYPE_CS8164C, 'CS8164C'),
            (TYPE_CS8264C, 'CS8264C'),
            (TYPE_CS8364C, 'CS8364C'),
            (TYPE_CS8464C, 'CS8464C'),
        )),
        ('ITA/International', (
            (TYPE_ITA_E, 'ITA Type E (CEE7/5)'),
            (TYPE_ITA_F, 'ITA Type F (CEE7/3)'),
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
            (TYPE_USB_MICROB, 'USB Micro B'),
            (TYPE_USB_C, 'USB Type C'),
        )),
        ('DC', (
            (TYPE_DC, 'DC Terminal'),
        )),
        ('Proprietary', (
            (TYPE_HDOT_CX, 'HDOT Cx'),
            (TYPE_SAF_D_GRID, 'Saf-D-Grid'),
        )),
        ('Other', (
            (TYPE_HARDWIRED, 'Hardwired'),
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
        (KIND_PHYSICAL, 'Physical'),
        (KIND_VIRTUAL, 'Virtual'),
        (KIND_WIRELESS, 'Wireless'),
    )


class InterfaceTypeChoices(ChoiceSet):

    # Virtual
    TYPE_VIRTUAL = 'virtual'
    TYPE_LAG = 'lag'

    # Ethernet
    TYPE_100ME_FIXED = '100base-tx'
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
    TYPE_100GE_CPAK = '100gbase-x-cpak'
    TYPE_100GE_QSFP28 = '100gbase-x-qsfp28'
    TYPE_200GE_CFP2 = '200gbase-x-cfp2'
    TYPE_200GE_QSFP56 = '200gbase-x-qsfp56'
    TYPE_400GE_QSFP_DD = '400gbase-x-qsfpdd'
    TYPE_400GE_OSFP = '400gbase-x-osfp'

    # Wireless
    TYPE_80211A = 'ieee802.11a'
    TYPE_80211G = 'ieee802.11g'
    TYPE_80211N = 'ieee802.11n'
    TYPE_80211AC = 'ieee802.11ac'
    TYPE_80211AD = 'ieee802.11ad'
    TYPE_80211AX = 'ieee802.11ax'

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
    TYPE_128GFC_QSFP28 = '128gfc-sfp28'

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

    # Stacking
    TYPE_STACKWISE = 'cisco-stackwise'
    TYPE_STACKWISE_PLUS = 'cisco-stackwise-plus'
    TYPE_FLEXSTACK = 'cisco-flexstack'
    TYPE_FLEXSTACK_PLUS = 'cisco-flexstack-plus'
    TYPE_JUNIPER_VCP = 'juniper-vcp'
    TYPE_SUMMITSTACK = 'extreme-summitstack'
    TYPE_SUMMITSTACK128 = 'extreme-summitstack-128'
    TYPE_SUMMITSTACK256 = 'extreme-summitstack-256'
    TYPE_SUMMITSTACK512 = 'extreme-summitstack-512'

    # Other
    TYPE_OTHER = 'other'

    CHOICES = (
        (
            'Virtual interfaces',
            (
                (TYPE_VIRTUAL, 'Virtual'),
                (TYPE_LAG, 'Link Aggregation Group (LAG)'),
            ),
        ),
        (
            'Ethernet (fixed)',
            (
                (TYPE_100ME_FIXED, '100BASE-TX (10/100ME)'),
                (TYPE_1GE_FIXED, '1000BASE-T (1GE)'),
                (TYPE_2GE_FIXED, '2.5GBASE-T (2.5GE)'),
                (TYPE_5GE_FIXED, '5GBASE-T (5GE)'),
                (TYPE_10GE_FIXED, '10GBASE-T (10GE)'),
                (TYPE_10GE_CX4, '10GBASE-CX4 (10GE)'),
            )
        ),
        (
            'Ethernet (modular)',
            (
                (TYPE_1GE_GBIC, 'GBIC (1GE)'),
                (TYPE_1GE_SFP, 'SFP (1GE)'),
                (TYPE_10GE_SFP_PLUS, 'SFP+ (10GE)'),
                (TYPE_10GE_XFP, 'XFP (10GE)'),
                (TYPE_10GE_XENPAK, 'XENPAK (10GE)'),
                (TYPE_10GE_X2, 'X2 (10GE)'),
                (TYPE_25GE_SFP28, 'SFP28 (25GE)'),
                (TYPE_50GE_SFP56, 'SFP56 (50GE)'),
                (TYPE_40GE_QSFP_PLUS, 'QSFP+ (40GE)'),
                (TYPE_50GE_QSFP28, 'QSFP28 (50GE)'),
                (TYPE_100GE_CFP, 'CFP (100GE)'),
                (TYPE_100GE_CFP2, 'CFP2 (100GE)'),
                (TYPE_200GE_CFP2, 'CFP2 (200GE)'),
                (TYPE_100GE_CFP4, 'CFP4 (100GE)'),
                (TYPE_100GE_CPAK, 'Cisco CPAK (100GE)'),
                (TYPE_100GE_QSFP28, 'QSFP28 (100GE)'),
                (TYPE_200GE_QSFP56, 'QSFP56 (200GE)'),
                (TYPE_400GE_QSFP_DD, 'QSFP-DD (400GE)'),
                (TYPE_400GE_OSFP, 'OSFP (400GE)'),
            )
        ),
        (
            'Wireless',
            (
                (TYPE_80211A, 'IEEE 802.11a'),
                (TYPE_80211G, 'IEEE 802.11b/g'),
                (TYPE_80211N, 'IEEE 802.11n'),
                (TYPE_80211AC, 'IEEE 802.11ac'),
                (TYPE_80211AD, 'IEEE 802.11ad'),
                (TYPE_80211AX, 'IEEE 802.11ax'),
            )
        ),
        (
            'Cellular',
            (
                (TYPE_GSM, 'GSM'),
                (TYPE_CDMA, 'CDMA'),
                (TYPE_LTE, 'LTE'),
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
                (TYPE_64GFC_QSFP_PLUS, 'QSFP+ (64GFC)'),
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
            'Serial',
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
            'Stacking',
            (
                (TYPE_STACKWISE, 'Cisco StackWise'),
                (TYPE_STACKWISE_PLUS, 'Cisco StackWise Plus'),
                (TYPE_FLEXSTACK, 'Cisco FlexStack'),
                (TYPE_FLEXSTACK_PLUS, 'Cisco FlexStack Plus'),
                (TYPE_JUNIPER_VCP, 'Juniper VCP'),
                (TYPE_SUMMITSTACK, 'Extreme SummitStack'),
                (TYPE_SUMMITSTACK128, 'Extreme SummitStack-128'),
                (TYPE_SUMMITSTACK256, 'Extreme SummitStack-256'),
                (TYPE_SUMMITSTACK512, 'Extreme SummitStack-512'),
            )
        ),
        (
            'Other',
            (
                (TYPE_OTHER, 'Other'),
            )
        ),
    )


class InterfaceModeChoices(ChoiceSet):

    MODE_ACCESS = 'access'
    MODE_TAGGED = 'tagged'
    MODE_TAGGED_ALL = 'tagged-all'

    CHOICES = (
        (MODE_ACCESS, 'Access'),
        (MODE_TAGGED, 'Tagged'),
        (MODE_TAGGED_ALL, 'Tagged (All)'),
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
    TYPE_SC_APC = 'sc-apc'
    TYPE_FC = 'fc'
    TYPE_LC = 'lc'
    TYPE_LC_APC = 'lc-apc'
    TYPE_MTRJ = 'mtrj'
    TYPE_MPO = 'mpo'
    TYPE_LSH = 'lsh'
    TYPE_LSH_APC = 'lsh-apc'
    TYPE_SPLICE = 'splice'
    TYPE_CS = 'cs'
    TYPE_SN = 'sn'
    TYPE_SMA_905 = 'sma-905'
    TYPE_SMA_906 = 'sma-906'
    TYPE_URM_P2 = 'urm-p2'
    TYPE_URM_P4 = 'urm-p4'
    TYPE_URM_P8 = 'urm-p8'

    CHOICES = (
        (
            'Copper',
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
            'Fiber Optic',
            (
                (TYPE_FC, 'FC'),
                (TYPE_LC, 'LC'),
                (TYPE_LC_APC, 'LC/APC'),
                (TYPE_LSH, 'LSH'),
                (TYPE_LSH_APC, 'LSH/APC'),
                (TYPE_MPO, 'MPO'),
                (TYPE_MTRJ, 'MTRJ'),
                (TYPE_SC, 'SC'),
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
            'Copper', (
                (TYPE_CAT3, 'CAT3'),
                (TYPE_CAT5, 'CAT5'),
                (TYPE_CAT5E, 'CAT5e'),
                (TYPE_CAT6, 'CAT6'),
                (TYPE_CAT6A, 'CAT6a'),
                (TYPE_CAT7, 'CAT7'),
                (TYPE_CAT7A, 'CAT7a'),
                (TYPE_CAT8, 'CAT8'),
                (TYPE_DAC_ACTIVE, 'Direct Attach Copper (Active)'),
                (TYPE_DAC_PASSIVE, 'Direct Attach Copper (Passive)'),
                (TYPE_MRJ21_TRUNK, 'MRJ21 Trunk'),
                (TYPE_COAXIAL, 'Coaxial'),
            ),
        ),
        (
            'Fiber', (
                (TYPE_MMF, 'Multimode Fiber'),
                (TYPE_MMF_OM1, 'Multimode Fiber (OM1)'),
                (TYPE_MMF_OM2, 'Multimode Fiber (OM2)'),
                (TYPE_MMF_OM3, 'Multimode Fiber (OM3)'),
                (TYPE_MMF_OM4, 'Multimode Fiber (OM4)'),
                (TYPE_MMF_OM5, 'Multimode Fiber (OM5)'),
                (TYPE_SMF, 'Singlemode Fiber'),
                (TYPE_SMF_OS1, 'Singlemode Fiber (OS1)'),
                (TYPE_SMF_OS2, 'Singlemode Fiber (OS2)'),
                (TYPE_AOC, 'Active Optical Cabling (AOC)'),
            ),
        ),
        (TYPE_POWER, 'Power'),
    )


class LinkStatusChoices(ChoiceSet):

    STATUS_CONNECTED = 'connected'
    STATUS_PLANNED = 'planned'
    STATUS_DECOMMISSIONING = 'decommissioning'

    CHOICES = (
        (STATUS_CONNECTED, 'Connected'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_DECOMMISSIONING, 'Decommissioning'),
    )

    CSS_CLASSES = {
        STATUS_CONNECTED: 'success',
        STATUS_PLANNED: 'info',
        STATUS_DECOMMISSIONING: 'warning',
    }


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
        (UNIT_KILOMETER, 'Kilometers'),
        (UNIT_METER, 'Meters'),
        (UNIT_CENTIMETER, 'Centimeters'),
        (UNIT_MILE, 'Miles'),
        (UNIT_FOOT, 'Feet'),
        (UNIT_INCH, 'Inches'),
    )


#
# PowerFeeds
#

class PowerFeedStatusChoices(ChoiceSet):

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'

    CHOICES = (
        (STATUS_OFFLINE, 'Offline'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PLANNED, 'Planned'),
        (STATUS_FAILED, 'Failed'),
    )

    CSS_CLASSES = {
        STATUS_OFFLINE: 'warning',
        STATUS_ACTIVE: 'success',
        STATUS_PLANNED: 'info',
        STATUS_FAILED: 'danger',
    }


class PowerFeedTypeChoices(ChoiceSet):

    TYPE_PRIMARY = 'primary'
    TYPE_REDUNDANT = 'redundant'

    CHOICES = (
        (TYPE_PRIMARY, 'Primary'),
        (TYPE_REDUNDANT, 'Redundant'),
    )

    CSS_CLASSES = {
        TYPE_PRIMARY: 'success',
        TYPE_REDUNDANT: 'info',
    }


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
        (PHASE_SINGLE, 'Single phase'),
        (PHASE_3PHASE, 'Three-phase'),
    )
