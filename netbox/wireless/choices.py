from utilities.choices import ChoiceSet


class WirelessRoleChoices(ChoiceSet):
    ROLE_AP = 'ap'
    ROLE_STATION = 'station'

    CHOICES = (
        (ROLE_AP, 'Access point'),
        (ROLE_STATION, 'Station'),
    )


class WirelessChannelChoices(ChoiceSet):

    # 2.4 GHz
    CHANNEL_24G_1 = '2.4g-1-2412-22'
    CHANNEL_24G_2 = '2.4g-2-2417-22'
    CHANNEL_24G_3 = '2.4g-3-2422-22'
    CHANNEL_24G_4 = '2.4g-4-2427-22'
    CHANNEL_24G_5 = '2.4g-5-2432-22'
    CHANNEL_24G_6 = '2.4g-6-2437-22'
    CHANNEL_24G_7 = '2.4g-7-2442-22'
    CHANNEL_24G_8 = '2.4g-8-2447-22'
    CHANNEL_24G_9 = '2.4g-9-2452-22'
    CHANNEL_24G_10 = '2.4g-10-2457-22'
    CHANNEL_24G_11 = '2.4g-11-2462-22'
    CHANNEL_24G_12 = '2.4g-12-2467-22'
    CHANNEL_24G_13 = '2.4g-13-2472-22'

    # 5 GHz
    CHANNEL_5G_32 = '5g-32-5160-20'
    CHANNEL_5G_34 = '5g-34-5170-40'
    CHANNEL_5G_36 = '5g-36-5180-20'
    CHANNEL_5G_38 = '5g-38-5190-40'
    CHANNEL_5G_40 = '5g-40-5200-20'
    CHANNEL_5G_42 = '5g-42-5210-80'
    CHANNEL_5G_44 = '5g-44-5220-20'
    CHANNEL_5G_46 = '5g-46-5230-40'
    CHANNEL_5G_48 = '5g-48-5240-20'
    CHANNEL_5G_50 = '5g-50-5250-160'
    CHANNEL_5G_52 = '5g-52-5260-20'
    CHANNEL_5G_54 = '5g-54-5270-40'
    CHANNEL_5G_56 = '5g-56-5280-20'
    CHANNEL_5G_58 = '5g-58-5290-80'
    CHANNEL_5G_60 = '5g-60-5300-20'
    CHANNEL_5G_62 = '5g-62-5310-40'
    CHANNEL_5G_64 = '5g-64-5320-20'
    CHANNEL_5G_100 = '5g-100-5500-20'
    CHANNEL_5G_102 = '5g-102-5510-40'
    CHANNEL_5G_104 = '5g-104-5520-20'
    CHANNEL_5G_106 = '5g-106-5530-80'
    CHANNEL_5G_108 = '5g-108-5540-20'
    CHANNEL_5G_110 = '5g-110-5550-40'
    CHANNEL_5G_112 = '5g-112-5560-20'
    CHANNEL_5G_114 = '5g-114-5570-160'
    CHANNEL_5G_116 = '5g-116-5580-20'
    CHANNEL_5G_118 = '5g-118-5590-40'
    CHANNEL_5G_120 = '5g-120-5600-20'
    CHANNEL_5G_122 = '5g-122-5610-80'
    CHANNEL_5G_124 = '5g-124-5620-20'
    CHANNEL_5G_126 = '5g-126-5630-40'
    CHANNEL_5G_128 = '5g-128-5640-20'
    CHANNEL_5G_132 = '5g-132-5660-20'
    CHANNEL_5G_134 = '5g-134-5670-40'
    CHANNEL_5G_136 = '5g-136-5680-20'
    CHANNEL_5G_138 = '5g-138-5690-80'
    CHANNEL_5G_140 = '5g-140-5700-20'
    CHANNEL_5G_142 = '5g-142-5710-40'
    CHANNEL_5G_144 = '5g-144-5720-20'
    CHANNEL_5G_149 = '5g-149-5745-20'
    CHANNEL_5G_151 = '5g-151-5755-40'
    CHANNEL_5G_153 = '5g-153-5765-20'
    CHANNEL_5G_155 = '5g-155-5775-80'
    CHANNEL_5G_157 = '5g-157-5785-20'
    CHANNEL_5G_159 = '5g-159-5795-40'
    CHANNEL_5G_161 = '5g-161-5805-20'
    CHANNEL_5G_163 = '5g-163-5815-160'
    CHANNEL_5G_165 = '5g-165-5825-20'
    CHANNEL_5G_167 = '5g-167-5835-40'
    CHANNEL_5G_169 = '5g-169-5845-20'
    CHANNEL_5G_171 = '5g-171-5855-80'
    CHANNEL_5G_173 = '5g-173-5865-20'
    CHANNEL_5G_175 = '5g-175-5875-40'
    CHANNEL_5G_177 = '5g-177-5885-20'

    CHOICES = (
        (
            '2.4 GHz (802.11b/g/n/ax)',
            (
                (CHANNEL_24G_1, '1 (2412 MHz)'),
                (CHANNEL_24G_2, '2 (2417 MHz)'),
                (CHANNEL_24G_3, '3 (2422 MHz)'),
                (CHANNEL_24G_4, '4 (2427 MHz)'),
                (CHANNEL_24G_5, '5 (2432 MHz)'),
                (CHANNEL_24G_6, '6 (2437 MHz)'),
                (CHANNEL_24G_7, '7 (2442 MHz)'),
                (CHANNEL_24G_8, '8 (2447 MHz)'),
                (CHANNEL_24G_9, '9 (2452 MHz)'),
                (CHANNEL_24G_10, '10 (2457 MHz)'),
                (CHANNEL_24G_11, '11 (2462 MHz)'),
                (CHANNEL_24G_12, '12 (2467 MHz)'),
                (CHANNEL_24G_13, '13 (2472 MHz)'),
            )
        ),
        (
            '5 GHz (802.11a/n/ac/ax)',
            (
                (CHANNEL_5G_32, '32 (5160/20 MHz)'),
                (CHANNEL_5G_34, '34 (5170/40 MHz)'),
                (CHANNEL_5G_36, '36 (5180/20 MHz)'),
                (CHANNEL_5G_38, '38 (5190/40 MHz)'),
                (CHANNEL_5G_40, '40 (5200/20 MHz)'),
                (CHANNEL_5G_42, '42 (5210/80 MHz)'),
                (CHANNEL_5G_44, '44 (5220/20 MHz)'),
                (CHANNEL_5G_46, '46 (5230/40 MHz)'),
                (CHANNEL_5G_48, '48 (5240/20 MHz)'),
                (CHANNEL_5G_50, '50 (5250/160 MHz)'),
                (CHANNEL_5G_52, '52 (5260/20 MHz)'),
                (CHANNEL_5G_54, '54 (5270/40 MHz)'),
                (CHANNEL_5G_56, '56 (5280/20 MHz)'),
                (CHANNEL_5G_58, '58 (5290/80 MHz)'),
                (CHANNEL_5G_60, '60 (5300/20 MHz)'),
                (CHANNEL_5G_62, '62 (5310/40 MHz)'),
                (CHANNEL_5G_64, '64 (5320/20 MHz)'),
                (CHANNEL_5G_100, '100 (5500/20 MHz)'),
                (CHANNEL_5G_102, '102 (5510/40 MHz)'),
                (CHANNEL_5G_104, '104 (5520/20 MHz)'),
                (CHANNEL_5G_106, '106 (5530/80 MHz)'),
                (CHANNEL_5G_108, '108 (5540/20 MHz)'),
                (CHANNEL_5G_110, '110 (5550/40 MHz)'),
                (CHANNEL_5G_112, '112 (5560/20 MHz)'),
                (CHANNEL_5G_114, '114 (5570/160 MHz)'),
                (CHANNEL_5G_116, '116 (5580/20 MHz)'),
                (CHANNEL_5G_118, '118 (5590/40 MHz)'),
                (CHANNEL_5G_120, '120 (5600/20 MHz)'),
                (CHANNEL_5G_122, '122 (5610/80 MHz)'),
                (CHANNEL_5G_124, '124 (5620/20 MHz)'),
                (CHANNEL_5G_126, '126 (5630/40 MHz)'),
                (CHANNEL_5G_128, '128 (5640/20 MHz)'),
                (CHANNEL_5G_132, '132 (5660/20 MHz)'),
                (CHANNEL_5G_134, '134 (5670/40 MHz)'),
                (CHANNEL_5G_136, '136 (5680/20 MHz)'),
                (CHANNEL_5G_138, '138 (5690/80 MHz)'),
                (CHANNEL_5G_140, '140 (5700/20 MHz)'),
                (CHANNEL_5G_142, '142 (5710/40 MHz)'),
                (CHANNEL_5G_144, '144 (5720/20 MHz)'),
                (CHANNEL_5G_149, '149 (5745/20 MHz)'),
                (CHANNEL_5G_151, '151 (5755/40 MHz)'),
                (CHANNEL_5G_153, '153 (5765/20 MHz)'),
                (CHANNEL_5G_155, '155 (5775/80 MHz)'),
                (CHANNEL_5G_157, '157 (5785/20 MHz)'),
                (CHANNEL_5G_159, '159 (5795/40 MHz)'),
                (CHANNEL_5G_161, '161 (5805/20 MHz)'),
                (CHANNEL_5G_163, '163 (5815/160 MHz)'),
                (CHANNEL_5G_165, '165 (5825/20 MHz)'),
                (CHANNEL_5G_167, '167 (5835/40 MHz)'),
                (CHANNEL_5G_169, '169 (5845/20 MHz)'),
                (CHANNEL_5G_171, '171 (5855/80 MHz)'),
                (CHANNEL_5G_173, '173 (5865/20 MHz)'),
                (CHANNEL_5G_175, '175 (5875/40 MHz)'),
                (CHANNEL_5G_177, '177 (5885/20 MHz)'),
            )
        ),
    )
