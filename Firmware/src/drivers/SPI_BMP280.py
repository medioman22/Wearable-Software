# -*- coding: utf-8 -*-
# Author: Salar Rahimi
# Date: December 2020
"""
Driver file for the BMP280 Temperature / Pressure / Altitude. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package.
"""
import time                                                     # Imported for delay reasons
import drivers._BMP280_SPI as BMP280_DRIVER                         # Import official driver
import busio, board , digitalio                                 # Adafruit Blinka        
import threading                                                # Threading class for the threads
from micropython import const

from MuxModule import GetMux                                    # SoftWEAR MUX module.

# Mux Module to switch channels
MuxModule = GetMux()

# Unique identifier of the sensor
IDENTIFIER = BMP280_DRIVER._CHIP_ID



# Mode Map
MODE_MAP = {
    'Sleep':      BMP280_DRIVER.MODE_SLEEP,
    'Normal':      BMP280_DRIVER.MODE_NORMAL,
    'Force':      BMP280_DRIVER.MODE_FORCE
}

#Chip ID
BMP280_DRIVER._CHIP_ID = const(0xc0)


class BMP280_SPI:
    """BMP280 SPI Driver"""

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
            '25 KHz',
            '50 KHz',
            '75 KHz',
            '100 KHz',
            '125 KHz',
            '150 KHz',
            '175 KHz',
            '200 KHz',
            '225 KHz',
            '250 KHz',
            '275 KHz',
            '300 KHz',
            '325 KHz'
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

    # Module number for SPI
    SPI_number = None

    # Connection Status
    _Status = False



    # Lock for the driver, used in scan and loop thread
    LOCK = threading.Lock()

    def __init__(self, pinConfig, muxedChannel = None, muxName = None):
        """Init the device."""
        try:
            if (muxedChannel != None):
                MuxModule.activate(muxName, muxedChannel)           # Activate mux channel


            self._muxName = muxName                                 # Set mux name
            self._muxedChannel = muxedChannel                       # Set muxed pin

            self._values = []                                       # Set empty values array

            self._mode = self._settings['modes'][1]                 # Set default mode

            self._frequency = self._settings['frequencies'][6]      # Set default frequency

            self._flags = [] 

            self.SPI_number = pinConfig['SPI#']
            # Selecting the SPI combination on BBGW
            if pinConfig['SPI#'] == 0:
                spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
                bmp_cs = digitalio.DigitalInOut(board.P9_17)
            elif pinConfig['SPI#'] == 1:
                spi = busio.SPI(board.SCK_1, board.MOSI_1, board.MISO_1)
                bmp_cs = digitalio.DigitalInOut(board.P9_28)

            self._bmp = BMP280_DRIVER.Adafruit_BMP280_SPI(spi, bmp_cs)  # Create the driver object

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
            if not self._connected:
                if self.SPI_number == 0:
                    spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
                    bmp_cs = digitalio.DigitalInOut(board.P9_17)
                elif self.SPI_number == 1:
                    spi = busio.SPI(board.SCK_1, board.MOSI_1, board.MISO_1)
                    bmp_cs = digitalio.DigitalInOut(board.P9_28)

                BMP280_DRIVER.Adafruit_BMP280_SPI(spi, bmp_cs)


                self._bmp = BMP280_DRIVER.Adafruit_BMP280_SPI(spi, bmp_cs)  # Create the driver object
                self._connected = True
                
            if (self._muxedChannel != None):
                MuxModule.deactivate(self._muxName)  
                
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
        """Get values for the spi device."""
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
            return '{}@SPI[{}]'.format(self._name, self.SPI_number)
        else:
            return '{}@SPI[{}]#{}[{}]'.format(self._name, self.SPI_number, self._muxName, self._muxedChannel)

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
        return self.SPI_number

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
            GetfreqNum = int(self._frequency.replace("KHz",""))*1000
            self._bmp._spi.baudrate = GetfreqNum
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
        return ("SPI#" in pinConfig and
                pinConfig["SPI#"] == self.SPI_number and
                muxedChannel == self._muxedChannel)
