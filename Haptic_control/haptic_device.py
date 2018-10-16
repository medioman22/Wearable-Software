#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 16 10:08:06 2018

@author: matteomacchini
"""

import time


class haptic_device():
    
    """
    REMEMBER : ALL class functions have 'self' as a first argument
    """
    
    ### CLASS FUNCTIONS ###
    
    def __init__(self):
        self.motor_number = 9
        self.matteo = 'nice guy'
        
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
    
    def pattern(self, style):
        if style == 'north':
            self._my_patterns_north()
        else:
            print('I don''t know this style')
            
    
    # function definition (if it is into a class it's called a METHOD)
    def motor_control(self, num, duty):
        self.motor_state[num] = duty
        print('activated motor # ', str(num), ' with duty cycle = ', str(duty))
              
    def wait(self, sec):
        print('waiting ', str(sec), ' seconds')
        time.sleep(sec)
        