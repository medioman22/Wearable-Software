# -*- coding: utf-8 -*-
"""
Driver file for the BASIC INPUT. Read the value from a input pin for integrating into
the SoftWEAR package.
"""
#import Adafruit_GPIO.AdafruitBBIOAdapter as AdafruitBBIOAdapter # Main peripheral class. Implements GPIO read out
import Adafruit_BBIO.GPIO as GPIO
import threading                                                # Threading class for the threads
import time                                                     # Required for controllng the sampling period

from MuxModule import Mux                                       # SoftWEAR MUX module.

# Create a MUX shadow instance as there is only one Mux
MuxShadow = Mux()


class InputBasic:
    """Driver for BASIC INPUT."""

    # Name of the device
    _name = 'INPUT_BASIC'

    # Info of the device
    _info = 'Basic Input device reading digital voltage values on a single pin. Optional multiplexing available.'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 1

    # Dimension map of the driver (0-#)
    _dimMap = ['Voltage']

    # Dimension unit of the driver (0-#)
    _dimUnit = ['V']

    # Pin
    _pin = None

    # Muxed pin
    _muxedPin = None

    # Settings of the driver
    _settings = {
        'frequencies': [],
        'modes': ['State', 'Rising Edge', 'Falling Edge']
    }

    # Data type of values
    _dataType = 'On/Off'

    # Data range for values
    _dataRange = [0,1]

    # Value to set
    _currentValue = 0

    # Value history
    _values = None

    # Mode
    _mode = None

    # Duty frequency
    _dutyFrequency = None

    # Flags
    _flags = None

    # Period for the thread
    _period = 0.1

    # Thread active flag
    _threadActive = False

    # Thread for the inner loop
    _thread = None


    def __init__(self, pin, muxedPin = None):
        """Device supports a pin."""
        self._pin = pin                                         # Set pin
        self._muxedPin = muxedPin                               # Set muxed pin
        self._values = []                                       # Set empty values array
        self._mode = self._settings['modes'][0]                 # Set default mode
        self._flags = []                                        # Set default flag list

    def cleanup(self):
        """Clean up driver when no longer needed."""
        self._threadActive = False                              # Unset thread active flag


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        return True                                             # No possibility to check that

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        GPIO.setup(self._pin, GPIO.IN, GPIO.PUD_DOWN)           # Init the pin and set it as input
        self._threadActive = True                               # Set thread active flag
        self._thread = threading.Thread(target=self._loop, name=self._name) # Create thread
        self._thread.daemon = True                              # Set thread as daemonic
        self._thread.start()                                    # Start thread

    def _loop(self):
        """Inner loop of the driver."""
        while True:
            beginT = time.time()                                # Save start time of loop cycle

            if self._mode == 'State':
                if (self._muxedPin != None):
                    MuxShadow.activate(self._muxedPin)          # Activate mux pin
                self._currentValue = GPIO.input(self._pin)      # Read the value
                if (self._muxedPin != None):
                    MuxShadow.deactivate()                      # Deactivate mux
            elif self._mode == 'Rising Edge' or self._mode == 'Falling Edge':
                if GPIO.event_detected(self._pin):
                    self._currentValue = 1                      # Return 1 for event
                else:
                    self._currentValue = 0                      # Return 0 for no event

            self._values.append([time.time(), [self._currentValue]]) # Save timestamp and value

            endT = time.time()                                  # Save start time of loop cycle
            deltaT = endT - beginT                              # Calculate time used for loop cycle
            if (deltaT < self._period):
                time.sleep(self._period - deltaT)               # Sleep until next loop period

            if not self._threadActive:                          # Stop the thread
                return

    def getValues(self, clear=True):
        """Get values for the basic input device."""
        if self._values == None:                                # Return empty array for no values
            return []
        values = self._values[:]                                # Get the values
        if clear:
            self._values = []                                   # Reset values
        return values                                           # Return the values



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
        return {
            'info': self._info,
            'dimMap': self._dimMap[:],
            'dimUnit': self._dimUnit[:],
            'dataType': self._dataType,
            'dataRange': self._dataRange[:]
        }
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

    def getFlags(self):
        """Return device mode."""
        return self._flags[:]

    def getFlag(self, flag):
        """Return device mode."""
        return self._flags[flag]

    def setFlag(self, flag, value):
        """Set device flag."""
        raise ValueError('flag {} is not allowed'.format(flag))

    def getDutyFrequency(self):
        """Return device duty frequency."""
        return self._dutyFrequency

    def setDutyFrequency(self, dutyFrequency):
        """Set device duty frequency."""
        raise ValueError('duty frequency {} is not allowed'.format(dutyFrequency))
