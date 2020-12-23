# -*- coding: utf-8 -*-
# Author: Salar Rahimi
# Date: November 2020
"""
Driver file for the BASIC PWM. Set the value of a pwm pin for integrating into the SoftWEAR package.
Update for Debian 10.3
"""
import Adafruit_BBIO.PWM as PWM
import threading                                                # Threading class for the threads
import time                                                     # Required for controllng the sampling period

class PWMBasic:
    """Driver for BASIC PWM."""

    # Name of the device
    _name = 'PWM_BASIC'

    # Info of the device
    _info = 'Basic PWM device driving a PWM-Signal on a single pin.'

    # Direction of the driver (in/out)
    _dir = 'out'

    # Dimension of the driver (0-#)
    _dim = 1

    # Dimension map of the driver (0-#)
    _dimMap = ['Duty']

    # Dimension units of the driver (0-#)
    _dimUnit = ['%']

    # Pin
    _pin = None

    # Settings of the driver
    _settings = {
        'dutyFrequencies': [
            '10 Hz',
            '20 Hz',
            '30 Hz',
            '40 Hz',
            '50 Hz',
            '60 Hz',
            '100 Hz',
            '120 Hz',
            '150 Hz',
            '200 Hz',
            '250 Hz',
            '300 Hz',
            '400 Hz',
            '500 Hz',
            '1000 Hz',
            '1500 Hz',
            '2000 Hz'
        ],
        'flags': ['INVERSE_PARITY'],
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
    _dataType = 'Range'

    # Data range for values
    _dataRange = [0,100]

    # Value to set
    _currentValue = 0.

    # Value history
    _values = []

    # Flag whether the values needs to be updated
    _update = True

    # Mode
    _mode = None

    # Duty frequency
    _dutyFrequency = None

    # Flags
    _flags = None

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

    # Duration needed for an update cycle
    _changeDutyFrequency = None


    def __init__(self, pin, changeDutyFrequency):
        """Device supports a pin."""
        self._pin = pin                                         # Set pin
        self._values = []                                       # Set empty values array
        self._dutyFrequency = self._settings['dutyFrequencies'][-1] # Set default duty frequency
        self._flags = []                                        # Set default flag list
        self._changeDutyFrequency = changeDutyFrequency         # Test if change duty frequency is available



    def cleanup(self):
        """Clean up driver when no longer needed."""
        self._threadActive = False                              # Unset thread active flag
        PWM.stop(self._pin)                                     # Stop PWM


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        return True                                             # No possibility to check that

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        PWM.start(self._pin, self._currentValue, int(self._dutyFrequency[:-3])) # Init the pin and set it as pwm
        self._threadActive = True                               # Set thread active flag
        self._thread = threading.Thread(target=self._loop, name=self._name) # Create thread
        self._thread.daemon = True                              # Set thread as daemonic
        self._thread.start()                                    # Start thread

    def _loop(self):
        """Inner loop of the driver."""
        while True:
            beginT = time.time()                                # Save start time of loop cycle

            if self._update:
                if 'INVERSE_PARITY' in self._flags:             # Check for parity flag
                    PWM.set_duty_cycle(self._pin, 100. - self._currentValue) # Set duty cycle
                else:
                    PWM.set_duty_cycle(self._pin, self._currentValue) # Set duty cycle
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
        """Get values for the basic pwm device."""
        if self._values == None:                                # Return empty array for no values
            return []
        values = self._values[:]                                # Get the values
        if clear:
            self._values = []                                   # Reset values
        return values                                           # Return the values

    def setValue(self, dim, value):
        """Set values for the basic pwm device."""
        self._currentValue = min(100., max(0., value))          # Get the value and update the current value of the driver
                                                                # Value is limited to range [0,100]
        self._update = True                                     # Raise update flag

    def getDevice(self):
        """Return device name."""
        return self._name

    def getName(self):
        """Return device name."""
        return '{}@PWM[{}]'.format(self._name, self._pin)

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
        settings = self._settings
        if not self._changeDutyFrequency:                       # Test if change duty frequency is available
            settings = dict(settings)
            settings.pop('dutyFrequencies', None)

        return settings

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
        if (flag in self._settings['flags']):
            if value:
                self._flags.append(flag)                            # Add the flag
            else:
                self._flags.remove(flag)                            # Remove the flag
            self._update = True                                     # Raise update flag
        else:
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
        if (dutyFrequency in self._settings['dutyFrequencies']):
            self._dutyFrequency = dutyFrequency
            PWM.set_frequency(self._pin, int(self._dutyFrequency[:-3])) # Set the duty frequency
            self._update = True                                     # Raise update flag
        else:
            raise ValueError('duty frequency {} is not allowed'.format(dutyFrequency))
