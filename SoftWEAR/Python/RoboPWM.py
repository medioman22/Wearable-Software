# -*- coding: utf-8 -*-
"""
SoftWEAR PWM module. Provides PWM read and write functionality for configured 
PWM channels.
"""

import mraa      # # Main peripheral class. Implements basic PWM functions
import logging   # This class logs all info - so logging is imported

# Translation between normal ADC inexes and the ones that mraa uses
idx2mraa = {0:13, 1:19, 2:34, 3:36, 4:67, 5:68, 6:74, 7:88}

# Translation between string IDs and normal ADC indexes (to be translated to MRAA)
str2idx = {'P8_13':0, 'P8_19':1, 'P8_34':2, 'P8_36':3, 
           'P9_21':4, 'P9_22':5, 'P9_28':6, 'P9_42':7}

class RoboPWM:
    def __init__(self):
        """ Class constructor. Initializes the logger and the mraa pwm objects. """
        # Configure the logger
        self._logger = logging.getLogger('RoboPWM')
        self._logger.setLevel(logging.INFO) # Only INFO level or above will be saved
        fh = logging.FileHandler('RoboPWM.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)           # Only INFO level or above will be saved
        self._logger.addHandler(fh)
        
        self._pin_objects = []              # Init mraa object list
        for pin in self.WRITE_PINS:         # Go through all the configured PWM channels
            # Validate the PWM channel pin and obtain the required indexes
            scan_idx, mraa_idx = self.validate_pin(pin)
            if scan_idx is -1 or mraa_idx is -1:
                self._logger.error("Init Error: PWM pin " + str(pin) + " is not valid!")
                raise ValueError("Init Error: pin scan list is incorrect!")
            x = mraa.Pwm(mraa_idx)          # Create PWM object
            x.period_us(1000)               # Set period to 1ms 
            x.enable(True)                  # Enable PWM
            x.write(0)                      # Init PWM with 0
            self._logger.info("PWM pin " + str(pin) + " successfully initialized!")
            self._pin_objects.append(x)     # Add mraa object to list
    
    def __del__(self):
        logging.shutdown()
    
    def validate_pin(self, pin):
        """ Returns scan_idx, mraa_idx if succesful, -1, -1 if not. 
            The scan_idx is the pin index in the class write list.
            The mraa_idx is the pin number used by the mraa library. """
        idx = None
        try:    # Parse the input parameter
            if isinstance(pin, str):
                idx = str2idx[pin]          # Pin is in string format -> use dict
        except KeyError:                    # Key error means it's not in str2idx dict.
            return -1, -1
        
        if not idx and isinstance(pin, int):
            idx = pin                       # If pin is already a number, save it
        
        if idx is None:                     # If we don't have a index by now -> error
            return -1, -1
            
        try:
            mraa_idx = idx2mraa[idx]        # Convert index to mraa index
        except KeyError:                    # Key error -> pin is not mraa PWM pin 
            return -1, -1
        
        try:                                # Get the scan index from the class write list
            scan_idx = self.WRITE_PINS.index(idx)            
        except ValueError:                  # Value Error -> pin not in class write list
            return -1, mraa_idx
        
        return scan_idx, mraa_idx
    
    def write_pin(self, pin, value):
        """ Writes the specified duty cycle in % (0-100) to the given PWM pin channel """
        scan_idx, mraa_idx = self.validate_pin(pin)
        if scan_idx is -1 or mraa_idx is -1:
            raise ValueError("Runtime Error: pin is incorrect or not available!")
        self._pin_objects[scan_idx].write(value/100.0)
        self._logger.info("PWM pin " + str(pin) + " written with " + str(value/100.0))
    
    def get_all_values(self):
        """ Returns a list of dictionaries in the form {'chn', 'val'} containing
            all PWM channel duty cycle values. """
        ret = []                        # Initialize return object to empty list
        for pin in self.WRITE_PINS:     # Go through all pin channels
            # Obtain the mraa & write index. Needed for the mraa read function
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
    