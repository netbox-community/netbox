from enum import Enum
import strawberry


#
# Sites
#

@strawberry.enum
class SiteStatusEnum(Enum):
    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_RETIRED = 'retired'


#
# Locations
#

@strawberry.enum
class LocationStatusEnum(Enum):
    STATUS_PLANNED = 'planned'
    STATUS_STAGING = 'staging'
    STATUS_ACTIVE = 'active'
    STATUS_DECOMMISSIONING = 'decommissioning'
    STATUS_RETIRED = 'retired'


#
# Racks
#

@strawberry.enum
class RackFormFactorEnum(Enum):
    TYPE_2POST = '2-post-frame'
    TYPE_4POST = '4-post-frame'
    TYPE_CABINET = '4-post-cabinet'
    TYPE_WALLFRAME = 'wall-frame'
    TYPE_WALLFRAME_VERTICAL = 'wall-frame-vertical'
    TYPE_WALLCABINET = 'wall-cabinet'
    TYPE_WALLCABINET_VERTICAL = 'wall-cabinet-vertical'


@strawberry.enum
class RackWidthEnum(Enum):

    WIDTH_10IN = 10
    WIDTH_19IN = 19
    WIDTH_21IN = 21
    WIDTH_23IN = 23


@strawberry.enum
class RackStatusEnum(Enum):
    STATUS_RESERVED = 'reserved'
    STATUS_AVAILABLE = 'available'
    STATUS_PLANNED = 'planned'
    STATUS_ACTIVE = 'active'
    STATUS_DEPRECATED = 'deprecated'


@strawberry.enum
class RackDimensionUnitEnum(Enum):
    UNIT_MILLIMETER = 'mm'
    UNIT_INCH = 'in'


@strawberry.enum
class RackElevationDetailRenderEnum(Enum):
    RENDER_JSON = 'json'
    RENDER_SVG = 'svg'


@strawberry.enum
class RackAirflowEnum(Enum):
    FRONT_TO_REAR = 'front-to-rear'
    REAR_TO_FRONT = 'rear-to-front'


#
# DeviceTypes
#

@strawberry.enum
class SubdeviceRoleEnum(Enum):
    ROLE_PARENT = 'parent'
    ROLE_CHILD = 'child'


#
# Devices
#

@strawberry.enum
class DeviceFaceEnum(Enum):
    FACE_FRONT = 'front'
    FACE_REAR = 'rear'


@strawberry.enum
class DeviceStatusEnum(Enum):
    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_INVENTORY = 'inventory'
    STATUS_DECOMMISSIONING = 'decommissioning'


@strawberry.enum
class DeviceAirflowEnum(Enum):

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


#
# Modules
#

@strawberry.enum
class ModuleStatusEnum(Enum):
    key = 'Module.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'


@strawberry.enum
class ModuleAirflowEnum(Enum):

    FRONT_TO_REAR = 'front-to-rear'
    REAR_TO_FRONT = 'rear-to-front'
    LEFT_TO_RIGHT = 'left-to-right'
    RIGHT_TO_LEFT = 'right-to-left'
    SIDE_TO_REAR = 'side-to-rear'
    PASSIVE = 'passive'


#
# ConsolePorts
#

@strawberry.enum
class ConsolePortTypeEnum(Enum):

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


@strawberry.enum
class ConsolePortSpeedEnum(Enum):

    SPEED_1200 = 1200
    SPEED_2400 = 2400
    SPEED_4800 = 4800
    SPEED_9600 = 9600
    SPEED_19200 = 19200
    SPEED_38400 = 38400
    SPEED_57600 = 57600
    SPEED_115200 = 115200


#
# PowerPorts
#

@strawberry.enum
class PowerPortTypeEnum(Enum):

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


#
# PowerOutlets
#

@strawberry.enum
class PowerOutletTypeEnum(Enum):

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


@strawberry.enum
class PowerOutletFeedLegEnum(Enum):

    FEED_LEG_A = 'A'
    FEED_LEG_B = 'B'
    FEED_LEG_C = 'C'


#
# Interfaces
#

@strawberry.enum
class InterfaceKindEnum(Enum):
    KIND_PHYSICAL = 'physical'
    KIND_VIRTUAL = 'virtual'
    KIND_WIRELESS = 'wireless'


@strawberry.enum
class InterfaceTypeEnum(Enum):

    # Virtual
    TYPE_VIRTUAL = 'virtual'
    TYPE_BRIDGE = 'bridge'
    TYPE_LAG = 'lag'

    # Ethernet
    TYPE_100ME_FX = '100base-fx'
    TYPE_100ME_LFX = '100base-lfx'
    TYPE_100ME_FIXED = '100base-tx'
    TYPE_100ME_T1 = '100base-t1'
    TYPE_100ME_SFP = '100base-x-sfp'
    TYPE_1GE_FIXED = '1000base-t'
    TYPE_1GE_LX_FIXED = '1000base-lx'
    TYPE_1GE_TX_FIXED = '1000base-tx'
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
    TYPE_400GE_CFP2 = '400gbase-x-cfp2'
    TYPE_400GE_QSFP112 = '400gbase-x-qsfp112'
    TYPE_400GE_QSFP_DD = '400gbase-x-qsfpdd'
    TYPE_400GE_OSFP = '400gbase-x-osfp'
    TYPE_400GE_OSFP_RHS = '400gbase-x-osfp-rhs'
    TYPE_400GE_CDFP = '400gbase-x-cdfp'
    TYPE_400GE_CFP8 = '400gbase-x-cfp8'
    TYPE_800GE_QSFP_DD = '800gbase-x-qsfpdd'
    TYPE_800GE_OSFP = '800gbase-x-osfp'

    # Ethernet Backplane
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


@strawberry.enum
class InterfaceSpeedEnum(Enum):
    SPEED_10MBPS = 10000
    SPEED_100MBPS = 100000
    SPEED_1GBPS = 1000000
    SPEED_10GBPS = 10000000
    SPEED_25GBPS = 25000000
    SPEED_40GBPS = 40000000
    SPEED_100GBPS = 100000000
    SPEED_200GBPS = 200000000
    SPEED_400GBPS = 400000000


@strawberry.enum
class InterfaceDuplexEnum(Enum):

    DUPLEX_HALF = 'half'
    DUPLEX_FULL = 'full'
    DUPLEX_AUTO = 'auto'


@strawberry.enum
class InterfaceModeEnum(Enum):

    MODE_ACCESS = 'access'
    MODE_TAGGED = 'tagged'
    MODE_TAGGED_ALL = 'tagged-all'
    MODE_Q_IN_Q = 'q-in-q'


@strawberry.enum
class InterfacePoEModeEnum(Enum):

    MODE_PD = 'pd'
    MODE_PSE = 'pse'


@strawberry.enum
class InterfacePoETypeEnum(Enum):

    TYPE_1_8023AF = 'type1-ieee802.3af'
    TYPE_2_8023AT = 'type2-ieee802.3at'
    TYPE_3_8023BT = 'type3-ieee802.3bt'
    TYPE_4_8023BT = 'type4-ieee802.3bt'

    PASSIVE_24V_2PAIR = 'passive-24v-2pair'
    PASSIVE_24V_4PAIR = 'passive-24v-4pair'
    PASSIVE_48V_2PAIR = 'passive-48v-2pair'
    PASSIVE_48V_4PAIR = 'passive-48v-4pair'


#
# FrontPorts/RearPorts
#

@strawberry.enum
class PortTypeEnum(Enum):

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
    TYPE_USB_A = 'usb-a'
    TYPE_USB_B = 'usb-b'
    TYPE_USB_C = 'usb-c'
    TYPE_USB_MINI_A = 'usb-mini-a'
    TYPE_USB_MINI_B = 'usb-mini-b'
    TYPE_USB_MICRO_A = 'usb-micro-a'
    TYPE_USB_MICRO_B = 'usb-micro-b'
    TYPE_USB_MICRO_AB = 'usb-micro-ab'
    TYPE_OTHER = 'other'


#
# Cables/links
#

@strawberry.enum
class CableTypeEnum(Enum):

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
    TYPE_USB = 'usb'


@strawberry.enum
class LinkStatusEnum(Enum):

    STATUS_CONNECTED = 'connected'
    STATUS_PLANNED = 'planned'
    STATUS_DECOMMISSIONING = 'decommissioning'


@strawberry.enum
class CableLengthUnitEnum(Enum):

    # Metric
    UNIT_KILOMETER = 'km'
    UNIT_METER = 'm'
    UNIT_CENTIMETER = 'cm'

    # Imperial
    UNIT_MILE = 'mi'
    UNIT_FOOT = 'ft'
    UNIT_INCH = 'in'


#
# CableTerminations
#

@strawberry.enum
class CableEndEnum(Enum):
    SIDE_A = 'A'
    SIDE_B = 'B'


#
# PowerFeeds
#

@strawberry.enum
class PowerFeedStatusEnum(Enum):
    key = 'PowerFeed.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_FAILED = 'failed'


@strawberry.enum
class PowerFeedTypeEnum(Enum):

    TYPE_PRIMARY = 'primary'
    TYPE_REDUNDANT = 'redundant'


@strawberry.enum
class PowerFeedSupplyEnum(Enum):

    SUPPLY_AC = 'ac'
    SUPPLY_DC = 'dc'


@strawberry.enum
class PowerFeedPhaseEnum(Enum):

    PHASE_SINGLE = 'single-phase'
    PHASE_3PHASE = 'three-phase'


#
# VDC
#
@strawberry.enum
class VirtualDeviceContextStatusEnum(Enum):
    key = 'VirtualDeviceContext.status'

    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_OFFLINE = 'offline'


#
# InventoryItem
#

@strawberry.enum
class InventoryItemStatusEnum(Enum):
    key = 'InventoryItem.status'

    STATUS_OFFLINE = 'offline'
    STATUS_ACTIVE = 'active'
    STATUS_PLANNED = 'planned'
    STATUS_STAGED = 'staged'
    STATUS_FAILED = 'failed'
    STATUS_DECOMMISSIONING = 'decommissioning'
