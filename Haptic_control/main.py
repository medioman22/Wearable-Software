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
#import math

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
lowestIntensity = 20

maxLength = 1.2

initialDirectionList = [north, south, east, west, northwest, northeast, southwest, southeast]
initialIntensityList = [1,2,3,4,5]

linear = 'linear'
flat = 'flat'
direction = 'direction'
intensity = 'intensity'
intensity_and_length = 'intensity_and_length'
guidance = 'guidance'

subject = 'Rokalito'
signalTypeExp = linear
experimentTypeChosen = guidance

#my_device = haptic_device.haptic_device() 
#my_device.connection()




def guidanceExperiment():
    distance_acquisition()

def experiment(experimentType = experimentTypeChosen, signalType = signalTypeExp):
    global nbOfSet
    print('First, you will train each ', experimentType, ' and a feedback will be given to you. Press space to activate each ', experimentType)
    random_set(nbOfSet = nbOfSetForTrain, exp = experimentType, feedbackRequest = True, save = True, signalType = signalTypeExp)
    print('')
    print('Now the experiment begin ', experimentType)
    random_set(nbOfSet = nbOfSetForTest, exp = experimentType, feedbackRequest = False, save = True, signalType = signalTypeExp )


def random_set(nbOfSet = 1, exp = 'direction', feedbackRequest = True, save = True, signalType = 'linear'):
    global initialDirectionList, initialIntensityList, maxLength, maxIntensity, dictOfCorresp, subject, savingPath, lowestIntensity, counter
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
            valueGiven, reactTime = my_device.impulsion_command(direction = valueList[i], length = maxLength, 
                                        signalType = signalTypeExp, duty = maxIntensity, all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = True, feedbackReturned = feedbackRequest)
        elif exp == 'intensity' :
           my_device.impulsion_command(direction = north, length = maxLength, 
                                        signalType = signalTypeExp, duty = 60., all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = False, feedbackReturned = False)
           time.sleep(1)
           valueGiven, reactTime = my_device.impulsion_command(direction = north, length = maxLength, 
                                        signalType = signalTypeExp, duty = valueList[i], all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = True, feedbackReturned = feedbackRequest)
        elif exp == 'intensity_and_length' :
           my_device.impulsion_command(direction = north, length = maxLength, 
                                        signalType = signalTypeExp, duty = 60., all_motors = False, realValue = correctList[i], 
                                        experiment = exp, feedbackAsked = False, feedbackReturned = False)
           signalLength = maxLength - (correctList[i]-3)/2*maxLength*0.3
           time.sleep(1)
           valueGiven, reactTime = my_device.impulsion_command(direction = north, length = signalLength, 
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
        with open(savingPath + subject + '_' + exp + signalTypeExp+ '_feedback' + str(counter) +'.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar= '|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Given ' + exp, 'Real '+ exp, 'Reaction time'])
            for i in range(0,len(correctList)):
                filewriter.writerow([givenList[i], correctList[i], timeList[i]])
        counter = counter+1
    
#def random_intensity_changing_length(listOfIntensity = intensityList, signalType = 'flat', length = maxLength) :
#    for i in range(0, len(listOfIntensity)):
#        my_device.impulsion_command(north, i/len(listOfIntensity)*length, signalType, listOfIntensity[i],  feedbackRequest = True)
        

def distance_acquisition():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 36000
    
    many_data = 1000000     # this is abuot 55 minutes of acquisition with 3 markers
                            # (increase for longer acquisition time)
    correction = [None] * many_data
    
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    
    count = 0
    
    #while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("acquired marker data, counter = ", count)
    
    strs = 'ffffffffffffff'
    
    data_ump = struct.unpack(strs, data)
    
    corr = data_ump[-2:]
    
    rollDistance = corr[0]
    pitchDistance = corr[1]
#    angle = math.atan(pitchDistance/rollDistance)
    correction[count] = np.array(corr)
    
    print(corr)
    
    count = count + 1       
    
#Thread(target = my_device.measure_time).start()        
if(experimentTypeChosen == guidance):
    guidanceExperiment()
    #    Thread(target = guidanceExperiment).start()
else :  Thread(target = experiment).start()
 


    