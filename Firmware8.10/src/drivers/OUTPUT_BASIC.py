# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Driver file for the BASIC OUTPUT. Set the value of a output pin for integrating into the SoftWEAR package.
"""
import Adafruit_BBIO.GPIO as GPIO
import threading                                                # Threading class for the threads
import time                                                     # Required for controllng the sampling period


class OutputBasic:
    """Driver for BASIC OUTPUT."""

    # Name of the device
    _name = 'OUTPUT_BASIC'

    # Info of the device
    _info = 'Basic Output device driving a On/Off-Signal on a single pin.'

    # Direction of the driver (in/out)
    _dir = 'out'

    # Dimension of the driver (0-#)
    _dim = 1

    # Dimension map of the driver (0-#)
    _dimMap = ['Voltage']

    # Dimension unit of the driver (0-#)
    _dimUnit = ['V']

    # Pin
    _pin = None

    # Settings of the driver
    _settings = {
        'frequencies': [
            '1 Hz',
            '2 Hz',
            '3 Hz',
            '4 Hz',
            '5 Hz',
            '6 Hz',
            '10 Hz',
            '20 Hz',
            '30 Hz',
            '40 Hz',
            '50 Hz',
            '60 Hz',
            '100 Hz'
        ]
    }

    # Data type of values
    _dataType = 'On/Off'

    # Data range for values
    _dataRange = [0,1]

    # Value to set
    _currentValue = 0

    # Mode
    _mode = None

    # Duty frequency
    _dutyFrequency = None

    # Flags
    _flags = None

    # Value history
    _values = []

    # Flag whether the values needs to be updated
    _update = True

    # Frequency for the thread
    _frequency = '10 Hz'

    # Period for the thread
    _period = 0.1

    # Thread active flag
    _threadActive = False

    # Thread for the inner loop
    _thread = None

    # Duration needed for an update cycle
    _cycleDuration = 0


    def __init__(self, pin):
        """Device supports a pin."""
        self._pin = pin                                         # Set pin
        self._values = []                                       # Set empty values array
        self._flags = []                                        # Set default flag list

    def cleanup(self):
        """Clean up driver when no longer needed."""
        self._threadActive = False                              # Unset thread active flag


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        return True                                             # No possibility to check that

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        GPIO.setup(self._pin, GPIO.OUT)                         # Init the pin and set it as output
        GPIO.output(self._pin, GPIO.LOW)                        # Set default to low
        self._threadActive = True                               # Set thread active flag
        self._thread = threading.Thread(target=self._loop, name=self._name) # Create thread
        self._thread.daemon = True                              # Set thread as daemonic
        self._thread.start()                                    # Start thread

    def _loop(self):
        """Inner loop of the driver."""
        while True:
            beginT = time.time()                                # Save start time of loop cycle

            if self._update:
                if self._currentValue == 1:                     # Set output to HIGH
                    GPIO.output(self._pin, GPIO.HIGH)
                else:                                           # Set output to LOW
                    GPIO.output(self._pin, GPIO.LOW)
                self._update = False
            self._values.append([time.time(), [self._currentValue]]) # Save timestamp and value

            endT = time.time()                                  # Save start time of loop cycle
            deltaT = endT - beginT                              # Calculate time used for loop cycle
            self._cycleDuration = deltaT                        # Save time needed for a cycle
            if (deltaT < self._period):
                time.sleep(self._period - deltaT)               # Sleep until next loop period

            if not self._threadActive:                          # Stop the thread
                return

    def getValues(self, clear=True):
        """Get values for the basic output device."""
        if self._values == None:                                # Return empty array for no values
            return []
        values = self._values[:]                                # Get the values
        if clear:
            self._values = []                                   # Reset values
        return values                                           # Return the values

    def setValue(self, dim, value):
        """Set values for the basic output device."""
        self._currentValue = value                              # Get the value and update the current value of the driver
        self._update = True                                     # Raise update flag

    def getDevice(self):
        """Return device name."""
        return self._name

    def getName(self):
        """Return device name."""
        return '{}@Output[{}]'.format(self._name, self._pin)

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

    def getCycleDuration(self):
        """Return device cycle duration."""
        return self._cycleDuration

    def getMode(self):
        """Return device mode."""
        return self._mode

    def setMode(self, mode):
        """Set device mode."""
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

    def getFrequency(self):
        """Return device frequency."""
        return self._frequency

    def setFrequency(self, frequency):
        """Set device frequency."""
        if (frequency in self._settings['frequencies']):
            self._frequency = frequency
            self._period = 1./int(self._frequency[:-3])
        else:
            raise ValueError('frequency {} is not allowed'.format(frequency))

    def getDutyFrequency(self):
        """Return device duty frequency."""
        return self._dutyFrequency

    def setDutyFrequency(self, dutyFrequency):
        """Set device duty frequency."""
        raise ValueError('duty frequency {} is not allowed'.format(dutyFrequency))
