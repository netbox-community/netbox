from .constants import *


#
# Console port type values
#

class ConsolePortTypes:
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

    TYPE_CHOICES = (
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

    @classmethod
    def slug_to_integer(cls, slug):
        """
        Provide backward-compatible mapping of the type slug to integer.
        """
        return {
            # Slug: integer
            cls.TYPE_DE9: CONSOLE_TYPE_DE9,
            cls.TYPE_DB25: CONSOLE_TYPE_DB25,
            cls.TYPE_RJ45: CONSOLE_TYPE_RJ45,
            cls.TYPE_USB_A: CONSOLE_TYPE_USB_A,
            cls.TYPE_USB_B: CONSOLE_TYPE_USB_B,
            cls.TYPE_USB_C: CONSOLE_TYPE_USB_C,
            cls.TYPE_USB_MINI_A: CONSOLE_TYPE_USB_MINI_A,
            cls.TYPE_USB_MINI_B: CONSOLE_TYPE_USB_MINI_B,
            cls.TYPE_USB_MICRO_A: CONSOLE_TYPE_USB_MICRO_A,
            cls.TYPE_USB_MICRO_B: CONSOLE_TYPE_USB_MICRO_B,
            cls.TYPE_OTHER: CONSOLE_TYPE_OTHER,
        }.get(slug)


#
# Interface type values
#

class InterfaceTypes:
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

    TYPE_CHOICES = (
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

    @classmethod
    def slug_to_integer(cls, slug):
        """
        Provide backward-compatible mapping of the type slug to integer.
        """
        return {
            # Slug: integer
            cls.TYPE_VIRTUAL: IFACE_TYPE_VIRTUAL,
            cls.TYPE_LAG: IFACE_TYPE_LAG,
            cls.TYPE_100ME_FIXED: IFACE_TYPE_100ME_FIXED,
            cls.TYPE_1GE_FIXED: IFACE_TYPE_1GE_FIXED,
            cls.TYPE_1GE_GBIC: IFACE_TYPE_1GE_GBIC,
            cls.TYPE_1GE_SFP: IFACE_TYPE_1GE_SFP,
            cls.TYPE_2GE_FIXED: IFACE_TYPE_2GE_FIXED,
            cls.TYPE_5GE_FIXED: IFACE_TYPE_5GE_FIXED,
            cls.TYPE_10GE_FIXED: IFACE_TYPE_10GE_FIXED,
            cls.TYPE_10GE_CX4: IFACE_TYPE_10GE_CX4,
            cls.TYPE_10GE_SFP_PLUS: IFACE_TYPE_10GE_SFP_PLUS,
            cls.TYPE_10GE_XFP: IFACE_TYPE_10GE_XFP,
            cls.TYPE_10GE_XENPAK: IFACE_TYPE_10GE_XENPAK,
            cls.TYPE_10GE_X2: IFACE_TYPE_10GE_X2,
            cls.TYPE_25GE_SFP28: IFACE_TYPE_25GE_SFP28,
            cls.TYPE_40GE_QSFP_PLUS: IFACE_TYPE_40GE_QSFP_PLUS,
            cls.TYPE_50GE_QSFP28: IFACE_TYPE_50GE_QSFP28,
            cls.TYPE_100GE_CFP: IFACE_TYPE_100GE_CFP,
            cls.TYPE_100GE_CFP2: IFACE_TYPE_100GE_CFP2,
            cls.TYPE_100GE_CFP4: IFACE_TYPE_100GE_CFP4,
            cls.TYPE_100GE_CPAK: IFACE_TYPE_100GE_CPAK,
            cls.TYPE_100GE_QSFP28: IFACE_TYPE_100GE_QSFP28,
            cls.TYPE_200GE_CFP2: IFACE_TYPE_200GE_CFP2,
            cls.TYPE_200GE_QSFP56: IFACE_TYPE_200GE_QSFP56,
            cls.TYPE_400GE_QSFP_DD: IFACE_TYPE_400GE_QSFP_DD,
            cls.TYPE_80211A: IFACE_TYPE_80211A,
            cls.TYPE_80211G: IFACE_TYPE_80211G,
            cls.TYPE_80211N: IFACE_TYPE_80211N,
            cls.TYPE_80211AC: IFACE_TYPE_80211AC,
            cls.TYPE_80211AD: IFACE_TYPE_80211AD,
            cls.TYPE_GSM: IFACE_TYPE_GSM,
            cls.TYPE_CDMA: IFACE_TYPE_CDMA,
            cls.TYPE_LTE: IFACE_TYPE_LTE,
            cls.TYPE_SONET_OC3: IFACE_TYPE_SONET_OC3,
            cls.TYPE_SONET_OC12: IFACE_TYPE_SONET_OC12,
            cls.TYPE_SONET_OC48: IFACE_TYPE_SONET_OC48,
            cls.TYPE_SONET_OC192: IFACE_TYPE_SONET_OC192,
            cls.TYPE_SONET_OC768: IFACE_TYPE_SONET_OC768,
            cls.TYPE_SONET_OC1920: IFACE_TYPE_SONET_OC1920,
            cls.TYPE_SONET_OC3840: IFACE_TYPE_SONET_OC3840,
            cls.TYPE_1GFC_SFP: IFACE_TYPE_1GFC_SFP,
            cls.TYPE_2GFC_SFP: IFACE_TYPE_2GFC_SFP,
            cls.TYPE_4GFC_SFP: IFACE_TYPE_4GFC_SFP,
            cls.TYPE_8GFC_SFP_PLUS: IFACE_TYPE_8GFC_SFP_PLUS,
            cls.TYPE_16GFC_SFP_PLUS: IFACE_TYPE_16GFC_SFP_PLUS,
            cls.TYPE_32GFC_SFP28: IFACE_TYPE_32GFC_SFP28,
            cls.TYPE_128GFC_QSFP28: IFACE_TYPE_128GFC_QSFP28,
            cls.TYPE_INFINIBAND_SDR: IFACE_TYPE_INFINIBAND_SDR,
            cls.TYPE_INFINIBAND_DDR: IFACE_TYPE_INFINIBAND_DDR,
            cls.TYPE_INFINIBAND_QDR: IFACE_TYPE_INFINIBAND_QDR,
            cls.TYPE_INFINIBAND_FDR10: IFACE_TYPE_INFINIBAND_FDR10,
            cls.TYPE_INFINIBAND_FDR: IFACE_TYPE_INFINIBAND_FDR,
            cls.TYPE_INFINIBAND_EDR: IFACE_TYPE_INFINIBAND_EDR,
            cls.TYPE_INFINIBAND_HDR: IFACE_TYPE_INFINIBAND_HDR,
            cls.TYPE_INFINIBAND_NDR: IFACE_TYPE_INFINIBAND_NDR,
            cls.TYPE_INFINIBAND_XDR: IFACE_TYPE_INFINIBAND_XDR,
            cls.TYPE_T1: IFACE_TYPE_T1,
            cls.TYPE_E1: IFACE_TYPE_E1,
            cls.TYPE_T3: IFACE_TYPE_T3,
            cls.TYPE_E3: IFACE_TYPE_E3,
            cls.TYPE_STACKWISE: IFACE_TYPE_STACKWISE,
            cls.TYPE_STACKWISE_PLUS: IFACE_TYPE_STACKWISE_PLUS,
            cls.TYPE_FLEXSTACK: IFACE_TYPE_FLEXSTACK,
            cls.TYPE_FLEXSTACK_PLUS: IFACE_TYPE_FLEXSTACK_PLUS,
            cls.TYPE_JUNIPER_VCP: IFACE_TYPE_JUNIPER_VCP,
            cls.TYPE_SUMMITSTACK: IFACE_TYPE_SUMMITSTACK,
            cls.TYPE_SUMMITSTACK128: IFACE_TYPE_SUMMITSTACK128,
            cls.TYPE_SUMMITSTACK256: IFACE_TYPE_SUMMITSTACK256,
            cls.TYPE_SUMMITSTACK512: IFACE_TYPE_SUMMITSTACK512,
        }.get(slug)


#
# Port type values
#

class PortTypes:
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

    TYPE_CHOICES = (
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

    @classmethod
    def slug_to_integer(cls, slug):
        """
        Provide backward-compatible mapping of the type slug to integer.
        """
        return {
            # Slug: integer
            cls.TYPE_8P8C: PORT_TYPE_8P8C,
            cls.TYPE_110_PUNCH: PORT_TYPE_8P8C,
            cls.TYPE_BNC: PORT_TYPE_BNC,
            cls.TYPE_ST: PORT_TYPE_ST,
            cls.TYPE_SC: PORT_TYPE_SC,
            cls.TYPE_SC_APC: PORT_TYPE_SC_APC,
            cls.TYPE_FC: PORT_TYPE_FC,
            cls.TYPE_LC: PORT_TYPE_LC,
            cls.TYPE_LC_APC: PORT_TYPE_LC_APC,
            cls.TYPE_MTRJ: PORT_TYPE_MTRJ,
            cls.TYPE_MPO: PORT_TYPE_MPO,
            cls.TYPE_LSH: PORT_TYPE_LSH,
            cls.TYPE_LSH_APC: PORT_TYPE_LSH_APC,
        }.get(slug)
