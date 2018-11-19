# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Driver file for the I2C TCA9548A MUX. Switch for 8 mux channels.
"""
import Adafruit_GPIO.I2C as I2C
import Adafruit_BBIO.GPIO as GPIO
import threading                                                # Threading class for the threads
import time                                                     # Time class for the waits


# Constants
TCA9548A_ADDRESS    = [0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77]
TCA9548A_BUSNUM     = [1, 2]


class I2CTCA9548AMux8:
    """Implements a multiplexing functionality that can be switch for different devices."""

    # Name of the mux
    _name = "I2C_TCA9548A_MUX_8"

    # Types of the mux
    _types = ['I2C']

    # Address of the mux
    _address = None

    # Bus num of the mux
    _busnum = None

    # Range of the mux
    _range = 8

    # Lock for the mux – One lock is created for all mux instances because they share all the same pins
    LOCK = threading.Lock()

    # Selected channel
    _selectedChannel = None

    # Device
    _device = None

    # Detect pin
    _DETECT = None

    def __init__(self, pinConfig):
        """Initialize mux with address and busnum."""
        if "ADDRESS" in pinConfig and pinConfig["ADDRESS"] == None or pinConfig["ADDRESS"] not in TCA9548A_ADDRESS:
            raise ValueError('address is invalid')
        if "BUSNUM" in pinConfig and pinConfig["BUSNUM"] == None or pinConfig["BUSNUM"] not in TCA9548A_BUSNUM:
            raise ValueError('busnum is invalid')

        self._address = pinConfig["ADDRESS"]                    # Get address
        self._busnum = pinConfig["BUSNUM"]                      # Get busnum
        self._DETECT = pinConfig["DETECT"]                      # Get detect pin

        self._device = I2C.get_i2c_device(self._address, self._busnum) # Init the I2C connection
        self._device.writeRaw8(0x0)                             # Test to write something
        GPIO.setup(self._DETECT, GPIO.IN, GPIO.PUD_DOWN)        # Init the detect pin and set it as input with pull down
        time.sleep(0.005)                                       # Wait a bit

    def cleanup(self):
        """Clean up driver when no longer needed."""
        try:
            self._device.writeRaw8(0x00)                        # Disable
        except:
            print('Exception in i2c mux cleanup')
            return


    def getMuxConnected(self):
        """Return True if the device is reachable."""
        try:
            return GPIO.input(self._DETECT)
        except:
            print('Exception in i2c mux conntected')
            return False

    def configureDevice(self):
        """Once the device is connected, it must be configured."""
        pass

    def activate(self, muxedPin):
        """Activate a MUX pin (0-#). Any future operations will happen on this selected channel."""
        # TODO: CHECK IF IT IS NEEDED TO WAIT A BIT
        self.LOCK.acquire()

        if muxedPin < 0 or muxedPin > self._range - 1:          # Test parameter validity
            raise ValueError("Parameter error: the MUX has only 8 channels (0-7)")
        self._selectedChannel = muxedPin                        # Set channel
        try:
            self._device.writeRaw8(0x01 << self._selectedChannel) # Set register
        except:
            print('Exception in i2c mux activate')
            pass

    def deactivate(self):
        """Deactivate the previously activated MUX pin."""
        # TODO: UNLOCK
        try:
            self._device.writeRaw8(0x00)
        except:
            print('Exception in i2c mux deactivate')
            pass                                                # Try to deactivate if possible
        self._selectedChannel = None
        self.LOCK.release()

    def getName(self):
        """Return mux name."""
        return '{}@MUX[{},{}]'.format(self._name, self._address, self._busnum)

    def getAbout(self):
        """Return device info."""
        return {
            'range': self._range,
            'types': self._types[:]
        }

    def comparePinConfig(self, pinConfig):
        """Check if the same pin config."""
        return ("ADDRESS" in pinConfig and
                "BUSNUM" in pinConfig and
                pinConfig["ADDRESS"] == self._address and
                pinConfig["BUSNUM"] == self._busnum);
