# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Driver file for the PCA9685 16-channel PWM controller. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package.
"""
import time                                                     # Imported for delay reasons
import drivers._PCA9685 as PCA9685_DRIVER                       # Import official driver
import threading                                                # Threading class for the threads

from MuxModule import GetMux                                    # SoftWEAR MUX module.

# Mux Module to switch channels
MuxModule = GetMux()

# Constants
PCA9685_ADDRESS    = [0x40]
PCA9685_BUSNUM     = [1, 2]



class PCA9685:
    """Driver for PCA9685."""

    # Name of the device
    _name = 'PCA9685'

    # Info of the device
    _info = 'The PCA9685 is an I2C-bus controlled 16-channel LED controller optimized for Red/Green/Blue/Amber (RGBA) color backlighting applications. Each LED output has its own 12-bit resolution (4096 steps) fixed frequency individual PWM controller that operates at a programmable frequency from a typical of 24 Hz to 1526 Hz with a duty cycle that is adjustable from 0 % to 100 % to allow the LED to be set to a specific brightness value. All outputs are set to the same PWM frequency.'


    # Direction of the driver (in/out)
    _dir = 'out'

    # Dimension of the driver (0-#)
    _dim = 16

    # Dimension map of the driver (0-#)
    _dimMap = ['PWM 00', 'PWM 01', 'PWM 02', 'PWM 03', 'PWM 04', 'PWM 05', 'PWM 06', 'PWM 07', 'PWM 08', 'PWM 09', 'PWM 10', 'PWM 11', 'PWM 12', 'PWM 13', 'PWM 14', 'PWM 15']

    # Dimension unit of the driver (0-#)
    _dimUnit = ['%', '%', '%', '%', '%', '%', '%', '%', '%', '%', '%', '%', '%', '%', '%', '%']

    # Muxed channel
    _muxedChannel = None

    # Mux name
    _muxName = None

    # The driver object
    _pca = None

    # Flag whether the driver is connected
    _connected = False

    # Settings of the driver
    _settings = {
        'dutyFrequencies': [
            '24 Hz',
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
            '1526 Hz'
        ],
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
        'flags': ['INVERSE_PARITY']
    }

    # Data type of values
    _dataType = 'Range'

    # Data range for values
    _dataRange = [0,99]

    # Value to set
    _currentValue = []

    # Value history
    _values = None

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

    # Address of the driver
    _address = None

    # Bus num of the driver
    _busnum = None

    # Lock for the driver, used in scan and loop thread
    LOCK = threading.Lock()

    def __init__(self, pinConfig, muxedChannel = None, muxName = None):
        """Init the device."""
        try:
            if (muxedChannel != None):
                MuxModule.activate(muxName, muxedChannel)       # Activate mux channel
            if "ADDRESS" in pinConfig and pinConfig["ADDRESS"] == None or pinConfig["ADDRESS"] not in PCA9685_ADDRESS:
                raise ValueError('address is invalid')
            if "BUSNUM" in pinConfig and pinConfig["BUSNUM"] == None or pinConfig["BUSNUM"] not in PCA9685_BUSNUM:
                raise ValueError('busnum is invalid')

            self._address = pinConfig["ADDRESS"]                # Set address
            self._busnum = pinConfig["BUSNUM"]                  # Set bus
            self._muxedChannel = muxedChannel                   # Set muxed pin
            self._muxName = muxName                             # Set mux name

            self._currentValue = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Initialize current value
            self._values = []                                   # Set empty values array

            self._dutyFrequency = self._settings['dutyFrequencies'][7] # Set default dutyFrequency
            #self._mode = self._settings['modes'][0]             # Set default mode
            self._flags = []                                    # Set default flag list

            self._pca = PCA9685_DRIVER.PCA9685(address=self._address,busnum=self._busnum) # Create the driver object
            if (muxedChannel != None):
                MuxModule.deactivate(muxName)                   # Deactivate mux
        except:
            print('Exception in PCA9685 driver init')
            self._connected = False
            if (muxedChannel != None):
                MuxModule.deactivate(muxName)                   # Deactivate mux

    def cleanup(self):
        """Clean up driver when no longer needed."""
        self._connected = False                                 # Device disconnected
        self._threadActive = False                              # Unset thread active
        try:
            self._pca.cleanup()                                 # Set PWM to sleep
        except:
            pass

    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        try:
            self.LOCK.acquire()                                 # Lock the driver for scanning
            if (self._muxedChannel != None):
                MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel
            self._connected = self._pca.status()                # Device is connected and has no error
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)             # Deactivate mux
            self.LOCK.release()                                 # Release driver
        except:
            self._connected = False                             # Device disconnected
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)             # Deactivate mux
            self.LOCK.release()                                 # Release driver
        return self._connected

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        # Device gets configured already at initialization, therefore no need to configure further
        self._threadActive = True                               # Set thread active flag
        self._thread = threading.Thread(target=self._loop, name=self._name) # Create thread
        self._thread.daemon = True                              # Set thread as daemonic
        self._thread.start()                                    # Start thread

    def _loop(self):
        """Inner loop of the driver."""
        while True:
            beginT = time.time()                                # Save start time of loop cycle

            try:
                self.LOCK.acquire()                             # Lock the driver for loop
                if (self._muxedChannel != None):
                    MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel
                if self._update:
                    if 'INVERSE_PARITY' in self._flags:         # Check for parity flag
                        for i, val in enumerate(self._currentValue): # Loop all values
                            setDuty(self._pca, i, 100. - val)   # Set duty for channel
                    else:
                        for i, val in enumerate(self._currentValue): # Loop all values
                            setDuty(self._pca, i, val)          # Set duty for channel


                    self._update = False                        # Clear update flag

                self._values.append([time.time(), self._currentValue]) # Save timestamp and value

                endT = time.time()                              # Save start time of loop cycle
                deltaT = endT - beginT                          # Calculate time used for loop cycle
                self._cycleDuration = deltaT                    # Save time needed for a cycle

                if (self._muxedChannel != None):
                    MuxModule.deactivate(self._muxName)         # Deactivate mux
                self.LOCK.release()                             # Release driver
            except:
                self._connected = False                         # Device disconnected
                if (self._muxedChannel != None):
                    MuxModule.deactivate(self._muxName)         # Deactivate mux
                self.LOCK.release()                             # Release driver

            if (deltaT < self._period):
                time.sleep(self._period - deltaT)               # Sleep until next loop period

            if not self._threadActive:                          # Stop the thread
                return

    def getValues(self, clear=True):
        """Get values for the i2c device."""
        if self._values == None:                                # Return empty array for no values
            return []
        values = self._values[:]                                # Get the values
        if clear:
            self._values = []                                   # Reset values
        return values                                           # Return the values

    def setValue(self, dim, value):
        """Set values for the i2c device."""
        self._currentValue[dim] = min(100., max(0., value))     # Get the value and update the dim current value of the driver
                                                                # Value is limited to range [0,100]
        self._update = True                                     # Raise update flag


    def getDevice(self):
        """Return device name."""
        return self._name

    def getName(self):
        """Return device name."""
        if self._muxedChannel == None:
            return '{}@I2C[{},{}]'.format(self._name, self._address, self._busnum)
        else:
            return '{}@I2C[{},{}]#{}[{}]'.format(self._name, self._address, self._busnum, self._muxName, self._muxedChannel)

    def getDir(self):
        """Return device direction."""
        return self._dir

    def getDim(self):
        """Return device dimension."""
        return self._dim

    def getDimMap(self):
        """Return device dimension map."""
        return self._dimMap[:]

    def getChannel(self):
        """Return device channel."""
        return self._busnum

    def getMuxedChannel(self):
        """Return device muxed channel."""
        return self._muxedChannel

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
            try:
                if (self._muxedChannel != None):
                    MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel
                self._dutyFrequency = dutyFrequency
                self._pca.set_pwm_freq(int(self._dutyFrequency[:-3]))
                self._update = True                             # Raise update flag
                if (self._muxedChannel != None):
                    MuxModule.deactivate(self._muxName)         # Deactivate mux
            except:
                self._connected = False                         # Device disconnected
                if (self._muxedChannel != None):
                    MuxModule.deactivate(self._muxName)         # Deactivate mux
        else:
            raise ValueError('duty frequency {} is not allowed'.format(dutyFrequency))


    def comparePinConfig(self, pinConfig, muxedChannel = None):
        """Check if the same pin config."""
        return ("ADDRESS" in pinConfig and
                "BUSNUM" in pinConfig and
                pinConfig["ADDRESS"] == self._address and
                pinConfig["BUSNUM"] == self._busnum and
                muxedChannel == self._muxedChannel)


def setDuty(pca, channel, duty):
    """Help function to make setting a duty width simpler."""
    res = 4096                                                      # 12 bits of resolution
    on = 0                                                          # Duty on
    off = int(duty / 100. * res)                                    # Duty off
    pca.set_pwm(channel, on, off)                                   # Send the values to the pca
