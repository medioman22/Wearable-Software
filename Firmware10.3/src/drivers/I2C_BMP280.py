# -*- coding: utf-8 -*-
# Author: Salar Rahimi
# Date: December 2020
"""
Driver file for the BMP280 Temperature / Pressure / Altitude. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package.
"""
import time                                                     # Imported for delay reasons
import drivers._BMP280 as BMP280_DRIVER                         # Import official driver
import busio, board                                             # Adafruit Blinka        
import threading                                                # Threading class for the threads

from MuxModule import GetMux                                    # SoftWEAR MUX module.

# Mux Module to switch channels
MuxModule = GetMux()

# Unique identifier of the sensor
IDENTIFIER = BMP280_DRIVER._CHIP_ID

# Addresses
BMP280_ADDRESS = [0x77]
BMP280_BUSNUM  = [1,2]

# Mode Map
MODE_MAP = {
    'Sleep':      BMP280_DRIVER.MODE_SLEEP,
    'Normal':      BMP280_DRIVER.MODE_NORMAL,
    'Force':      BMP280_DRIVER.MODE_FORCE
}


class BMP280_I2C:
    """Driver for <Device name>."""

    # Name of the device
    _name = 'BMP280'

    # Info of the device
    _info = 'The BMP280 is an absolute barometric pressure sensor, which is especially feasible for mobile applications. Its small dimensions and its low power consumption allow for the implementation in battery-powered devices such as mobile phones, GPS modules or watches.'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 3

    # Dimension map of the driver (0-#)
    _dimMap = ['Pressure', 'Temperature', 'Altitude']

    # Dimension unit of the driver (0-#)
    _dimUnit = ['hPa', 'C', 'meters']

    # Muxed channel
    _muxedChannel = None

    # Mux name
    _muxName = None

    # The driver object
    _bmp = None

    # Flag whether the driver is connected
    _connected = False

    # Settings of the driver
    _settings = {
        #Data refresh frequency
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
        #Operation mode for driver
        'modes': [
            'Sleep',
            'Normal',
            'Force'
        ]
    }

    # Data type of values
    _dataType = 'Range'

    # Data range for values
    _dataRange = []

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
    _frequency = '20 Hz'

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
                MuxModule.activate(muxName, muxedChannel)           # Activate mux channel

            if "ADDRESS" in pinConfig and pinConfig["ADDRESS"] == None or pinConfig["ADDRESS"] not in BMP280_ADDRESS:
                raise ValueError('address is invalid')
            if "BUSNUM" in pinConfig and pinConfig["BUSNUM"] == None or pinConfig["BUSNUM"] not in BMP280_BUSNUM:
                raise ValueError('busnum is invalid')

            self._address = pinConfig["ADDRESS"]                    # Set address
            self._busnum = pinConfig["BUSNUM"]                      # Set bus
            self._muxName = muxName                                 # Set mux name
            self._muxedChannel = muxedChannel                       # Set muxed pin

            self._values = []                                       # Set empty values array

            self._mode = self._settings['modes'][0]                 # Set default mode

            self._frequency = self._settings['frequencies'][6]      # Set default frequency

            self._flags = [] 

            i2c_busio = busio.I2C(board.SCL, board.SDA)                              # Object for I2C
            self._bmp = BMP280_DRIVER.Adafruit_BMP280_I2C(i2c_busio)  # Create the driver object
            #self._bmp.sea_level_pressure = 1013.25

            if (muxedChannel != None):
                MuxModule.deactivate(muxName)                       # Deactivate mux
        except:
            #print('Exception in <device> driver init')
            self._connected = False

            if (muxedChannel != None):
                MuxModule.deactivate(muxName)                       # Deactivate mux


    def cleanup(self):
        """Clean up driver when no longer needed."""
        self._connected = False                                 # Device disconnected
        self._threadActive = False                              # Unset thread active flag
        

    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        self.LOCK.acquire()                                     # Lock the driver for scanning
        try:
            if (self._muxedChannel != None):
                MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel
            status = self._bmp._get_status() # Get status
            self._connected = True                       # Device is connected and has no error
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)             # Deactivate mux
        except:
            self._connected = False                             # Device disconnected
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)             # Deactivate mux
        self.LOCK.release()                                     # Release driver
        return self._connected

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        try:
            if (self._muxedChannel != None):
                MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel
            self._bmp.mode = MODE_MAP[self._mode]
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)             # Deactivate mux
        except:                                                 # Device disconnected in the meantime
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)             # Deactivate mux
            raise IOError('<What Error?>')
        self._threadActive = True                               # Set thread active flag
        self._thread = threading.Thread(target=self._loop, name=self._name) # Create thread
        self._thread.daemon = True                              # Set thread as daemonic
        self._thread.start()                                    # Start thread

    def _loop(self):
        """Inner loop of the driver."""
        while True:
            beginT = time.time()                                # Save start time of loop cycle
            deltaT = 0

            try:
                self.LOCK.acquire()                             # Lock the driver for loop
                if (self._muxedChannel != None):
                    MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel

                self._currentValue = [self._bmp.pressure, self._bmp.temperature, self._bmp.altitude]

                
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
        if (mode in self._settings['modes']):
            self._mode = mode

            try:
                if (self._muxedChannel != None):
                    MuxModule.activate(self._muxName, self._muxedChannel) # Activate mux channel
                self._bmp.mode = MODE_MAP[self._mode]                        # Set device to mode
                if (self._muxedChannel != None):
                    MuxModule.deactivate(self._muxName)             # Deactivate mux
            except:                                                 # Device disconnected in the meantime
                if (self._muxedChannel != None):
                    MuxModule.deactivate(self._muxName)             # Deactivate mux
                raise IOError('Error on i2c device while switching mode')
        else:
            raise ValueError('mode {} is not allowed'.format(mode))

    def getFlags(self):
        """Return device mode."""
        return []

    def getFlag(self, flag):
        """Return device mode."""
        return None

    def setFlag(self, flag, value):
        """Set device flag."""
        if (flag in self._settings['flags']):
            if value:
                self._flags.append(flag)                            # Add the flag
            else:
                self._flags.remove(flag)                            # Remove the flag
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
        raise ValueError('duty frequency {} is not allowed'.format(dutyFrequency))


    def comparePinConfig(self, pinConfig, muxedChannel = None):
        """Check if the same pin config."""
        return ("ADDRESS" in pinConfig and
                "BUSNUM" in pinConfig and
                pinConfig["ADDRESS"] == self._address and
                pinConfig["BUSNUM"] == self._busnum and
                muxedChannel == self._muxedChannel)
