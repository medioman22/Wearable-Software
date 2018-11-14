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
south  = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southwest = np.array([10,5,7])
dictOfCorresp = {north[0] : 'N', south[0] : 'S', east[0] : 'E', west[0] : 'W', northeast[0] : 'NE', northwest[0] : 'NW', southeast[0] : 'SE', southwest[0] : 'SW'}


nbOfDirectionSet = 1
nbOfIntensitySet = 1
maxIntensity = 90
maxLength = 1.5

initialDirectionList = [north, south, east, west, northwest, northeast, southwest, southeast]
directionList = []
initialIntensityList = [1,2,3,4,5]
intensityList = []

for i in range (0, nbOfDirectionSet):
    directionList.extend(initialDirectionList)
    
for i in range(0,nbOfIntensitySet):
    intensityList.extend(initialIntensityList)

random.shuffle(directionList)
random.shuffle(intensityList)


my_device = haptic_device.haptic_device() 
my_device.connection()


def random_direction(listOfDirection = directionList, signalType = '', length = maxLength, duty = maxIntensity, all_motors = False, exp = 'direction') :  
    correctDirList = []
    givenDirList = []
    timeList = []
    for i in range(0, len(listOfDirection)):
        correctDirList.append(dictOfCorresp[listOfDirection[i][0]])
    for i in range(0, len(listOfDirection)):
        dirGiven, reactTime = my_device.impulsion_command(listOfDirection[i], length, signalType, duty, all_motors, realValue = correctDirList[i], experiment = exp, feedbackRequest = True )
        givenDirList.append(dirGiven)
        timeList.append(reactTime)
    print('Thanks for the feedback')
    print('')
    print('The real directions where :')
    print(correctDirList)
    print('Youre answers were :')
    print(givenDirList)
    print('with the corresponding reaction time :')
    print(timeList)
    

def random_intensity(listOfIntensity = intensityList, signalType = 'flat', length = maxLength, exp = 'intensity') : 
    correctIntensList = listOfIntensity
    listOfIntensity = [i*maxIntensity/5 for i in listOfIntensity]
    givenIntensList = []
    timeList = []
 
    for i in range(0, len(listOfIntensity)):
        my_device.impulsion_command(north, length, signalType, duty = 60., realValue = correctIntensList[i], experiment = exp,  feedbackRequest = False)
        intensGiven, reactTime = my_device.impulsion_command(north, length, signalType, duty = listOfIntensity[i], realValue = correctIntensList[i], experiment = exp,  feedbackRequest = True)
        givenIntensList.append(intensGiven)
        timeList.append(reactTime)
    print('Thanks for the feedback')
    print('')
    print('The real intensities where :')
    print(correctIntensList)
    print('Youre answers were :')
    print(givenIntensList)
    print('with the corresponding reaction time :')
    print(timeList)
        
def random_intensity_changing_length(listOfIntensity = intensityList, signalType = 'flat', length = maxLength) :
    for i in range(0, len(listOfIntensity)):
        my_device.impulsion_command(north, i/len(listOfIntensity)*length, signalType, listOfIntensity[i],  feedbackRequest = True)
        
        
        
Thread(target = haptic_device.measure_time).start()        
Thread(target = random_intensity).start()
 
#my_device.impulsion_command(south, length = 1, signalType = 'flat', duty = 0)


    