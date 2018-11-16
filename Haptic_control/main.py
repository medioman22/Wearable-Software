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
import csv

north = np.array([8,5,2])
south  = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southwest = np.array([10,5,7])
dictOfCorresp = {north[0] : 'N', south[0] : 'S', east[0] : 'E', west[0] : 'W', northeast[0] : 'NE', northwest[0] : 'NW', southeast[0] : 'SE', southwest[0] : 'SW'}


nbOfDirectionSet = 3
nbOfIntensitySet = 1
maxIntensity = 90
maxLength = 1

#initialDirectionList = [north, south]   
initialDirectionList = [north, south, east, west, northwest, northeast, southwest, southeast]
initialIntensityList = [1,2,3,4,5]
intensityList = []

subject = 'Hugo'
    
for i in range(0,nbOfIntensitySet):
    intensityList.extend(initialIntensityList)


random.shuffle(intensityList)


my_device = haptic_device.haptic_device() 
my_device.connection()



def random_direction(nbOfSet = 1,signalType = 'linear', all_motors = False, exp = 'direction', feedbackRequest = True, save = True ) :  
    global initialDirectionList, maxLength, maxIntensity, dictOfCorresp, subject
    directionList = []
    correctDirList = []
    givenDirList = []
    timeList = []
    
    for i in range (0, nbOfSet):
        directionList.extend(initialDirectionList)
        
    random.shuffle(directionList)
    
    for i in range(0, len(directionList)):
        correctDirList.append(dictOfCorresp[directionList[i][0]])
        
    for i in range(0, len(directionList)):
        dirGiven, reactTime = my_device.impulsion_command(direction = directionList[i], 
                        length = maxLength, signalType = signalType, duty = maxIntensity, all_motors = False, realValue = correctDirList[i], 
                        experiment = exp, feedback = feedbackRequest)
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
    if save :  
        with open(subject + '_intens_feedback.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar= '|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Given Direction', 'Real Direction', 'Reaction time'])
            for i in range(0,len(correctDirList)):
                filewriter.writerow([givenDirList[i], correctDirList[i], timeList[i]])
    
def direction_experiment():
    global nbOfDirectionSet
    print('First, you will experiment each direction, and a feedback will be given to you. Press space to activate each direction')
    random_direction(nbOfSet = 1, signalType = 'linear', all_motors = False, exp = 'direction', feedbackRequest = True, save = False)
    print('')
    print('Now the experiment begin, press space to activate each direction')
    random_direction(nbOfSet = nbOfDirectionSet, signalType = 'linear', all_motors = False, exp = 'direction', feedbackRequest = False, save = True) 

def random_intensity(listOfIntensity = intensityList, signalType = 'flat', length = maxLength, exp = 'intensity', feedbackRequest = True ) : 
    correctIntensList = listOfIntensity
    listOfIntensity = [i*maxIntensity/5 for i in listOfIntensity]
    givenIntensList = []
    timeList = []
 
    for i in range(0, len(listOfIntensity)):
        my_device.impulsion_command(north, length, signalType, duty = 60., realValue = correctIntensList[i], experiment = exp,  feedbackRequest = False)
        intensGiven, reactTime = my_device.impulsion_command(north, length, signalType, duty = listOfIntensity[i], realValue = correctIntensList[i], experiment = exp,  feedback = feedbackRequest )
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
Thread(target = direction_experiment).start()
 
#my_device.impulsion_command(south, length = 1, signalType = 'flat', duty = 0)


    