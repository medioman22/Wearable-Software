# -*- coding: utf-8 -*-
"""
SoftWEAR Utility module. Add here all inter-module utility functionality.

    Provides the translation between the port pins as presented on the
    BeagleBoard and the mraa indexes. This is strictly for GPIO pins not
    used in any other peripheral. When designing functionalities that require
    GPIO only use pins from this list!
"""

# Use the below version if the eMMC is enabled and the P8 pins are not available
gpio2mraa = {'P8_07':7, 'P8_08':8,
             'P8_09':9, 'P8_10':10, 'P8_11':11, 'P8_12':12, 'P8_14':14, 'P8_15':15,
             'P8_16':16, 'P8_17':17, 'P8_18':18, 'P8_27':27, 'P8_28':28,
             'P8_29':29, 'P8_30':30, 'P8_31':31, 'P8_32':32, 'P8_33':33, 'P8_35':35,
             'P8_39':39, 'P8_40':40, 'P8_41':41, 'P8_42':42, 'P8_43':43, 'P8_44':44,
             'P8_45':45, 'P8_46':46,
             'P9_12':58, 'P9_14':60, 'P9_15':61, 'P9_16':62, 'P9_23':69, 'P9_25':71,
             'P9_27':73, 'P9_41':87}

# Use the below version if the eMMC is disabled (and the P8 pins are available)
"""gpio2mraa = {'P8_03':3, 'P8_04':4, 'P8_05':5, 'P8_06':6, 'P8_07':7, 'P8_08':8,
             'P8_09':9, 'P8_10':10, 'P8_11':11, 'P8_12':12, 'P8_14':14, 'P8_15':15,
             'P8_16':16, 'P8_17':17, 'P8_18':18, 'P8_20':20, 'P8_21':21, 'P8_22':22,
             'P8_23':23, 'P8_24':24, 'P8_25':25, 'P8_26':26, 'P8_27':27, 'P8_28':28,
             'P8_29':29, 'P8_30':30, 'P8_31':31, 'P8_32':32, 'P8_33':33, 'P8_35':35,
             'P8_39':39, 'P8_40':40, 'P8_41':41, 'P8_42':42, 'P8_43':43, 'P8_44':44,
             'P8_45':45, 'P8_46':46,
             'P9_12':58, 'P9_14':60, 'P9_15':61, 'P9_16':62, 'P9_23':69, 'P9_25':71,
             'P9_27':73, 'P9_41':87 } """

class UsedGPIO:
    """
    Provides a list of used GPIO.

    Use this to detect any GPIO usage conflicts in the SoftWEAR package (e.g. same pin used more than once).
    """

    pin_list = []
