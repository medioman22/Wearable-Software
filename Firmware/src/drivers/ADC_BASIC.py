# -*- coding: utf-8 -*-
"""
Driver file for the BASIC ADC. Read the value from a analog pin for integrating into
the SoftWEAR package.
"""
#import Adafruit_GPIO.AdafruitBBIOAdapter as AdafruitBBIOAdapter # Main peripheral class. Implements GPIO read out
import Adafruit_BBIO.ADC as ADC
import threading                                                # Threading class for the threads
import time                                                     # Required for controllng the sampling period

from MuxModule import Mux                                       # SoftWEAR MUX module.

# Create a MUX shadow instance as there is only one Mux
MuxShadow = Mux()

# Timeout device
TIMEOUT_TICKS = 10
TIMEOUT_ENABLED = True
TIMEOUT_THRESHOLD = 0.005

class ADCBasic:
    """Driver for BASIC ADC."""

    # Name of the device
    _name = 'ADC_BASIC'

    # Info of the device
    _info = 'Basic ADC device reading analog voltage values on a single pin. Optional multiplexing available.'

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

    # Zero counter
    _zeroCounter = 0

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
        ],
        'modes': ['Auto Detection', 'Manual Detection']
    }

    # Data type of values
    _dataType = 'Range'

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


    def __init__(self, pin, muxedPin = None):
        """Device supports a pin."""
        self._pin = pin                                         # Set pin
        self._muxedPin = muxedPin                               # Set muxed pin
        self._zeroCounter = 0                                   # Set zero counter to 0
        self._mode = self._settings['modes'][0]                 # Set default mode
        self._flags = []                                        # Set default flag list
        self._values = []                                       # Set empty values array
        ADC.setup()                                             # Enable ADC readings

    def cleanup(self):
        """Clean up driver when no longer needed."""
        self._threadActive = False                              # Unset thread active flag


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        if not TIMEOUT_ENABLED:                                 # Check if flag to deconnect inactive devices is set
            return True

        # BUG: Due to a bug in the ADC driver, read the values 2 times to get the most recent
        if (self._muxedPin != None):
            MuxShadow.activate(self._muxedPin)                  # Activate mux pin
        ADC.read(self._pin)
        if (self._muxedPin != None):
            MuxShadow.deactivate()                              # Deactivate mux

        if self._mode == 'Auto Detection':                      # Got for >0 detection
            if (self._muxedPin != None):
                MuxShadow.activate(self._muxedPin)              # Activate mux pin
            currentValueZero = ADC.read(self._pin) < TIMEOUT_THRESHOLD # Check if current value is different to zero
            if (self._muxedPin != None):
                MuxShadow.deactivate()                          # Deactivate mux
            pastValuesZero = self._zeroCounter < TIMEOUT_TICKS  # Check if past values are constant zero

            return not (currentValueZero and pastValuesZero)    # Return False to deconnect device
        elif self._mode == 'Manual Detection':                  # Connected anyway
            return True

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        self._threadActive = True                               # Set thread active flag
        self._thread = threading.Thread(target=self._loop, name=self._name) # Create thread
        self._thread.daemon = True                              # Set thread as daemonic
        self._thread.start()                                    # Start thread

    def _loop(self):
        """Inner loop of the driver."""
        while True:
            beginT = time.time()                                # Save start time of loop cycle

            # BUG: Due to a bug in the ADC driver, read the values 2 times to get the most recent
            if (self._muxedPin != None):
                MuxShadow.activate(self._muxedPin)              # Activate mux pin
            ADC.read(self._pin)
            self._currentValue = ADC.read(self._pin)
            if (self._muxedPin != None):
                MuxShadow.deactivate()                          # Deactivate mux
            if self._mode == 'Auto Detection':                  # Go for detection
                if self._currentValue < TIMEOUT_THRESHOLD:      # Count how many times the values is zero
                    self._zeroCounter += 1                      # Increase zero counter
                else:
                    self._zeroCounter = 0                       # Reset zero counter
            elif self._mode == 'Manual Detection':              # Keep device anyway
                self._zeroCounter = 0                           # Reset zero counter

            self._values.append([time.time(), [self._currentValue]]) # Save timestamp and value

            endT = time.time()                                  # Save start time of loop cycle
            deltaT = endT - beginT                              # Calculate time used for loop cycle
            self._cycleDuration = deltaT                        # Save time needed for a cycle
            if (deltaT < self._period):
                time.sleep(self._period - deltaT)               # Sleep until next loop period

            if not self._threadActive:                          # Stop the thread
                return

    def getValues(self, clear=True):
        """Get values for the adc device."""
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
            return '{}@ADC[{}]'.format(self._name, self._pin)
        else:
            return '{}@ADC[{}:{}]'.format(self._name, self._pin, self._muxedPin)

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

    def getCycleDuration(self):
        """Return device cycle duration."""
        return self._cycleDuration

    def getMode(self):
        """Return device mode."""
        return self._mode

    def setMode(self, mode):
        """Set device mode."""
        if (mode in self._settings['modes']):
            self._mode = mode
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
