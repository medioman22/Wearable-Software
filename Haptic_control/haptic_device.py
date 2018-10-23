#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:08:06 2018

@author: matteomacchini
"""

import time
import numpy as np
import matplotlib.pyplot as plt



class haptic_device():
    
    
    """
    REMEMBER : ALL class functions have 'self' as a first argument
    """
    
    ### CLASS FUNCTIONS ###
    
    def __init__(self):
        self.motor_number = 9
        self.matteo = 'nice guy !'
        
        self.motor_state = [0, 0, 0,
                            0, 0, 0,
                            0, 0, 0]
        
        
    ### PRIVATE FUNCTIONS ###
    
    # they start with a _
    def _my_patterns_north(self):
        self.motor_control(8, 1)
        self.wait(1)   
        self.motor_control(8, 0)
        self.motor_control(5, 1)
        self.wait(1) 
        self.motor_control(5, 0)
        self.motor_control(2, 1)
    
        
        
        
    ### PUBLIC FUNCTIONS ###
    
    def motor_activation(self, num, duty):
        if duty: print('Motor',num,'switched on with duty of', duty)
        else : print('Motor switched off')
            
    
    # function definition (if it is into a class it's called a METHOD)
    
    
    def motor_control_flat(self, length, duty, direction):
        x_axis1 = [] 
        x_axis2 = []
        x_axis3 = []
        time_axis = []
        self.motor_activation(direction[0],duty)
        x_axis1.append(1)
        x_axis2.append(0)
        x_axis3.append(0)
        time_axis.append(0)
        
        self.wait(length/3)
        self.motor_activation(direction[0],0)
        x_axis1.append(0)
        x_axis2.append(1)
        x_axis3.append(0)
        time_axis.append(length/3)
        
        self.motor_activation(direction[1],duty)
        self.wait(length/3)
        self.motor_activation(direction[1],0)
        x_axis1.append(0)
        x_axis2.append(0)
        x_axis3.append(1)
        time_axis.append(2*length/3)
        self.motor_activation(direction[2],duty)
        self.wait(length/3)
        self.motor_activation(direction[2],0)
        x_axis1.append(0)
        x_axis2.append(0)
        x_axis3.append(0)
        time_axis.append(3*length/3)
        plt.step(time_axis,x_axis1)
        plt.show()
        
    def motor_control_linear(self, length, duty, direction):
        fraction = 10
        for i in range(1,fraction+1):
            self.motor_activation(direction[0],i*duty/fraction)
            self.wait(length/(4*fraction)) #4 is coming from the 4 different phases
        for i in range(1,fraction+1):
            self.motor_activation(direction[0],(fraction-i)*duty/fraction)
            self.motor_activation(direction[1],i*duty/fraction)
            self.wait(length/(4*fraction))
        for i in range(1,fraction+1):
            self.motor_activation(direction[1],(fraction-i)*duty/fraction)
            self.motor_activation(direction[2],i*duty/fraction)
            self.wait(length/(4*fraction))
        for i in range(1,fraction+1):
            self.motor_activation(direction[2],(fraction-i)*duty/fraction)
            self.wait(length/(4*fraction))
            
        
    def motor_control_sinus(self, length, duty, direction):
        print('sinus motor control')
        
        
        
    def impulsion_command(self, length, signalType, duty, direction):
        
        if signalType == 'flat':
            self.motor_control_flat(length,duty,direction)
        elif signalType == 'linear':
            self.motor_control_linear(length,duty,direction)
            print('linear')
        elif signalType == 'sinus':
            self.motor_control_sinus(length, duty, direction)
            print('sinus')
        else: 
            print('Incorrect signal type')
        
        
    def wait(self, sec):
        print('waiting ', str(sec), ' seconds')
        time.sleep(sec)