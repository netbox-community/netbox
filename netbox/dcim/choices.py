from utilities.choices import ChoiceSet


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

    LEGACY_MAP = {
        TYPE_2POST: 100,
        TYPE_4POST: 200,
        TYPE_CABINET: 300,
        TYPE_WALLFRAME: 1000,
        TYPE_WALLCABINET: 1100,
    }


class RackWidthChoices(ChoiceSet):

    WIDTH_19IN = 19
    WIDTH_23IN = 23

    CHOICES = (
        (WIDTH_19IN, '19 inches'),
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

    LEGACY_MAP = {
        STATUS_RESERVED: 0,
        STATUS_AVAILABLE: 1,
        STATUS_PLANNED: 2,
        STATUS_ACTIVE: 3,
        STATUS_DEPRECATED: 4,
    }


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

    LEGACY_MAP = {
        ROLE_PARENT: True,
        ROLE_CHILD: False,
    }


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

    LEGACY_MAP = {
        FACE_FRONT: 0,
        FACE_REAR: 1,
    }


#
# ConsolePorts
#

class ConsolePortTypeChoices(ChoiceSet):
    """
    ConsolePort/ConsoleServerPort.type slugs
    """
    TYPE_DE9 = 'de-9'
    TYPE_DB25 = 'db-25'
    TYPE_RJ45 = 'rj-45'
    TYPE_USB_A = 'usb-a'
    TYPE_USB_B = 'usb-b'
    TYPE_USB_C = 'usb-c'
    TYPE_USB_MINI_A = 'usb-mini-a'
    TYPE_USB_MINI_B = 'usb-mini-b'
    TYPE_USB_MICRO_A = 'usb-micro-a'
    TYPE_USB_MICRO_B = 'usb-micro-b'
    TYPE_OTHER = 'other'

    CHOICES = (
        ('Serial', (
            (TYPE_DE9, 'DE-9'),
            (TYPE_DB25, 'DB-25'),
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
        )),
        ('Other', (
            (TYPE_OTHER, 'Other'),
        )),
    )


#
# PowerPorts
#

class PowerPortTypeChoices(ChoiceSet):
    # TODO: Add more power port types
    # IEC 60320
    TYPE_IEC_C6 = 'iec-60320-c6'
    TYPE_IEC_C8 = 'iec-60320-c8'
    TYPE_IEC_C14 = 'iec-60320-c14'
    TYPE_IEC_C16 = 'iec-60320-c16'
    TYPE_IEC_C20 = 'iec-60320-c20'
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
    TYPE_NEMA_515P = 'nema-5-15p'
    TYPE_NEMA_520P = 'nema-5-20p'
    TYPE_NEMA_530P = 'nema-5-30p'
    TYPE_NEMA_550P = 'nema-5-50p'
    TYPE_NEMA_615P = 'nema-6-15p'
    TYPE_NEMA_620P = 'nema-6-20p'
    TYPE_NEMA_630P = 'nema-6-30p'
    TYPE_NEMA_650P = 'nema-6-50p'
    # NEMA locking
    TYPE_NEMA_L515P = 'nema-l5-15p'
    TYPE_NEMA_L520P = 'nema-l5-20p'
    TYPE_NEMA_L530P = 'nema-l5-30p'
    TYPE_NEMA_L615P = 'nema-l5-50p'
    TYPE_NEMA_L620P = 'nema-l6-20p'
    TYPE_NEMA_L630P = 'nema-l6-30p'
    TYPE_NEMA_L650P = 'nema-l6-50p'

    CHOICES = (
        ('IEC 60320', (
            (TYPE_IEC_C6, 'C6'),
            (TYPE_IEC_C8, 'C8'),
            (TYPE_IEC_C14, 'C14'),
            (TYPE_IEC_C16, 'C16'),
            (TYPE_IEC_C20, 'C20'),
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
            (TYPE_NEMA_515P, 'NEMA 5-15P'),
            (TYPE_NEMA_520P, 'NEMA 5-20P'),
            (TYPE_NEMA_530P, 'NEMA 5-30P'),
            (TYPE_NEMA_550P, 'NEMA 5-50P'),
            (TYPE_NEMA_615P, 'NEMA 6-15P'),
            (TYPE_NEMA_620P, 'NEMA 6-20P'),
            (TYPE_NEMA_630P, 'NEMA 6-30P'),
            (TYPE_NEMA_650P, 'NEMA 6-50P'),
        )),
        ('NEMA (Locking)', (
            (TYPE_NEMA_L515P, 'NEMA L5-15P'),
            (TYPE_NEMA_L520P, 'NEMA L5-20P'),
            (TYPE_NEMA_L530P, 'NEMA L5-30P'),
            (TYPE_NEMA_L615P, 'NEMA L6-15P'),
            (TYPE_NEMA_L620P, 'NEMA L6-20P'),
            (TYPE_NEMA_L630P, 'NEMA L6-30P'),
            (TYPE_NEMA_L650P, 'NEMA L6-50P'),
        )),
    )


#
# PowerOutlets
#

class PowerOutletTypeChoices(ChoiceSet):
    # TODO: Add more power outlet types
    # IEC 60320
    TYPE_IEC_C5 = 'iec-60320-c5'
    TYPE_IEC_C7 = 'iec-60320-c7'
    TYPE_IEC_C13 = 'iec-60320-c13'
    TYPE_IEC_C15 = 'iec-60320-c15'
    TYPE_IEC_C19 = 'iec-60320-c19'
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
    TYPE_NEMA_515R = 'nema-5-15r'
    TYPE_NEMA_520R = 'nema-5-20r'
    TYPE_NEMA_530R = 'nema-5-30r'
    TYPE_NEMA_550R = 'nema-5-50r'
    TYPE_NEMA_615R = 'nema-6-15r'
    TYPE_NEMA_620R = 'nema-6-20r'
    TYPE_NEMA_630R = 'nema-6-30r'
    TYPE_NEMA_650R = 'nema-6-50r'
    # NEMA locking
    TYPE_NEMA_L515R = 'nema-l5-15r'
    TYPE_NEMA_L520R = 'nema-l5-20r'
    TYPE_NEMA_L530R = 'nema-l5-30r'
    TYPE_NEMA_L615R = 'nema-l5-50r'
    TYPE_NEMA_L620R = 'nema-l6-20r'
    TYPE_NEMA_L630R = 'nema-l6-30r'
    TYPE_NEMA_L650R = 'nema-l6-50r'

    CHOICES = (
        ('IEC 60320', (
            (TYPE_IEC_C5, 'C5'),
            (TYPE_IEC_C7, 'C7'),
            (TYPE_IEC_C13, 'C13'),
            (TYPE_IEC_C15, 'C15'),
            (TYPE_IEC_C19, 'C19'),
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
            (TYPE_NEMA_515R, 'NEMA 5-15R'),
            (TYPE_NEMA_520R, 'NEMA 5-20R'),
            (TYPE_NEMA_530R, 'NEMA 5-30R'),
            (TYPE_NEMA_550R, 'NEMA 5-50R'),
            (TYPE_NEMA_615R, 'NEMA 6-15R'),
            (TYPE_NEMA_620R, 'NEMA 6-20R'),
            (TYPE_NEMA_630R, 'NEMA 6-30R'),
            (TYPE_NEMA_650R, 'NEMA 6-50R'),
        )),
        ('NEMA (Locking)', (
            (TYPE_NEMA_L515R, 'NEMA L5-15R'),
            (TYPE_NEMA_L520R, 'NEMA L5-20R'),
            (TYPE_NEMA_L530R, 'NEMA L5-30R'),
            (TYPE_NEMA_L615R, 'NEMA L6-15R'),
            (TYPE_NEMA_L620R, 'NEMA L6-20R'),
            (TYPE_NEMA_L630R, 'NEMA L6-30R'),
            (TYPE_NEMA_L650R, 'NEMA L6-50R'),
        )),
    )


#
# Interfaces
#

class InterfaceTypeChoices(ChoiceSet):
    """
    Interface.type slugs
    """
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
    TYPE_128GFC_QSFP28 = '128gfc-sfp28'

    # InfiniBand
    TYPE_INFINIBAND_SDR = 'inifiband-sdr'
    TYPE_INFINIBAND_DDR = 'inifiband-ddr'
    TYPE_INFINIBAND_QDR = 'inifiband-qdr'
    TYPE_INFINIBAND_FDR10 = 'inifiband-fdr10'
    TYPE_INFINIBAND_FDR = 'inifiband-fdr'
    TYPE_INFINIBAND_EDR = 'inifiband-edr'
    TYPE_INFINIBAND_HDR = 'inifiband-hdr'
    TYPE_INFINIBAND_NDR = 'inifiband-ndr'
    TYPE_INFINIBAND_XDR = 'inifiband-xdr'

    # Serial
    TYPE_T1 = 't1'
    TYPE_E1 = 'e1'
    TYPE_T3 = 't3'
    TYPE_E3 = 'e3'

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

    LEGACY_MAP = {
        TYPE_VIRTUAL: 0,
        TYPE_LAG: 200,
        TYPE_100ME_FIXED: 800,
        TYPE_1GE_FIXED: 1000,
        TYPE_1GE_GBIC: 1050,
        TYPE_1GE_SFP: 1100,
        TYPE_2GE_FIXED: 1120,
        TYPE_5GE_FIXED: 1130,
        TYPE_10GE_FIXED: 1150,
        TYPE_10GE_CX4: 1170,
        TYPE_10GE_SFP_PLUS: 1200,
        TYPE_10GE_XFP: 1300,
        TYPE_10GE_XENPAK: 1310,
        TYPE_10GE_X2: 1320,
        TYPE_25GE_SFP28: 1350,
        TYPE_40GE_QSFP_PLUS: 1400,
        TYPE_50GE_QSFP28: 1420,
        TYPE_100GE_CFP: 1500,
        TYPE_100GE_CFP2: 1510,
        TYPE_100GE_CFP4: 1520,
        TYPE_100GE_CPAK: 1550,
        TYPE_100GE_QSFP28: 1600,
        TYPE_200GE_CFP2: 1650,
        TYPE_200GE_QSFP56: 1700,
        TYPE_400GE_QSFP_DD: 1750,
        TYPE_400GE_OSFP: 1800,
        TYPE_80211A: 2600,
        TYPE_80211G: 2610,
        TYPE_80211N: 2620,
        TYPE_80211AC: 2630,
        TYPE_80211AD: 2640,
        TYPE_GSM: 2810,
        TYPE_CDMA: 2820,
        TYPE_LTE: 2830,
        TYPE_SONET_OC3: 6100,
        TYPE_SONET_OC12: 6200,
        TYPE_SONET_OC48: 6300,
        TYPE_SONET_OC192: 6400,
        TYPE_SONET_OC768: 6500,
        TYPE_SONET_OC1920: 6600,
        TYPE_SONET_OC3840: 6700,
        TYPE_1GFC_SFP: 3010,
        TYPE_2GFC_SFP: 3020,
        TYPE_4GFC_SFP: 3040,
        TYPE_8GFC_SFP_PLUS: 3080,
        TYPE_16GFC_SFP_PLUS: 3160,
        TYPE_32GFC_SFP28: 3320,
        TYPE_128GFC_QSFP28: 3400,
        TYPE_INFINIBAND_SDR: 7010,
        TYPE_INFINIBAND_DDR: 7020,
        TYPE_INFINIBAND_QDR: 7030,
        TYPE_INFINIBAND_FDR10: 7040,
        TYPE_INFINIBAND_FDR: 7050,
        TYPE_INFINIBAND_EDR: 7060,
        TYPE_INFINIBAND_HDR: 7070,
        TYPE_INFINIBAND_NDR: 7080,
        TYPE_INFINIBAND_XDR: 7090,
        TYPE_T1: 4000,
        TYPE_E1: 4010,
        TYPE_T3: 4040,
        TYPE_E3: 4050,
        TYPE_STACKWISE: 5000,
        TYPE_STACKWISE_PLUS: 5050,
        TYPE_FLEXSTACK: 5100,
        TYPE_FLEXSTACK_PLUS: 5150,
        TYPE_JUNIPER_VCP: 5200,
        TYPE_SUMMITSTACK: 5300,
        TYPE_SUMMITSTACK128: 5310,
        TYPE_SUMMITSTACK256: 5320,
        TYPE_SUMMITSTACK512: 5330,
    }


#
# FrontPorts/RearPorts
#

class PortTypeChoices(ChoiceSet):
    """
    FrontPort/RearPort.type slugs
    """
    TYPE_8P8C = '8p8c'
    TYPE_110_PUNCH = '110-punch'
    TYPE_BNC = 'bnc'
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

    CHOICES = (
        (
            'Copper',
            (
                (TYPE_8P8C, '8P8C'),
                (TYPE_110_PUNCH, '110 Punch'),
                (TYPE_BNC, 'BNC'),
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
            )
        )
    )

    LEGACY_MAP = {
        TYPE_8P8C: 1000,
        TYPE_110_PUNCH: 1100,
        TYPE_BNC: 1200,
        TYPE_ST: 2000,
        TYPE_SC: 2100,
        TYPE_SC_APC: 2110,
        TYPE_FC: 2200,
        TYPE_LC: 2300,
        TYPE_LC_APC: 2310,
        TYPE_MTRJ: 2400,
        TYPE_MPO: 2500,
        TYPE_LSH: 2600,
        TYPE_LSH_APC: 2610,
    }
