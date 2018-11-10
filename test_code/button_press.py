# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 17:36:16 2018

@author: macchini
"""

import keyboard     #Using module keyboard
import time

def measure_time():
    t_init = time.time()
    
    while True:         #making a loop
        try:            #used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('a'): #if key 'a' is pressed
                t_fin = time.time()
                print('You pressed the A key!')
                print('After ', t_fin - t_init, 's')
                break   #finishing the loop
            else:
                pass
        except:
            break
        
    return t_fin - t_init