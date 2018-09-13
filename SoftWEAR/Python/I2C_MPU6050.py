# -*- coding: utf-8 -*-
"""
Driver file for the MPU6050 accelerometer / gyroscope / magnetometer. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package. 
"""
import mraa  # Main peripheral class. Implements I2C communication 
import time  # Imported for delay reasons

class MPU6050:
    def __init__(self, chn, ADR_set = False):
        """ Class contstructor. Since device supports and address pin, one can
            represent this with a 'True' value of ADR_set. """
        self._mraa_object = mraa.I2c(chn)       # Create mraa I2C object
        if ADR_set == True:                     # Set the I2C address
            self._mraa_object.address(0x69)
        else:
            self._mraa_object.address(0x68)
            
    def getDeviceConnected(self):        
        """ Returns True if the device is connected, false otherwise """
        time.sleep(0.005)   # Wait 5ms  - test if needed!!!!
        try:                # If no device, mraa will throw an exception.
            # At register address 0x75 a constant of 0x68 is always returned.
            res = self._mraa_object.readReg(0x75)
            if res == 0x68:
                return True
            else:           # Other value -> other device at same I2C address
                return False
        except:             # mraa exception -> no device. Return False
            return False
    
    def ConfigureDevice(self):
        """ Once the device is connected, it must be configured """
        try:
            time.sleep(0.005)   # Wait 5ms  - test if needed!!!!          
            self._mraa_object.writeReg(0x6B, 0x03)  # Set PLL source from Z axis gyro
        except:     # Device disconnected in the meantime
            return
        
    def getAcceleractionXYZ(self):
        """ Get accelerometer values for axis X, Y and Z """
        try:
            x = self._mraa_object.readReg(0x3C)             # Read LSB of X axis
            x += 0x100 * self._mraa_object.readReg(0x3B)    # Read MSB of X axis
            if x > 0x7fff:      # Convert to signed int (16 bits)
                x = x - 65536
            
            y = self._mraa_object.readReg(0x3E)             # Read LSB of Y axis
            y += 0x100 * self._mraa_object.readReg(0x3D)    # Read MSB of Y axis
            if y > 0x7fff:      # Convert to signed int (16 bits)
                y = y - 65536
            
            z = self._mraa_object.readReg(0x40)             # Read LSB of Z axis
            z += 0x100 * self._mraa_object.readReg(0x3F)    # Read MSB of Z axis
            if z > 0x7fff:      # Convert to signed int (16 bits)
                z = z - 65536
        except:     # Device disconnected in the meantime
            return [0,0,0]  
        
        return [x, y, z]
    
    def getDevice(self):
        """ Return a string representing the device name. """
        return "MPU6050"

    """ The mraa object used to handle the I2C communication"""
    _mraa_object = None