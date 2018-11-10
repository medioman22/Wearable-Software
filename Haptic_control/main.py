# just a random second comment #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:16:00 2018

@author: matteomacchini
"""

import numpy as np
import haptic_device
import time


north = np.array([8,5,2])
south = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southwest = np.array([10,5,7])

my_device = haptic_device.haptic_device() 
my_device.connection()


#for i in range(0,2):
#    my_device.impulsion_command(southeast, length = 1, signalType = 'flat')
my_device.impulsion_command(south, length = 1, signalType = 'linear', duty = 0)

def random_direction(dir1 = north, dir2 = east, dir3 = west, dir4 = northwest, signalType = 'flat', length = 0.8, duty = 70., all_motors = False) :
    
    my_device.impulsion_command(dir1, length, signalType, duty, all_motors)
    my_device.impulsion_command(dir2, length, signalType, duty, all_motors)
    my_device.impulsion_command(dir3, length, signalType, duty, all_motors)
    my_device.impulsion_command(dir4, length, signalType, duty, all_motors)
    print('What did you feel ?')
    
random_direction()
my_device.impulsion_command(south, length = 1, signalType = 'flat', duty = 0)


    