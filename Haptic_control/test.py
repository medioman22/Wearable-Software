#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 15:45:31 2019

@author: matteomacchini
"""

"""
Created on Tue Oct 16 10:08:06 2018
@author: matteomacchini
"""


import time
#from pyqtgraph.Qt import QtGui
#import pyqtgraph as pg
import json
import sys

import os,sys
sys.path.insert(1, os.path.join(sys.path[0], '../Interface/src'))

from connections.beagleboneGreenWirelessConnection import BeagleboneGreenWirelessConnection



c = BeagleboneGreenWirelessConnection()

I2C_interface = "PCA9685@I2C[64,2]"

c.connect()
print('Status: {}'.format(c.getState()))
c.sendMessages([json.dumps({"type": "Settings", "name": I2C_interface, "dutyFrequency": '50 Hz'})])
time.sleep(3)
c.sendMessages([json.dumps({"type": "Settings", "name": I2C_interface, "scan": False})])


c.sendMessages([json.dumps({"dim":  0, "value": 0, "type": "Set", "name": I2C_interface})])
