# just a random second comment #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:16:00 2018

@author: Hugo kohli
"""

import numpy as np
import haptic_device
import threading
from threading import Thread
import random

north = np.array([8,5,2])
south = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southwest = np.array([10,5,7])
dictOfCorresp = {north[0] : 'N', south[0] : 'S', east[0] : 'E', west[0] : 'W', northeast[0] : 'NE', northwest[0] : 'NW', southeast[0] : 'SE', southwest[0] : 'SW'}


nbOfDirectionSet = 2
nbOfIntensitySet = 5
maxIntensity = 80
maxLength = 0.8

initialDirectionList = [north, south, east, west, northwest, northeast, southwest, southeast]
directionList = []
initialIntensityList = [0.2,0.4,0.6,0.8,1.]
intensityList = []

for i in range (0, nbOfDirectionSet):
    directionList.extend(initialDirectionList)
    
for i in range(0,nbOfIntensitySet):
    intensityList.extend(initialIntensityList)

random.shuffle(directionList)
random.shuffle(intensityList)
intensityList = [i*maxIntensity for i in intensityList]


my_device = haptic_device.haptic_device() 
my_device.connection()


def random_direction(listOfDirection = directionList, signalType = 'flat', length = maxLength, duty = maxIntensity, all_motors = False) :  
    correctDirList = []
    for i in range(0, len(listOfDirection)):
        my_device.impulsion_command(listOfDirection[i], length, signalType, duty, all_motors)
    print('Thanks for the feedback')
    for i in range(0, len(listOfDirection)):
        correctDirList.append(dictOfCorresp[listOfDirection[i][0]])
    print('The real direction where :')
    print(correctDirList)
    
    

def random_intensity(listOfIntensity = intensityList, signalType = 'flat', length = maxLength) :
    for i in range(0, len(listOfIntensity)):
        my_device.impulsion_command(north, length, signalType, listOfIntensity[i])
    
    
        
def random_intensity_changing_length(listOfIntensity = intensityList, signalType = 'flat', length = maxLength) :
    for i in range(0, len(listOfIntensity)):
        my_device.impulsion_command(north, i/len(listOfIntensity)*length, signalType, listOfIntensity[i])
        
        
Thread(target = random_direction).start()

#my_device.impulsion_command(south, length = 1, signalType = 'flat', duty = 0)


    