# -*- coding: utf-8 -*-
"""
Driver file for the BASIC INPUT.Read the value from a input pin for integrating into
the SoftWEAR package.
"""
#import Adafruit_GPIO.AdafruitBBIOAdapter as AdafruitBBIOAdapter # Main peripheral class. Implements GPIO read out
import Adafruit_BBIO.GPIO as GPIO
import time                                                     # Imported for delay reasons

# Adapter for BBGW
# GPIO = AdafruitBBIOAdapter()

class InputBasic:
    """Driver for BASIC INPUT."""

    # Name of the device
    _name = 'BASIC_INPUT'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 1

    # Pin
    _pin = None

    # Muxed pin
    _muxedPin = None


    def __init__(self, pin, muxedPin = None):
        """Device supports a pin."""
        self._pin = pin
        self._muxedPin = muxedPin


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        return True                                             # No possibility to check that

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        GPIO.setup(self._pin, GPIO.IN, GPIO.PUD_DOWN)           # Init the pin and set it as input
        return

    def getValues(self):
        """Get values for the basic input."""
        return [GPIO.input(self._pin)]                          # Read the value


    def getDevice(self):
        """Return device name."""
        return self._name
    def getDir(self):
        """Return device direction."""
        return self._dir
    def getDim(self):
        """Return device dimension."""
        return self._dim
    def getPin(self):
        """Return device pin."""
        return self._pin
    def getMuxedPin(self):
        """Return device muxed pin."""
        return self._muxedPin
