# -*- coding: utf-8 -*-
"""
Driver file for the BNO055 accelerometer / gyroscope / magnetometer. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package.
"""
import Adafruit_GPIO.I2C as I2C                                 # Main peripheral class. Implements I2C communication
import time                                                     # Imported for delay reasons
import drivers._BNO055 as BNO055_DRIVER                         # Import official driver

# Unique identifier of the sensor
IDENTIFIER = BNO055_DRIVER.BNO055_ID

# Addresses
ADDRESS_1 = BNO055_DRIVER.BNO055_ADDRESS_A
ADDRESS_2 = BNO055_DRIVER.BNO055_ADDRESS_B
BUSNUM = 2

# Mode Map
MODE_MAP = {
    'ACCONLY':      BNO055_DRIVER.OPERATION_MODE_ACCONLY,
    'MAGONLY':      BNO055_DRIVER.OPERATION_MODE_MAGONLY,
    'GYRONLY':      BNO055_DRIVER.OPERATION_MODE_GYRONLY,
    'ACCMAG':       BNO055_DRIVER.OPERATION_MODE_ACCMAG,
    'ACCGYRO':      BNO055_DRIVER.OPERATION_MODE_ACCGYRO,
    'MAGGYRO':      BNO055_DRIVER.OPERATION_MODE_MAGGYRO,
    'AMG':          BNO055_DRIVER.OPERATION_MODE_AMG,
    'IMU':          BNO055_DRIVER.OPERATION_MODE_IMUPLUS,
    'COMPASS':      BNO055_DRIVER.OPERATION_MODE_COMPASS,
    'M4G':          BNO055_DRIVER.OPERATION_MODE_M4G,
    'NDOF_FMC_OFF': BNO055_DRIVER.OPERATION_MODE_NDOF_FMC_OFF,
    #'NDOF':         BNO055_DRIVER.OPERATION_MODE_NDOF
}
######################
# BUG: NDOF
# NDOF mode cannot be selected during runtime. Please change driver to initialize to NDOF mode at the beginning if needed and do not change it afterwards.
######################



class BNO055:
    """Driver for BNO055."""

    # Name of the device
    _name = 'BNO055'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 17

    # Dimension map of the driver (0-#)
    _dimMap = ['Acc X', 'Acc Y', 'Acc Z', 'Mag X', 'Mag Y', 'Mag Z', 'Gyr X', 'Gyr Y', 'Gyr Z', 'Euler Head', 'Euler Roll', 'Euler Pitch', 'Quat W', 'Quat X', 'Quat Y', 'Quat Z', 'Temp']


    # Channel
    _channel = None

    # Muxed channel
    _muxedChannel = None

    # The driver object
    _bno = None

    # Flag whether the driver is connected
    _connected = False

    # Settings of the driver
    _settings = {
        'modes': [
            'ACCONLY',
            'MAGONLY',
            'GYRONLY',
            'ACCMAG',
            'ACCGYRO',
            'MAGGYRO',
            'AMG',
            'IMU',
            'COMPASS',
            'M4G',
            'NDOF_FMC_OFF',
            #'NDOF'
        ],
        'flags': ['TEMPERATURE']
    }

    # Mode
    _mode = None

    # Mode
    _flags = None


    def __init__(self, channel, muxedChannel = None, ADRSet = False):
        """Device supports an address pin, one can represent this with a 'True' value of ADRSet."""
        self._channel = channel                                 # Set pin
        self._muxedChannel = muxedChannel                       # Set muxed pin

        self._mode = self._settings['modes'][0]                 # Set default mode
        self._flags = []                                        # Set default flag list

        # self._bno = BNO055_DRIVER.BNO055(rst='P9_12')         # Use that line for hardware reset pin
                                                                # otherwise software reset is used
        self._bno = BNO055_DRIVER.BNO055(address=ADDRESS_1,busnum=BUSNUM) # Create the driver object
        try:
            self._connected = self._bno.begin()                 # Connect to the device
        except IOError:
            self._connected = False


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        try:
            status, self_test, error = self._bno.get_system_status(False) # Get status
            self._connected = (error == 0)                      # Device is connected and has no error
        except IOError:
             self._connected = False                            # Device disconnected
        return self._connected

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        try:
            self._bno.set_mode(MODE_MAP[self._mode])            # Set device as to default mode
        except:                                                 # Device disconnected in the meantime
            raise IOError('Error on i2c device while switching mode')

    def getValues(self):
        """Get values."""
        acc = [None,None,None]
        mag = [None,None,None]
        gyr = [None,None,None]
        eul = [None,None,None]
        qua = [None,None,None,None]
        tem = [None]
        if self._mode in ['ACCONLY', 'ACCMAG', 'ACCGYRO', 'AMG', 'IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            acc = list(self._bno.read_accelerometer())          # Get acc data
        if self._mode in ['MAGONLY', 'ACCMAG', 'MAGGYRO', 'AMG', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            mag = list(self._bno.read_magnetometer())           # Get mag data
        if self._mode in ['GYRONLY', 'ACCGYRO', 'MAGGYRO', 'AMG', 'IMU', 'NDOF_FMC_OFF', 'NDOF']:
            gyr = list(self._bno.read_gyroscope())              # Get gyr data
        if self._mode in ['IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            eul = list(self._bno.read_euler())                  # Get eul data
        if self._mode in ['IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            qua = list(self._bno.read_quaternion())             # Get qua data
        if 'TEMPERATURE' in self._flags:
            tem = [self._bno.read_temp()]                       # Get tem data

        return acc + mag + gyr + eul + qua + tem

    def getDevice(self):
        """Return device name."""
        return self._name
    def getName(self):
        """Return device name."""
        if self._muxedChannel == None:
            return '{}@I2C[{}]'.format(self._name, self._channel)
        else:
            return '{}@I2C[{}:{}]'.format(self._name, self._channel, self._muxedChannel)
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
        return self._channel
    def getMuxedChannel(self):
        """Return device muxed channel."""
        return self._muxedChannel
    def getAbout(self):
        """Return device settings."""
        return {'dimMap': self._dimMap[:]}
    def getSettings(self):
        """Return device settings."""
        return self._settings
    def getMode(self):
        """Return device mode."""
        return self._mode
    def getFlags(self):
        """Return device mode."""
        return self._flags[:]
    def getFlag(self, flag):
        """Return device mode."""
        return self._flags[flag]

    def setMode(self, mode):
        """Set device mode."""
        if (mode in self._settings['modes']):
            self._mode = mode
            try:
                self._bno.set_mode(MODE_MAP[self._mode])            # Set device to mode
            except:                                                 # Device disconnected in the meantime
                raise IOError('Error on i2c device while switching mode')
        else:
            raise ValueError('mode {} is not allowed'.format(mode))

    def setFlag(self, flag, value):
        """Set device flag."""
        if (flag in self._settings['flags']):
            if value:
                self._flags.append(flag)                            # Add the flag
            else:
                self._flags.remove(flag)                            # Remove the flag
        else:
            raise ValueError('flag {} is not allowed'.format(flag))
