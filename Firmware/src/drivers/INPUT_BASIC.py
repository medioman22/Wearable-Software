# -*- coding: utf-8 -*-
"""
Driver file for the BASIC INPUT. Read the value from a input pin for integrating into
the SoftWEAR package.
"""
#import Adafruit_GPIO.AdafruitBBIOAdapter as AdafruitBBIOAdapter # Main peripheral class. Implements GPIO read out
import Adafruit_BBIO.GPIO as GPIO


class InputBasic:
    """Driver for BASIC INPUT."""

    # Name of the device
    _name = 'INPUT_BASIC'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 1

    # Dimension map of the driver (0-#)
    _dimMap = ['Voltage']

    # Pin
    _pin = None

    # Muxed pin
    _muxedPin = None

    # Settings of the driver
    _settings = {
        'modes': ['State', 'Rising Edge', 'Falling Edge']
    }

    # Mode
    _mode = None


    def __init__(self, pin, muxedPin = None):
        """Device supports a pin."""
        self._pin = pin                                         # Set pin
        self._muxedPin = muxedPin                               # Set muxed pin
        self._mode = self._settings['modes'][0]                 # Set default mode


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        return True                                             # No possibility to check that

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        GPIO.setup(self._pin, GPIO.IN, GPIO.PUD_DOWN)           # Init the pin and set it as input

    def getValues(self):
        """Get values for the basic input."""
        if self._mode == 'State':
            return [GPIO.input(self._pin)]                      # Read the value
        elif self._mode == 'Rising Edge' or self._mode == 'Falling Edge':
            if GPIO.event_detected(self._pin):
                return [1]                                      # Return 1 for event
            return [0]                                          # Return 0 for no event



    def getDevice(self):
        """Return device name."""
        return self._name
    def getName(self):
        """Return device name."""
        if self._muxedPin == None:
            return '{}@Input[{}]'.format(self._name, self._pin)
        else:
            return '{}@Input[{}:{}]'.format(self._name, self._pin, self._muxedPin)
    def getDir(self):
        """Return device direction."""
        return self._dir
    def getDim(self):
        """Return device dimension."""
        return self._dim
    def getDimMap(self):
        """Return device dimension map."""
        return self._dimMap[:]
    def getPin(self):
        """Return device pin."""
        return self._pin
    def getMuxedPin(self):
        """Return device muxed pin."""
        return self._muxedPin
    def getAbout(self):
        """Return device settings."""
        return {'dimMap': self._dimMap[:]}
    def getSettings(self):
        """Return device settings."""
        return self._settings
    def getMode(self):
        """Return device mode."""
        return self._mode

    def setMode(self, mode):
        """Set device mode."""
        if (mode in self._settings['modes']):
            self._mode = mode
            if mode == 'State':
                GPIO.remove_event_detect(self._pin)                 # Remove event detection
            elif mode == 'Rising Edge':
                GPIO.remove_event_detect(self._pin)                 # Remove event detection
                GPIO.add_event_detect(self._pin, GPIO.RISING)       # Set rising edge detection
            elif mode == 'Falling Edge':
                GPIO.remove_event_detect(self._pin)                 # Remove event detection
                GPIO.add_event_detect(self._pin, GPIO.FALLING)      # Set falling edge detection
        else:
            raise ValueError('mode {} is not allowed'.format(mode))
