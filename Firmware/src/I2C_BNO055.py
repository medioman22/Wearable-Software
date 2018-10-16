# -*- coding: utf-8 -*-
"""
Driver file for the BNO055 accelerometer / gyroscope / magnetometer. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package.
"""
import Adafruit_GPIO.I2C as I2C                                 # Main peripheral class. Implements I2C communication
import time                                                     # Imported for delay reasons

# Unique identifier of the sensor
IDENTIFIER = 0xA0

# Addresses
ADDRESS_1 = 0x28
ADDRESS_2 = 0x29

"""Registers"""
BNO055_CHIP_ID               = 0x00
BNO055_ACCEL_REV_ID          = 0x01
BNO055_MAG_REV_ID            = 0x02
BNO055_GYRO_REV_ID           = 0x03
BNO055_SW_REV_ID_LSB         = 0x04
BNO055_SW_REV_ID_MSB         = 0x05
BNO055_BL_REV_ID             = 0x06

# Accel data register
BNO055_ACC_X_LSB             = 0x08
BNO055_ACC_X_MSB             = 0x09
BNO055_ACC_Y_LSB             = 0x0a
BNO055_ACC_Y_MSB             = 0x0b
BNO055_ACC_Z_LSB             = 0x0c
BNO055_ACC_Z_MSB             = 0x0d

# Mag data register
BNO055_MAG_X_LSB             = 0x0e
BNO055_MAG_X_MSB             = 0x0f
BNO055_MAG_Y_LSB             = 0x10
BNO055_MAG_Y_MSB             = 0x11
BNO055_MAG_Z_LSB             = 0x12
BNO055_MAG_Z_MSB             = 0x13

# Gyro data registers
BNO055_GYR_X_LSB             = 0x14
BNO055_GYR_X_MSB             = 0x15
BNO055_GYR_Y_LSB             = 0x16
BNO055_GYR_Y_MSB             = 0x17
BNO055_GYR_Z_LSB             = 0x18
BNO055_GYR_Z_MSB             = 0x19

# Euler data registers
BNO055_EULER_H_LSB           = 0x1a
BNO055_EULER_H_MSB           = 0x1b
BNO055_EULER_R_LSB           = 0x1c
BNO055_EULER_R_MSB           = 0x1d
BNO055_EULER_P_LSB           = 0x1e
BNO055_EULER_P_MSB           = 0x1f

# Quaternion data registers
BNO055_QUATERNION_W_LSB      = 0x20
BNO055_QUATERNION_W_MSB      = 0x21
BNO055_QUATERNION_X_LSB      = 0x22
BNO055_QUATERNION_X_MSB      = 0x23
BNO055_QUATERNION_Y_LSB      = 0x24
BNO055_QUATERNION_Y_MSB      = 0x25
BNO055_QUATERNION_Z_LSB      = 0x26
BNO055_QUATERNION_Z_MSB      = 0x27

# Linear acceleration data registers
BNO055_LINEAR_ACC_X_LSB      = 0x28
BNO055_LINEAR_ACC_X_MSB      = 0x29
BNO055_LINEAR_ACC_Y_LSB      = 0x2a
BNO055_LINEAR_ACC_Y_MSB      = 0x2b
BNO055_LINEAR_ACC_Z_LSB      = 0x2c
BNO055_LINEAR_ACC_Z_MSB      = 0x2d

# Gravity data registers
BNO055_GRAVITY_X_LSB         = 0x2e
BNO055_GRAVITY_X_MSB         = 0x2f
BNO055_GRAVITY_Y_LSB         = 0x30
BNO055_GRAVITY_Y_MSB         = 0x31
BNO055_GRAVITY_Z_LSB         = 0x32
BNO055_GRAVITY_Z_MSB         = 0x33

# Temperature data register
BNO055_TEMP                  = 0x34

# Status Registers
BNO055_CALIB_STAT_ADDR       = 0X35
BNO055_SELFTEST_RESULT_ADDR  = 0X36
BNO055_INTR_STAT_ADDR        = 0X37

BNO055_SYS_CLK_STAT_ADDR     = 0X38
BNO055_SYS_STAT_ADDR         = 0X39
BNO055_SYS_ERR_ADDR          = 0X3A

# Unit selection register
BNO055_UNIT_SEL_ADDR         = 0X3B
BNO055_DATA_SELECT_ADDR      = 0X3C

# Mode registers
BNO055_OPR_MODE_ADDR         = 0X3D
BNO055_PWR_MODE_ADDR         = 0X3E

BNO055_SYS_TRIGGER_ADDR      = 0X3F
BNO055_TEMP_SOURCE_ADDR      = 0X40

# Axis remap registers
BNO055_AXIS_MAP_CONFIG_ADDR  = 0X41
BNO055_AXIS_MAP_SIGN_ADDR    = 0X42

# SIC registers
BNO055_SIC_MATRIX_0_LSB_ADDR = 0X43
BNO055_SIC_MATRIX_0_MSB_ADDR = 0X44
BNO055_SIC_MATRIX_1_LSB_ADDR = 0X45
BNO055_SIC_MATRIX_1_MSB_ADDR = 0X46
BNO055_SIC_MATRIX_2_LSB_ADDR = 0X47
BNO055_SIC_MATRIX_2_MSB_ADDR = 0X48
BNO055_SIC_MATRIX_3_LSB_ADDR = 0X49
BNO055_SIC_MATRIX_3_MSB_ADDR = 0X4A
BNO055_SIC_MATRIX_4_LSB_ADDR = 0X4B
BNO055_SIC_MATRIX_4_MSB_ADDR = 0X4C
BNO055_SIC_MATRIX_5_LSB_ADDR = 0X4D
BNO055_SIC_MATRIX_5_MSB_ADDR = 0X4E
BNO055_SIC_MATRIX_6_LSB_ADDR = 0X4F
BNO055_SIC_MATRIX_6_MSB_ADDR = 0X50
BNO055_SIC_MATRIX_7_LSB_ADDR = 0X51
BNO055_SIC_MATRIX_7_MSB_ADDR = 0X52
BNO055_SIC_MATRIX_8_LSB_ADDR = 0X53
BNO055_SIC_MATRIX_8_MSB_ADDR = 0X54

# Accelerometer Offset registers
ACCEL_OFFSET_X_LSB_ADDR      = 0X55
ACCEL_OFFSET_X_MSB_ADDR      = 0X56
ACCEL_OFFSET_Y_LSB_ADDR      = 0X57
ACCEL_OFFSET_Y_MSB_ADDR      = 0X58
ACCEL_OFFSET_Z_LSB_ADDR      = 0X59
ACCEL_OFFSET_Z_MSB_ADDR      = 0X5A

# Magnetometer Offset registers
MAG_OFFSET_X_LSB_ADDR        = 0X5B
MAG_OFFSET_X_MSB_ADDR        = 0X5C
MAG_OFFSET_Y_LSB_ADDR        = 0X5D
MAG_OFFSET_Y_MSB_ADDR        = 0X5E
MAG_OFFSET_Z_LSB_ADDR        = 0X5F
MAG_OFFSET_Z_MSB_ADDR        = 0X60

# Gyroscope Offset registers
GYRO_OFFSET_X_LSB_ADDR       = 0X61
GYRO_OFFSET_X_MSB_ADDR       = 0X62
GYRO_OFFSET_Y_LSB_ADDR       = 0X63
GYRO_OFFSET_Y_MSB_ADDR       = 0X64
GYRO_OFFSET_Z_LSB_ADDR       = 0X65
GYRO_OFFSET_Z_MSB_ADDR       = 0X66

# Radius registers
ACCEL_RADIUS_LSB_ADDR        = 0X67
ACCEL_RADIUS_MSB_ADDR        = 0X68
MAG_RADIUS_LSB_ADDR          = 0X69
MAG_RADIUS_MSB_ADDR          = 0X6A



# Mode Map
MODE_MAP = {
    'ACCONLY':      0x01,
    'MAGONLY':      0x02,
    'GYROONLY':     0x03,
    'ACCMAG':       0x04,
    'ACCGYRO':      0x05,
    'MAGGYRO':      0x06,
    'AMG':          0x07,
    'IMU':          0x08,
    'COMPASS':      0x09,
    'M4G':          0x0A,
    'NDOF_FMC_OFF': 0x0B,
    'NDOF':         0x0C,
}




class BNO055:
    """Driver for BNO055."""

    # Name of the device
    _name = 'BNO055'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 17

    # Channel
    _channel = None

    # Muxed channel
    _muxedChannel = None

    # The object used to handle the I2C communication
    _i2cObject = None

    # Settings of the driver
    _settings = {
        'modes': ['ACCONLY', 'MAGONLY', 'GYROONLY', 'ACCMAG', 'ACCGYRO', 'MAGGYRO', 'AMG', 'IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF'],
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

        if ADRSet == True:                                      # Set the I2C address
            self._i2cObject = I2C.get_i2c_device(ADDRESS_2, 2)
        else:
            self._i2cObject = I2C.get_i2c_device(ADDRESS_1, 2)


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        time.sleep(0.005)                                       # Wait 5ms  - test if needed!!!!
        try:                                                    # If no device, it will throw an exception.
            res = self._i2cObject.readU8(BNO055_CHIP_ID)        # At register address 0x00 a constant of IDENTIFIER is always returned.
            if res == IDENTIFIER:
                return True
            else:                                               # Other value -> other device at same I2C address
                return False
        except:                                                 # exception -> no device. Return False
            return False

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        try:
            time.sleep(0.005)                                   # Wait 5ms to let the device boot up
            self._i2cObject.write8(BNO055_OPR_MODE_ADDR, 0x00)  # Set device in configuration mode (should already be there at boot)
            time.sleep(0.02)                                    # Wait >19ms to let the device switch the mode
            self._i2cObject.write8(BNO055_PWR_MODE_ADDR, 0x00)  # Put device in normal power mode
            self._i2cObject.write8(BNO055_UNIT_SEL_ADDR, 0x01)  # Select default units
            self._i2cObject.write8(BNO055_OPR_MODE_ADDR, MODE_MAP[self._mode]) # Set device as to default mode
            time.sleep(0.01)                                    # Wait >7ms to let the device switch the mode
        except:                                                 # Device disconnected in the meantime
            return

    def getValues(self):
        """Get values."""
        acc = [None,None,None]
        mag = [None,None,None]
        gyr = [None,None,None]
        eul = [None,None,None]
        qua = [None,None,None,None]
        tem = [None]
        if self._mode in ['ACCONLY', 'ACCMAG', 'ACCGYRO', 'AMG', 'IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            acc = self._getAccValues()                          # Get acc data
        if self._mode in ['MAGONLY', 'ACCMAG', 'MAGGYRO', 'AMG', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            mag = self._getMagValues()                          # Get mag data
        if self._mode in ['GYROONLY', 'ACCGYRO', 'MAGGYRO', 'AMG', 'IMU', 'NDOF_FMC_OFF', 'NDOF']:
            gyr = self._getGyrValues()                          # Get gyr data
        if self._mode in ['IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            eul = self._getEulValues()                          # Get eul data
        if self._mode in ['IMU', 'COMPASS', 'M4G', 'NDOF_FMC_OFF', 'NDOF']:
            qua = self._getQuaValues()                          # Get qua data
        if 'TEMPERATURE' in self._flags:
            tem = self._getTemValues()

        return acc + mag + gyr + eul + qua + tem

    def _getAccValues(self):
        """Get values for the acc (x,y,z)."""
        try:
            x = self._i2cObject.readU8(BNO055_ACC_X_LSB)        # Read LSB of X axis
            x += 0x100 * self._i2cObject.readU8(BNO055_ACC_X_MSB) # Read MSB of X axis
            if x > 0x7fff:                                      # Convert to signed int (16 bits)
                x = x - 65536

            y = self._i2cObject.readU8(BNO055_ACC_Y_LSB)        # Read LSB of Y axis
            y += 0x100 * self._i2cObject.readU8(BNO055_ACC_Y_MSB) # Read MSB of Y axis
            if y > 0x7fff:                                      # Convert to signed int (16 bits)
                y = y - 65536

            z = self._i2cObject.readU8(BNO055_ACC_Z_LSB)        # Read LSB of Z axis
            z += 0x100 * self._i2cObject.readU8(BNO055_ACC_Z_MSB) # Read MSB of Z axis
            if z > 0x7fff:                                      # Convert to signed int (16 bits)
                z = z - 65536

            return [x,y,z]                                      # Return values

        except:                                                 # Device disconnected in the meantime
            return [0,0,0]

    def _getMagValues(self):
        """Get values for the mag (x,y,z)."""
        try:
            x = self._i2cObject.readU8(BNO055_MAG_X_LSB)        # Read LSB of X axis
            x += 0x100 * self._i2cObject.readU8(BNO055_MAG_X_MSB) # Read MSB of X axis
            if x > 0x7fff:                                      # Convert to signed int (16 bits)
                x = x - 65536

            y = self._i2cObject.readU8(BNO055_MAG_Y_LSB)        # Read LSB of Y axis
            y += 0x100 * self._i2cObject.readU8(BNO055_MAG_Y_MSB) # Read MSB of Y axis
            if y > 0x7fff:                                      # Convert to signed int (16 bits)
                y = y - 65536

            z = self._i2cObject.readU8(BNO055_MAG_Z_LSB)        # Read LSB of Z axis
            z += 0x100 * self._i2cObject.readU8(BNO055_MAG_Z_MSB) # Read MSB of Z axis
            if z > 0x7fff:                                      # Convert to signed int (16 bits)
                z = z - 65536

            return [x,y,z]                                      # Return values

        except:                                                 # Device disconnected in the meantime
            return [0,0,0]

    def _getGyrValues(self):
        """Get values for the gyr (x,y,z)."""
        try:
            x = self._i2cObject.readU8(BNO055_GYR_X_LSB)        # Read LSB of X axis
            x += 0x100 * self._i2cObject.readU8(BNO055_GYR_X_MSB) # Read MSB of X axis
            if x > 0x7fff:                                      # Convert to signed int (16 bits)
                x = x - 65536

            y = self._i2cObject.readU8(BNO055_GYR_Y_LSB)        # Read LSB of Y axis
            y += 0x100 * self._i2cObject.readU8(BNO055_GYR_Y_MSB) # Read MSB of Y axis
            if y > 0x7fff:                                      # Convert to signed int (16 bits)
                y = y - 65536

            z = self._i2cObject.readU8(BNO055_GYR_Z_LSB)        # Read LSB of Z axis
            z += 0x100 * self._i2cObject.readU8(BNO055_GYR_Z_MSB) # Read MSB of Z axis
            if z > 0x7fff:                                      # Convert to signed int (16 bits)
                z = z - 65536

            return [x,y,z]                                      # Return values

        except:                                                 # Device disconnected in the meantime
            return [0,0,0]

    def _getEulValues(self):
        """Get values for the eul (h,r,p)."""
        try:
            h = self._i2cObject.readU8(BNO055_EULER_H_LSB)      # Read LSB of H angle
            h += 0x100 * self._i2cObject.readU8(BNO055_EULER_H_MSB) # Read MSB of H angle
            if h > 0x7fff:                                      # Convert to signed int (16 bits)
                h = h - 65536

            r = self._i2cObject.readU8(BNO055_EULER_R_LSB)      # Read LSB of R angle
            r += 0x100 * self._i2cObject.readU8(BNO055_EULER_R_MSB) # Read MSB of R angle
            if r > 0x7fff:                                      # Convert to signed int (16 bits)
                r = r - 65536

            p = self._i2cObject.readU8(BNO055_EULER_P_LSB)      # Read LSB of P angle
            p += 0x100 * self._i2cObject.readU8(BNO055_EULER_P_LSB) # Read MSB of P angle
            if p > 0x7fff:                                      # Convert to signed int (16 bits)
                p = p - 65536

            return [h,r,p]                                      # Return values

        except:                                                 # Device disconnected in the meantime
            return [0,0,0]

    def _getQuaValues(self):
        """Get values for the qua (w,x,y,z)."""
        try:
            w = self._i2cObject.readU8(BNO055_QUATERNION_W_LSB) # Read LSB of W
            w += 0x100 * self._i2cObject.readU8(BNO055_QUATERNION_W_MSB) # Read MSB of W
            if w > 0x7fff:                                      # Convert to signed int (16 bits)
                w = w - 65536

            x = self._i2cObject.readU8(BNO055_QUATERNION_X_LSB) # Read LSB of X
            x += 0x100 * self._i2cObject.readU8(BNO055_QUATERNION_X_MSB) # Read MSB of X
            if x > 0x7fff:                                      # Convert to signed int (16 bits)
                x = x - 65536

            y = self._i2cObject.readU8(BNO055_QUATERNION_Y_LSB) # Read LSB of Y
            y += 0x100 * self._i2cObject.readU8(BNO055_QUATERNION_Y_MSB) # Read MSB of Y
            if y > 0x7fff:                                      # Convert to signed int (16 bits)
                y = y - 65536

            z = self._i2cObject.readU8(BNO055_QUATERNION_Z_LSB) # Read LSB of Z
            z += 0x100 * self._i2cObject.readU8(BNO055_QUATERNION_Z_MSB) # Read MSB of Z
            if z > 0x7fff:                                      # Convert to signed int (16 bits)
                z = z - 65536

            return [w,x,y,z]                                    # Return values

        except:                                                 # Device disconnected in the meantime
            return [0,0,0]

    def _getTemValues(self):
        """Get values for the tem (t)."""
        try:
            t = self._i2cObject.readU8(BNO055_TEMP)             # Read LSB of T

            return [t]                                          # Return values

        except:                                                 # Device disconnected in the meantime
            return [0]

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
    def getChannel(self):
        """Return device channel."""
        return self._channel
    def getMuxedChannel(self):
        """Return device muxed channel."""
        return self._muxedChannel
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
                self._i2cObject.write8(BNO055_OPR_MODE_ADDR, 0x00)  # Set device to  config mode
                time.sleep(0.01)                                    # Wait >7ms to let the device switch the mode
                self._i2cObject.write8(BNO055_OPR_MODE_ADDR, MODE_MAP[self._mode]) # Set device to mode
                time.sleep(0.02)                                    # Wait >19ms to let the device switch the mode
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
