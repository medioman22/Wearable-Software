# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Configuration file for the Firmware of the Wearable SoftWEAR. PLEASE DO NOT CHANGE AT RUNTIME.
"""

################################################################################
# Pin assignments on the board
"""
             'P8_07':7, 'P8_08':8,
             'P8_09':9, 'P8_10':10, 'P8_11':11, 'P8_12':12, 'P8_14':14, 'P8_15':15,
             'P8_16':16, 'P8_17':17, 'P8_18':18, 'P8_27':27, 'P8_28':28,
             'P8_29':29, 'P8_30':30, 'P8_31':31, 'P8_32':32, 'P8_33':33, 'P8_35':35,
             'P8_39':39, 'P8_40':40, 'P8_41':41, 'P8_42':42, 'P8_43':43, 'P8_44':44,
             'P8_45':45, 'P8_46':46,
             'P9_12':58, 'P9_14':60, 'P9_15':61, 'P9_16':62, 'P9_23':69, 'P9_25':71,
             'P9_27':73, 'P9_41':87
"""
################################################################################

# Layout configuration
LAYOUT = "DevLayout"

################################################################################
# Used I2C addresses
ADDRESSES = []
# I2C MUX TCA9548A
ADDRESSES += [0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77]
# I2C MUX PCA9685
ADDRESSES += [0x40]
# I2C MUX ADS1015
ADDRESSES += [0x48, 0x49]
# I2C MUX BNO055
ADDRESSES += [0x28, 0x29]
################################################################################




################################################################################
# Pin mapping
PIN_MAP = {
    "SCAN": "P9_41",
    "MUX": [
        {
            # Basic
            "A": "P8_43",
            "B": "P8_44",
            "C": "P8_45",
            "DETECT": "P8_46"
        },
        {
            # I2C
            "ADDRESS": 0x70,
            "BUSNUM": 2,
            "DETECT": "P9_15"
        },
        {
            # I2C
            "ADDRESS": 0x71,
            "BUSNUM": 2,
            "DETECT": "P9_15"
        }
    ],

    "INPUT": [
        {
            "DATA": "P8_27",
            "MUX": "P8_29"
        },
        {
            "DATA": "P8_31",
            "MUX": "P8_33"
        }
    ],
    "OUTPUT": [
        # {
        #     "DATA": "USR0"
        # },
        # {
        #     "DATA": "USR1"
        # },
        # {
        #     "DATA": "USR2"
        # },
        # {
        #     "DATA": "USR3"
        # },
        {
            "DATA": "P9_23"
        },
        {
            "DATA": "P9_25"
        },
        {
            "DATA": "P9_27"
        },
        {
            "DATA": "P8_35"
        },
        {
            "DATA": "P8_37"
        },
        {
            "DATA": "P8_39"
        },
        {
            "DATA": "P8_41"
        },
    ],
    "PWM": [
        {
            "DATA": "P9_14",
            "CHANGE_DUTY_FREQUENCY": False
        },
        {
            "DATA": "P9_16",
            "CHANGE_DUTY_FREQUENCY": False
        },
        {
            "DATA": "P8_13",
            "CHANGE_DUTY_FREQUENCY": False
        },
        {
            "DATA": "P8_19",
            "CHANGE_DUTY_FREQUENCY": False
        },
        {
            "DATA": "P9_42",
            "CHANGE_DUTY_FREQUENCY": True
        },
    ],
    "ADC": [
        {
            "DATA": "P9_39",
            "MUX": "P8_28"
        },
        {
            "DATA": "P9_40",
            "MUX": "P8_30"
        },
        {
            "DATA": "P9_33",
            "MUX": "P8_32"
        },
        {
            "DATA": "P9_35",
            "MUX": "P8_34"
        },
        {
            "DATA": "P9_36",
            "MUX": "P8_36"
        },
        {
            "DATA": "P9_37",
            "MUX": "P8_38"
        },
        {
            "DATA": "P9_38",
            "MUX": "P8_40"
        }
    ],
    "I2C": [
        {
            "ADDRESS": 0x40,
            "BUSNUM": 2
        },
        {
            "ADDRESS": 0x28,
            "BUSNUM": 2
        },
        {
            "ADDRESS": 0x29,
            "BUSNUM": 2
        },
        {
            "ADDRESS": 0x48,
            "BUSNUM": 2
        },
    ]

}
################################################################################
