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
import time
import socket
import struct
import math

rollDistance = 0
pitchDistance = 0
savingPath = 'C:\\Users\\Hugo\\Documents\\GitHub\\Wearable-Software\\Haptic_control\\logs\\'
north = np.array([8,5,2])
south  = np.array([2,5,8])
east = np.array([4,5,6])
west = np.array([6,5,4])
northwest = np.array([9,5,1])
northeast = np.array([7,5,10])
southeast = np.array([1,5,9])
southwest = np.array([10,5,7])

dictOfCorresp = {north[0] : 'N', south[0] : 'S', east[0] : 'E', west[0] : 'W', northeast[0] : 'NE', northwest[0] : 'NW', southeast[0] : 'SE', southwest[0] : 'SW'}

counter = 0
nbOfSetForTrain = 2 
nbOfSetForTest = 4 
maxIntensity = 99
lowestIntensity = 40

moyLength = 1. 

initialDirectionList = [north, south, east, west, northwest, northeast, southwest, southeast]
initialIntensityList = [1,2,3,4,5]

linear = 'linear'
flat = 'flat'
direction = 'direction'
intensity = 'intensity'
intensity_and_length = 'intensity_and_length'
guidance = 'guidance'

subject = 'test'
signalTypeExp = linear

experimentTypeChosen = guidance

#experimentTypeChosen = direction

my_device = haptic_device.haptic_device() 
my_device.connection()


#my_device.impulsion_command_guidance(direction = east,length = 2, duty = 0)

def guidanceExperiment():
    global moyLength
    while True :
        rawAngle, rawRadius = distances_acquisition()
        if rawAngle != None : 
            rawAngle = math.pi/2
            rawRadius = 101
            angle = quarter_attribution(rawAngle)
            print(angle)
            radius = intensity_attribution(rawRadius)
            motorIntens = (radius)*(maxIntensity-lowestIntensity)/5 + lowestIntensity
            print(motorIntens)
            signalLength = moyLength - (radius-3)/2*moyLength*0.4
            print(signalLength)
    #        my_device.impulsion_command_guidance(direction = east,length = 2, duty = 99)
            my_device.impulsion_command_guidance(direction = angle,length = signalLength, duty = motorIntens)
            time.sleep(0.5)
        else : print('Waiting for datas')


def experiment(experimentType = experimentTypeChosen, signalType = signalTypeExp):
    global nbOfSet
    print('First, you will train each ', experimentType, ' and a feedback will be given to you. Press space to activate each ', experimentType)
    random_set(nbOfSet = nbOfSetForTrain, exp = experimentType, feedbackRequest = True, save = True, signalType = signalTypeExp)
    print('')
    print('Now the experiment begin ', experimentType)
    random_set(nbOfSet = nbOfSetForTest, exp = experimentType, feedbackRequest = False, save = True, signalType = signalTypeExp )


def random_set(nbOfSet = 1, exp = 'direction', feedbackRequest = True, save = True, signalType = 'linear'):
    global initialDirectionList, initialIntensityList, moyLength, maxIntensity, dictOfCorresp, subject, savingPath, lowestIntensity, counter
    valueList = []
    correctList = []
    givenList = []
    timeList = []
    signalTypeExp = signalType
    
    for i in  range(0, nbOfSet): 
        if exp == 'direction' : valueList.extend(initialDirectionList)
        elif exp == 'intensity_and_length' or 'intensity': valueList.extend(initialIntensityList)
        else :
            print('wrong experiment type')
            break
    random.shuffle(valueList)
    
    for i in range(0, len(valueList)): 
        if exp == 'direction' : correctList.append(dictOfCorresp[valueList[i][0]])
        elif exp == 'intensity_and_length' or exp == 'intensity' : correctList = valueList
        else : print('wrong experiment type')
   
    
    if exp == 'intensity_and_length' or exp == 'intensity' : valueList = [(i-1)*(maxIntensity-lowestIntensity)/(len(initialIntensityList)-1) + lowestIntensity for i in valueList]
    
    for i in range(0, len(valueList)):
        if exp == 'direction' :
            valueGiven, reactTime = my_device.impulsion_command(direction = valueList[i], length = moyLength, 
                                        signalType = signalTypeExp, duty = maxIntensity, all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = True, feedbackReturned = feedbackRequest)
        elif exp == 'intensity' :
           my_device.impulsion_command(direction = east, length = moyLength, 
                                        signalType = signalTypeExp, duty = 60., all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = False, feedbackReturned = False)
           time.sleep(1)
           valueGiven, reactTime = my_device.impulsion_command(direction = east, length = moyLength, 
                                        signalType = signalTypeExp, duty = valueList[i], all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = True, feedbackReturned = feedbackRequest)
        elif exp == 'intensity_and_length' :
           my_device.impulsion_command(direction = east, length = moyLength, 
                                        signalType = signalTypeExp, duty = 60., all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = False, feedbackReturned = False)
           signalLength = moyLength - (correctList[i]-3)/2*moyLength*0.4
           time.sleep(1)
           valueGiven, reactTime = my_device.impulsion_command(direction = east, length = signalLength, 
                                        signalType = signalTypeExp, duty = valueList[i], all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = True, feedbackReturned = feedbackRequest)
        else : print('wrong experiment type')
        givenList.append(valueGiven)
        timeList.append(reactTime)
    print('Thanks for the feedback')
    print('')
    print('The real ', exp,' where :')
    print(correctList)
    print('Youre answers were :')
    print(givenList)
    print('with the corresponding reaction time :')
    print(timeList)
    if save : 
        with open(savingPath + subject + '_' + exp + signalTypeExp + '_feedback' + str(counter) +'.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar= '|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Given ' + exp, 'Real '+ exp, 'Reaction time'])
            for i in range(0,len(correctList)):
                filewriter.writerow([givenList[i], correctList[i], timeList[i]])
        counter = counter + 1
    
def quarter_attribution(angle):
    PI_8 = math.pi/8
    if angle < 3*PI_8 and angle > PI_8:
        direction = northeast
    if angle < 5*PI_8 and angle > 3*PI_8:
        direction = north
    if angle < 7*PI_8 and angle > 5*PI_8:
        direction = northwest
    if angle < 9*PI_8 and angle > 7*PI_8:
        direction = west
    if angle < 11*PI_8 and angle > 9*PI_8:
        direction = southwest
    if angle < 13*PI_8 and angle > 11*PI_8:
        direction = south
    if angle < 15*PI_8 and angle > 13*PI_8:
        direction = southeast
    if angle < PI_8 and angle > 15*PI_8:
        direction = east       
    return direction

def intensity_attribution(radius):
    IntensityThreshold = 100
    if radius > IntensityThreshold:
        motorIntens = 5
    elif radius >3*IntensityThreshold/4 :
        motorIntens = 4
    elif radius >2*IntensityThreshold/4 :
        motorIntens = 3
    elif radius >1*IntensityThreshold/4 :
        motorIntens = 2
    else :
        motorIntens = 1
    return motorIntens

def distances_acquisition():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 36000    
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    strs = 'ffffffffffffff'    
    data_ump = struct.unpack(strs, data)
    
    corr = data_ump[-2:]
    
    rollDistance = corr[0]
    pitchDistance = corr[1]
    
    angle = math.atan(pitchDistance/rollDistance)
    radius = math.sqrt(math.pow(rollDistance,2) + math.pow(pitchDistance,2))

    return angle, radius       
            
if(experimentTypeChosen == guidance):
    guidanceExperiment()
else :  
    Thread(target = experiment).start()
    Thread(target = my_device.measure_time).start()
 


    