# -*- coding: utf-8 -*-
"""
"""

import mraa
import logging

# Translation between normal ADC inexes and the ones that mraa uses
idx2mraa = {0:13, 1:19, 2:34, 3:36, 4:67, 5:68, 6:74, 7:88}

# Translation between string IDs and normal ADC indexes (to be translated to MRAA)
str2idx = {'P8_13':0, 'P8_19':1, 'P8_34':2, 'P8_36':3, 
           'P9_21':4, 'P9_22':5, 'P9_28':6, 'P9_42':7}

class RoboPWM:
    def __init__(self):
        # Configure the logger
        self._logger = logging.getLogger('RoboPWM')
        self._logger.setLevel(logging.INFO)
        fh = logging.FileHandler('RoboPWM.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        self._logger.addHandler(fh)
        
        self._pin_objects = []
        for pin in self.WRITE_PINS:
            scan_idx, mraa_idx = self.validate_pin(pin)
            if scan_idx is -1 or mraa_idx is -1:
                self._logger.error("Init Error: PWM pin " + str(pin) + " is not valid!")
                raise ValueError("Init Error: pin scan list is incorrect!")
            x = mraa.Pwm(mraa_idx)
            x.period_us(1000)
            x.enable(True)
            x.write(0)
            self._logger.info("PWM pin " + str(pin) + " successfully initialized!")
            self._pin_objects.append(x)
    
    def __del__(self):
        logging.shutdown()
    
    def validate_pin(self, pin):
        """ Returns scan_idx, mraa_idx if succesful, -1, -1 if not"""
        idx = None
        try:    # Parse the input parameter
            if isinstance(pin, str):
                idx = str2idx[pin]      # Pin is in string format -> use dict
        except KeyError:       
            return -1, -1
        
        if not idx and isinstance(pin, int):
            idx = pin                   # If pin is already a number, save it
        
        if idx is None:     # If we don't have a index by now -> error
            return -1, -1
            
        try:
            mraa_idx = idx2mraa[idx]    # Convert index to mraa index
        except KeyError:
            return -1, -1
        
        try:            # Get the scan index from the 
            scan_idx = self.WRITE_PINS.index(idx)            
        except ValueError:
            return -1, mraa_idx
        
        return scan_idx, mraa_idx
    
    def write_pin(self, pin, value):
        scan_idx, mraa_idx = self.validate_pin(pin)
        if scan_idx is -1 or mraa_idx is -1:
            raise ValueError("Runtime Error: pin is incorrect or not available!")
        self._pin_objects[scan_idx].write(value/100.0)
        self._logger.info("PWM pin " + str(pin) + " written with " + str(value/100.0))
    
    def get_all_values(self):
        ret = []
        for pin in self.WRITE_PINS:
            scan_idx, mraa_idx = self.validate_pin(pin)
            ret.append({'chn':pin, 'val':self._pin_objects[scan_idx].read()})
            self._logger.info("PWM pin " + str(pin) + " read with value " + str(self._pin_objects[scan_idx].read()))
        return ret
    
    
    """ List of scan pins to be initialized. SHOULD BE CONSTAT THROUGHT EXECUTION """
    WRITE_PINS = [0, 1]
    
    """ List of all initialized pin objects. Created from the list of scan pins. """
    _pin_objects = []
    
    """ Logger object used by the class to create the log file """
    _logger = logging.getLogger('RoboPWM')
    