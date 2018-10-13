# -*- coding: utf-8 -*-
"""
Driver file for the BNO055 accelerometer / gyroscope / magnetometer. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package.
"""
import Adafruit_GPIO.I2C as I2C                                 # Main peripheral class. Implements I2C communication
import time                                                     # Imported for delay reasons

class BNO055:
    """Driver for BNO055."""

    # Name of the device
    _name = 'BNO055'

    # Direction of the driver (in/out)
    _dir = 'in'

    # Dimension of the driver (0-#)
    _dim = 3


    def __init__(self, chn, ADR_set = False):
        """Device supports an address pin, one can represent this with a 'True' value of ADR_set."""
        #self._i2c_object = mraa.I2c(chn)   # Create mraa I2C object
        if ADR_set == True:                 # Set the I2C address
            #self._i2c_object.address(0x29)
            self._i2c_object = I2C.get_i2c_device(0x29, 2)
        else:
            #self._i2c_object.address(0x28)
            self._i2c_object = I2C.get_i2c_device(0x28, 2)


    def getDeviceConnected(self):
        """Return True if the device is connected, false otherwise."""
        time.sleep(0.005)   # Wait 5ms  - test if needed!!!!
        try:                # If no device, it will throw an exception.
            # At register address 0x00 a constant of 0xA0 is always returned.
            #res = self._i2c_object.readReg(0x00)
            res = self._i2c_object.readU8(0x00)
            if res == 0xA0:
                return True
            else:           # Other value -> other device at same I2C address
                return False
        except:             # exception -> no device. Return False
            return False

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        try:
            time.sleep(0.005)   # Wait 5ms  - test if needed!!!!
            #self._i2c_object.writeReg(0x3D, 0x00)  # Set device in configuration mode
            self._i2c_object.write8(0x3D, 0x00)
            #self._i2c_object.writeReg(0x3E, 0x00)  # Put device in normal power mode
            self._i2c_object.write8(0x3E, 0x00)
            #self._i2c_object.writeReg(0x3B, 0x01)  # Select default units
            self._i2c_object.write8(0x3B, 0x01)
            time.sleep(0.005)   # Wait 5ms  - test if needed!!!!

            #self._i2c_object.writeReg(0x3D, 0x08)  # Set device as IMU
            self._i2c_object.write8(0x3D, 0x08)
        except:     # Device disconnected in the meantime
            return

    def getValues(self):
        """Get values for the imu (x,y,z)."""
        try:
            #x = self._i2c_object.readReg(0x08)             # Read LSB of X axis
            x = self._i2c_object.readU8(0x08)
            #x += 0x100 * self._i2c_object.readReg(0x09)    # Read MSB of X axis
            x += 0x100 * self._i2c_object.readU8(0x09)
            if x > 0x7fff:          # Convert to signed int (16 bits)
                x = x - 65536

            #y = self._i2c_object.readReg(0x0A)             # Read LSB of Y axis
            y = self._i2c_object.readU8(0x0A)
            #y += 0x100 * self._i2c_object.readReg(0x0B)    # Read MSB of Y axis
            y += 0x100 * self._i2c_object.readU8(0x0B)
            if y > 0x7fff:          # Convert to signed int (16 bits)
                y = y - 65536

            #z = self._i2c_object.readReg(0x0C)             # Read LSB of Z axis
            z = self._i2c_object.readU8(0x0C)
            #z += 0x100 * self._i2c_object.readReg(0x0D)    # Read MSB of Z axis
            z += 0x100 * self._i2c_object.readU8(0x0D)
            if z > 0x7fff:          # Convert to signed int (16 bits)
                z = z - 65536

        except:     # Device disconnected in the meantime
            return [0,0,0]

        return [x, y, z]

    def getDevice(self):
        """Return device name."""
        return self._name
    def getDir(self):
        """Return device direction."""
        return self._dir
    def getDim(self):
        """Return device dimension."""
        return self._dim

    """The object used to handle the I2C communication."""
    _i2c_object = None



"""
//---------------------------------------------------------
//----- Register's definition -----------------------------
//---------------------------------------------------------
// Page id register definition
#define BNO055_PAGE_ID          0x07

//----- page0 ---------------------------------------------
#define BNO055_CHIP_ID          0x00
#define BNO055_ACCEL_REV_ID     0x01
#define BNO055_MAG_REV_ID       0x02
#define BNO055_GYRO_REV_ID      0x03
#define BNO055_SW_REV_ID_LSB    0x04
#define BNO055_SW_REV_ID_MSB    0x05
#define BNO055_BL_REV_ID        0x06

// Accel data register*/
#define BNO055_ACC_X_LSB        0x08
#define BNO055_ACC_X_MSB        0x09
#define BNO055_ACC_Y_LSB        0x0a
#define BNO055_ACC_Y_MSB        0x0b
#define BNO055_ACC_Z_LSB        0x0c
#define BNO055_ACC_Z_MSB        0x0d

// Mag data register
#define BNO055_MAG_X_LSB        0x0e
#define BNO055_MAG_X_MSB        0x0f
#define BNO055_MAG_Y_LSB        0x10
#define BNO055_MAG_Y_MSB        0x11
#define BNO055_MAG_Z_LSB        0x12
#define BNO055_MAG_Z_MSB        0x13

// Gyro data registers
#define BNO055_GYR_X_LSB        0x14
#define BNO055_GYR_X_MSB        0x15
#define BNO055_GYR_Y_LSB        0x16
#define BNO055_GYR_Y_MSB        0x17
#define BNO055_GYR_Z_LSB        0x18
#define BNO055_GYR_Z_MSB        0x19

// Euler data registers
#define BNO055_EULER_H_LSB      0x1a
#define BNO055_EULER_H_MSB      0x1b

#define BNO055_EULER_R_LSB      0x1c
#define BNO055_EULER_R_MSB      0x1d

#define BNO055_EULER_P_LSB      0x1e
#define BNO055_EULER_P_MSB      0x1f

// Quaternion data registers
#define BNO055_QUATERNION_W_LSB 0x20
#define BNO055_QUATERNION_W_MSB 0x21
#define BNO055_QUATERNION_X_LSB 0x22
#define BNO055_QUATERNION_X_MSB 0x23
#define BNO055_QUATERNION_Y_LSB 0x24
#define BNO055_QUATERNION_Y_MSB 0x25
#define BNO055_QUATERNION_Z_LSB 0x26
#define BNO055_QUATERNION_Z_MSB 0x27

// Linear acceleration data registers
#define BNO055_LINEAR_ACC_X_LSB 0x28
#define BNO055_LINEAR_ACC_X_MSB 0x29
#define BNO055_LINEAR_ACC_Y_LSB 0x2a
#define BNO055_LINEAR_ACC_Y_MSB 0x2b
#define BNO055_LINEAR_ACC_Z_LSB 0x2c
#define BNO055_LINEAR_ACC_Z_MSB 0x2d

// Gravity data registers
#define BNO055_GRAVITY_X_LSB    0x2e
#define BNO055_GRAVITY_X_MSB    0x2f
#define BNO055_GRAVITY_Y_LSB    0x30
#define BNO055_GRAVITY_Y_MSB    0x31
#define BNO055_GRAVITY_Z_LSB    0x32
#define BNO055_GRAVITY_Z_MSB    0x33

// Temperature data register
#define BNO055_TEMP             0x34
"""
