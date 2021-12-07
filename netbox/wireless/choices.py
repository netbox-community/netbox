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
    
    # 6 GHz
    CHANNEL_6G_1 = '6g-1-5955-20'
    CHANNEL_6G_3 = '6g-3-5955-40'
    CHANNEL_6G_5 = '6g-5-5965-20'
    CHANNEL_6G_7 = '6g-7-5975-80'
    CHANNEL_6G_9 = '6g-9-5985-20'
    CHANNEL_6G_11 = '6g-11-5995-40'
    CHANNEL_6G_13 = '6g-13-6005-20'
    CHANNEL_6G_15 = '6g-15-6015-160'
    CHANNEL_6G_17 = '6g-17-6025-20'
    CHANNEL_6G_19 = '6g-19-6035-40'
    CHANNEL_6G_21 = '6g-21-6045-20'
    CHANNEL_6G_23 = '6g-23-6055-80'
    CHANNEL_6G_25 = '6g-25-6065-20'
    CHANNEL_6G_28 = '6g-28-6080-40'
    CHANNEL_6G_29 = '6g-29-6085-20'
    CHANNEL_6G_31 = '6g-31-6095-320'
    CHANNEL_6G_33 = '6g-33-6105-20'
    CHANNEL_6G_36 = '6g-36-6120-40'
    CHANNEL_6G_37 = '6g-37-6125-20'
    CHANNEL_6G_39 = '6g-39-6135-80'
    CHANNEL_6G_41 = '6g-41-6145-20'
    CHANNEL_6G_44 = '6g-44-6160-40'
    CHANNEL_6G_45 = '6g-45-6165-20'
    CHANNEL_6G_47 = '6g-47-6175-160'
    CHANNEL_6G_49 = '6g-49-6185-20'
    CHANNEL_6G_52 = '6g-52-6200-40'
    CHANNEL_6G_53 = '6g-53-6205-20'
    CHANNEL_6G_55 = '6g-55-6215-80'
    CHANNEL_6G_57 = '6g-57-6225-20'
    CHANNEL_6G_60 = '6g-60-6240-40'
    CHANNEL_6G_61 = '6g-61-6245-20'
    CHANNEL_6G_65 = '6g-65-6265-20'
    CHANNEL_6G_68 = '6g-68-6280-40'
    CHANNEL_6G_69 = '6g-69-6285-20'
    CHANNEL_6G_71 = '6g-71-6295-80'
    CHANNEL_6G_73 = '6g-73-6305-20'
    CHANNEL_6G_76 = '6g-76-6320-40'
    CHANNEL_6G_77 = '6g-77-6325-20'
    CHANNEL_6G_79 = '6g-79-6335-160'
    CHANNEL_6G_81 = '6g-81-6345-20'
    CHANNEL_6G_84 = '6g-84-6360-40'
    CHANNEL_6G_85 = '6g-85-6365-20'
    CHANNEL_6G_87 = '6g-87-6375-80'
    CHANNEL_6G_89 = '6g-89-6385-20'
    CHANNEL_6G_92 = '6g-92-6400-40'
    CHANNEL_6G_93 = '6g-93-6405-20'
    CHANNEL_6G_95 = '6g-95-6415-320'
    CHANNEL_6G_97 = '6g-97-6425-20'
    CHANNEL_6G_100 = '6g-100-6440-40'
    CHANNEL_6G_101 = '6g-101-6445-20'
    CHANNEL_6G_103 = '6g-103-6455-80'
    CHANNEL_6G_105 = '6g-105-6465-20'
    CHANNEL_6G_108 = '6g-108-6480-40'
    CHANNEL_6G_109 = '6g-109-6485-20'
    CHANNEL_6G_111 = '6g-111-6495-160'
    CHANNEL_6G_113 = '6g-113-6505-20'
    CHANNEL_6G_116 = '6g-116-6520-40'
    CHANNEL_6G_117 = '6g-117-6525-20'
    CHANNEL_6G_119 = '6g-119-6535-80'
    CHANNEL_6G_121 = '6g-121-6545-20'
    CHANNEL_6G_124 = '6g-124-6560-40'
    CHANNEL_6G_125 = '6g-125-6565-20'
    CHANNEL_6G_129 = '6g-129-6585-20'
    CHANNEL_6G_132 = '6g-132-6600-40'
    CHANNEL_6G_133 = '6g-133-6605-20'
    CHANNEL_6G_135 = '6g-135-6615-80'
    CHANNEL_6G_137 = '6g-137-6625-20'
    CHANNEL_6G_140 = '6g-140-6640-40'
    CHANNEL_6G_141 = '6g-141-6645-20'
    CHANNEL_6G_143 = '6g-143-6655-160'
    CHANNEL_6G_145 = '6g-145-6665-20'
    CHANNEL_6G_148 = '6g-148-6680-40'
    CHANNEL_6G_149 = '6g-149-6685-20'
    CHANNEL_6G_151 = '6g-151-6695-80'
    CHANNEL_6G_153 = '6g-153-6705-20'
    CHANNEL_6G_156 = '6g-156-6720-40'
    CHANNEL_6G_157 = '6g-157-6725-20'
    CHANNEL_6G_159 = '6g-159-6735-320'
    CHANNEL_6G_161 = '6g-161-6745-20'
    CHANNEL_6G_164 = '6g-164-6760-40'
    CHANNEL_6G_165 = '6g-165-6765-20'
    CHANNEL_6G_167 = '6g-167-6775-80'
    CHANNEL_6G_169 = '6g-169-6785-20'
    CHANNEL_6G_172 = '6g-172-6800-40'
    CHANNEL_6G_173 = '6g-173-6805-20'
    CHANNEL_6G_175 = '6g-175-6815-160'
    CHANNEL_6G_177 = '6g-177-6825-20'
    CHANNEL_6G_180 = '6g-180-6840-40'
    CHANNEL_6G_181 = '6g-181-6845-20'
    CHANNEL_6G_183 = '6g-183-6855-80'
    CHANNEL_6G_185 = '6g-185-6865-20'
    CHANNEL_6G_188 = '6g-188-6880-40'
    CHANNEL_6G_189 = '6g-189-6885-20'
    CHANNEL_6G_193 = '6g-193-6905-20'
    CHANNEL_6G_196 = '6g-196-6920-40'
    CHANNEL_6G_197 = '6g-197-6925-20'
    CHANNEL_6G_199 = '6g-199-6935-80'
    CHANNEL_6G_201 = '6g-201-6945-20'
    CHANNEL_6G_204 = '6g-204-6960-40'
    CHANNEL_6G_205 = '6g-205-6965-20'
    CHANNEL_6G_207 = '6g-207-6975-160'
    CHANNEL_6G_209 = '6g-209-6985-20'
    CHANNEL_6G_212 = '6g-212-7000-40'
    CHANNEL_6G_213 = '6g-213-7005-20'
    CHANNEL_6G_215 = '6g-215-7015-80'
    CHANNEL_6G_217 = '6g-217-7025-20'
    CHANNEL_6G_220 = '6g-220-7040-40'
    CHANNEL_6G_221 = '6g-221-7045-20'
    CHANNEL_6G_225 = '6g-225-7065-20'
    CHANNEL_6G_228 = '6g-228-7080-40'
    CHANNEL_6G_229 = '6g-229-7085-20'
    CHANNEL_6G_233 = '6g-233-7105-20'

    
    # 60 GHz
    CHANNEL_60G_1 = '60g-1-58320-2160'
    CHANNEL_60G_2 = '60g-2-60480-2160'
    CHANNEL_60G_3 = '60g-3-62640-2160'
    CHANNEL_60G_4 = '60g-4-64800-2160'
    CHANNEL_60G_5 = '60g-5-66960-2160'
    CHANNEL_60G_6 = '60g-6-69120-2160'
    CHANNEL_60G_9 = '60g-9-59400-4320'
    CHANNEL_60G_10 = '60g-10-61560-4320'
    CHANNEL_60G_11 = '60g-11-63720-4320'
    CHANNEL_60G_12 = '60g-12-65880-4320'
    CHANNEL_60G_13 = '60g-13-68040-4320'
    CHANNEL_60G_17 = '60g-17-60480-6480'
    CHANNEL_60G_18 = '60g-18-62640-6480'
    CHANNEL_60G_19 = '60g-19-64800-6480'
    CHANNEL_60G_20 = '60g-20-66960-6480'
    CHANNEL_60G_25 = '60g-25-61560-6480'
    CHANNEL_60G_26 = '60g-26-63720-6480'
    CHANNEL_60G_27 = '60g-27-65880-6480'
    


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
        (
            '6 GHz (802.11ax)',
            (
                (CHANNEL_6G_1, '1 (5945/20 MHz)'),
                (CHANNEL_6G_3, '3 (5955/40 MHz)'),
                (CHANNEL_6G_5, '5 (5965/20 MHz)'),
                (CHANNEL_6G_7, '7 (5975/80 MHz)'),
                (CHANNEL_6G_9, '9 (5985/20 MHz)'),
                (CHANNEL_6G_11, '11 (5995/40 MHz)'),
                (CHANNEL_6G_13, '13 (6005/20 MHz)'),
                (CHANNEL_6G_15, '15 (6015/160 MHz)'),
                (CHANNEL_6G_17, '17 (6025/20 MHz)'),
                (CHANNEL_6G_19, '19 (6035/40 MHz)'),
                (CHANNEL_6G_21, '21 (6045/20 MHz)'),
                (CHANNEL_6G_23, '23 (6055/80 MHz)'),
                (CHANNEL_6G_25, '25 (6065/20 MHz)'),
                (CHANNEL_6G_28, '28 (6080/40 MHz)'),
                (CHANNEL_6G_29, '29 (6085/20 MHz)'),
                (CHANNEL_6G_31, '31 (6095/320 MHz)'),
                (CHANNEL_6G_33, '33 (6105/20 MHz)'),
                (CHANNEL_6G_36, '36 (6120/40 MHz)'),
                (CHANNEL_6G_37, '37 (6125/20 MHz)'),
                (CHANNEL_6G_39, '39 (6135/80 MHz)'),
                (CHANNEL_6G_41, '41 (6145/20 MHz)'),
                (CHANNEL_6G_44, '44 (6160/40 MHz)'),
                (CHANNEL_6G_45, '45 (6165/20 MHz)'),
                (CHANNEL_6G_47, '47 (6175/160 MHz)'),
                (CHANNEL_6G_49, '49 (6185/20 MHz)'),
                (CHANNEL_6G_52, '52 (6200/40 MHz)'),
                (CHANNEL_6G_53, '53 (6205/20 MHz)'),
                (CHANNEL_6G_55, '55 (6215/80 MHz)'),
                (CHANNEL_6G_57, '57 (6225/20 MHz)'),
                (CHANNEL_6G_60, '60 (6240/40 MHz)'),
                (CHANNEL_6G_61, '61 (6245/20 MHz)'),
                (CHANNEL_6G_65, '65 (6265/20 MHz)'),
                (CHANNEL_6G_68, '68 (6280/40 MHz)'),
                (CHANNEL_6G_69, '69 (6285/20 MHz)'),
                (CHANNEL_6G_71, '71 (6295/80 MHz)'),
                (CHANNEL_6G_73, '73 (6305/20 MHz)'),
                (CHANNEL_6G_76, '76 (6320/40 MHz)'),
                (CHANNEL_6G_77, '77 (6325/20 MHz)'),
                (CHANNEL_6G_79, '79 (6335/160 MHz)'),
                (CHANNEL_6G_81, '81 (6345/20 MHz)'),
                (CHANNEL_6G_84, '84 (6360/40 MHz)'),
                (CHANNEL_6G_85, '85 (6365/20 MHz)'),
                (CHANNEL_6G_87, '87 (6375/80 MHz)'),
                (CHANNEL_6G_89, '89 (6385/20 MHz)'),
                (CHANNEL_6G_92, '92 (6400/40 MHz)'),
                (CHANNEL_6G_93, '93 (6405/20 MHz)'),
                (CHANNEL_6G_95, '95 (6415/320 MHz)'),
                (CHANNEL_6G_97, '97 (6425/20 MHz)'),
                (CHANNEL_6G_100, '100 (6440/40 MHz)'),
                (CHANNEL_6G_101, '101 (6445/20 MHz)'),
                (CHANNEL_6G_103, '103 (6455/80 MHz)'),
                (CHANNEL_6G_105, '105 (6465/20 MHz)'),
                (CHANNEL_6G_108, '108 (6480/40 MHz)'),
                (CHANNEL_6G_109, '109 (6485/20 MHz)'),
                (CHANNEL_6G_111, '111 (6495/160 MHz)'),
                (CHANNEL_6G_113, '113 (6505/20 MHz)'),
                (CHANNEL_6G_116, '116 (6520/40 MHz)'),
                (CHANNEL_6G_117, '117 (6525/20 MHz)'),
                (CHANNEL_6G_119, '119 (6535/80 MHz)'),
                (CHANNEL_6G_121, '121 (6545/20 MHz)'),
                (CHANNEL_6G_124, '124 (6560/40 MHz)'),
                (CHANNEL_6G_125, '125 (6565/20 MHz)'),
                (CHANNEL_6G_129, '129 (6585/20 MHz)'),
                (CHANNEL_6G_132, '132 (6600/40 MHz)'),
                (CHANNEL_6G_133, '133 (6605/20 MHz)'),
                (CHANNEL_6G_135, '135 (6615/80 MHz)'),
                (CHANNEL_6G_137, '137 (6625/20 MHz)'),
                (CHANNEL_6G_140, '140 (6640/40 MHz)'),
                (CHANNEL_6G_141, '141 (6645/20 MHz)'),
                (CHANNEL_6G_143, '143 (6655/160 MHz)'),
                (CHANNEL_6G_145, '145 (6665/20 MHz)'),
                (CHANNEL_6G_148, '148 (6680/40 MHz)'),
                (CHANNEL_6G_149, '149 (6685/20 MHz)'),
                (CHANNEL_6G_151, '151 (6695/80 MHz)'),
                (CHANNEL_6G_153, '153 (6705/20 MHz)'),
                (CHANNEL_6G_156, '156 (6720/40 MHz)'),
                (CHANNEL_6G_157, '157 (6725/20 MHz)'),
                (CHANNEL_6G_159, '159 (6735/320 MHz)'),
                (CHANNEL_6G_161, '161 (6745/20 MHz)'),
                (CHANNEL_6G_164, '164 (6760/40 MHz)'),
                (CHANNEL_6G_165, '165 (6765/20 MHz)'),
                (CHANNEL_6G_167, '167 (6775/80 MHz)'),
                (CHANNEL_6G_169, '169 (6785/20 MHz)'),
                (CHANNEL_6G_172, '172 (6800/40 MHz)'),
                (CHANNEL_6G_173, '173 (6805/20 MHz)'),
                (CHANNEL_6G_175, '175 (6815/160 MHz)'),
                (CHANNEL_6G_177, '177 (6825/20 MHz)'),
                (CHANNEL_6G_180, '180 (6840/40 MHz)'),
                (CHANNEL_6G_181, '181 (6845/20 MHz)'),
                (CHANNEL_6G_183, '183 (6855/80 MHz)'),
                (CHANNEL_6G_185, '185 (6865/20 MHz)'),
                (CHANNEL_6G_188, '188 (6880/40 MHz)'),
                (CHANNEL_6G_189, '189 (6885/20 MHz)'),
                (CHANNEL_6G_193, '193 (6905/20 MHz)'),
                (CHANNEL_6G_196, '196 (6920/40 MHz)'),
                (CHANNEL_6G_197, '197 (6925/20 MHz)'),
                (CHANNEL_6G_199, '199 (6935/80 MHz)'),
                (CHANNEL_6G_201, '201 (6945/20 MHz)'),
                (CHANNEL_6G_204, '204 (6960/40 MHz)'),
                (CHANNEL_6G_205, '205 (6965/20 MHz)'),
                (CHANNEL_6G_207, '207 (6975/160 MHz)'),
                (CHANNEL_6G_209, '209 (6985/20 MHz)'),
                (CHANNEL_6G_212, '212 (7000/40 MHz)'),
                (CHANNEL_6G_213, '213 (7005/20 MHz)'),
                (CHANNEL_6G_215, '215 (7015/80 MHz)'),
                (CHANNEL_6G_217, '217 (7025/20 MHz)'),
                (CHANNEL_6G_220, '220 (7040/40 MHz)'),
                (CHANNEL_6G_221, '221 (7045/20 MHz)'),
                (CHANNEL_6G_225, '225 (7065/20 MHz)'),
                (CHANNEL_6G_228, '228 (7080/40 MHz)'),
                (CHANNEL_6G_229, '229 (7085/20 MHz)'),
                (CHANNEL_6G_233, '233 (7105/20 MHz)'),

            )
        ),
        (
            '60 GHz (802.11ad/ay)',
            (
                (CHANNEL_60G_1, '1 (58.32/2.16 GHz)'),
                (CHANNEL_60G_2, '2 (60.48/2.16 GHz)'),
                (CHANNEL_60G_3, '3 (62.64/2.16 GHz)'),
                (CHANNEL_60G_4, '4 (64.80/2.16 GHz)'),
                (CHANNEL_60G_5, '5 (66.96/2.16 GHz)'),
                (CHANNEL_60G_6, '6 (69.12/2.16 GHz)'),
                (CHANNEL_60G_9, '9 (59.40/4.32 GHz)'),
                (CHANNEL_60G_10, '10 (61.56/4.32 GHz)'),
                (CHANNEL_60G_11, '11 (63.72/4.32 GHz)'),
                (CHANNEL_60G_12, '12 (65.88/4.32 GHz)'),
                (CHANNEL_60G_13, '13 (68.04/4.32 GHz)'),
                (CHANNEL_60G_17, '17 (60.48/6.48 GHz)'),
                (CHANNEL_60G_18, '18 (62.64/6.48 GHz)'),
                (CHANNEL_60G_19, '19 (64.80/6.48 GHz)'),
                (CHANNEL_60G_20, '20 (66.96/6.48 GHz)'),
                (CHANNEL_60G_25, '25 (61.56/8.64 GHz)'),
                (CHANNEL_60G_26, '26 (63.72/8.64 GHz)'),
                (CHANNEL_60G_27, '27 (65.88/8.64 GHz)'),
            )
        ),
    )


class WirelessAuthTypeChoices(ChoiceSet):
    TYPE_OPEN = 'open'
    TYPE_WEP = 'wep'
    TYPE_WPA_PERSONAL = 'wpa-personal'
    TYPE_WPA_ENTERPRISE = 'wpa-enterprise'

    CHOICES = (
        (TYPE_OPEN, 'Open'),
        (TYPE_WEP, 'WEP'),
        (TYPE_WPA_PERSONAL, 'WPA Personal (PSK)'),
        (TYPE_WPA_ENTERPRISE, 'WPA Enterprise'),
    )


class WirelessAuthCipherChoices(ChoiceSet):
    CIPHER_AUTO = 'auto'
    CIPHER_TKIP = 'tkip'
    CIPHER_AES = 'aes'

    CHOICES = (
        (CIPHER_AUTO, 'Auto'),
        (CIPHER_TKIP, 'TKIP'),
        (CIPHER_AES, 'AES'),
    )
