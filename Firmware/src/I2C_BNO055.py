# -*- coding: utf-8 -*-
"""
Driver file for the BNO055 accelerometer / gyroscope / magnetometer. Communicates
with the device via I2C and implements the basic functions for integrating into
the SoftWEAR package. 
"""
import mraa  # Main peripheral class. Implements I2C communication 
import time  # Imported for delay reasons

class BNO055:
    def __init__(self, chn, ADR_set = False):
        """ Class contstructor. Since device supports and address pin, one can
            represent this with a 'True' value of ADR_set. """
        self._mraa_object = mraa.I2c(chn)   # Create mraa I2C object
        if ADR_set == True:                 # Set the I2C address
            self._mraa_object.address(0x29)
        else:
            self._mraa_object.address(0x28)
            
    def getDeviceConnected(self):        
        """ Returns True if the device is connected, false otherwise """
        time.sleep(0.005)   # Wait 5ms  - test if needed!!!!
        try:                # If no device, mraa will throw an exception.
            # At register address 0x00 a constant of 0xA0 is always returned.
            res = self._mraa_object.readReg(0x00)
            if res == 0xA0:
                return True
            else:           # Other value -> other device at same I2C address
                return False
        except:             # mraa exception -> no device. Return False
            return False
    
    def ConfigureDevice(self):
        """ Once the device is connected, it must be configured """
        try:
            time.sleep(0.005)   # Wait 5ms  - test if needed!!!!           
            self._mraa_object.writeReg(0x3D, 0x00)  # Set device in configuration mode
            self._mraa_object.writeReg(0x3E, 0x00)  # Put device in normal power mode
            self._mraa_object.writeReg(0x3B, 0x01)  # Select default units
            time.sleep(0.005)   # Wait 5ms  - test if needed!!!!
            
            self._mraa_object.writeReg(0x3D, 0x08)  # Set device as IMU
        except:     # Device disconnected in the meantime
            return
        
    def getAcceleractionXYZ(self):
        """ Get accelerometer values for axis X, Y and Z """
        try:
            x = self._mraa_object.readReg(0x08)             # Read LSB of X axis
            x += 0x100 * self._mraa_object.readReg(0x09)    # Read MSB of X axis
            if x > 0x7fff:          # Convert to signed int (16 bits)
                x = x - 65536
            
            y = self._mraa_object.readReg(0x0A)             # Read LSB of Y axis
            y += 0x100 * self._mraa_object.readReg(0x0B)    # Read MSB of Y axis
            if y > 0x7fff:          # Convert to signed int (16 bits)
                y = y - 65536
            
            z = self._mraa_object.readReg(0x0C)             # Read LSB of Z axis
            z += 0x100 * self._mraa_object.readReg(0x0D)    # Read MSB of Z axis
            if z > 0x7fff:          # Convert to signed int (16 bits)
                z = z - 65536
        except:     # Device disconnected in the meantime
            return [0,0,0]  
        
        return [x, y, z]
    
    def getDevice(self):
        """ Return a string representing the device name. """
        return "BNO055"

    """ The mraa object used to handle the I2C communication"""
    _mraa_object = None