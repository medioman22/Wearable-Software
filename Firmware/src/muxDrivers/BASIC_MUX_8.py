# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Driver file for the BASIC MUX. Switch for 8 mux channels.
"""
import Adafruit_BBIO.GPIO as GPIO
import threading                                                # Threading class for the threads

# Constants



class BasicMux8:
    """Implements a multiplexing functionality that can be switch for different devices."""

    # Name of the mux
    _name = "BASIC_MUX_8"

    # Types of the mux
    _types = ['Input', 'ADC']

    # Pins of the mux
    _pins = 3

    # Range of the mux
    _range = 8

    # Lock for the mux – One lock is created for all mux instances because they share all the same pins
    LOCK = threading.Lock()

    # Pin A
    _A = None

    # Pin B
    _B = None

    # Pin C
    _C = None

    # Detect pin
    _DETECT = None

    def __init__(self, pinConfig):
        """Initialize mux with pins (A,B,C,DETECT)."""
        if "A" not in pinConfig or pinConfig["A"] == None:
            raise ValueError('Pin A is invalid')
        if "B" not in pinConfig or pinConfig["B"] == None:
            raise ValueError('Pin B is invalid')
        if "C" not in pinConfig or pinConfig["C"] == None:
            raise ValueError('Pin C is invalid')
        if "DETECT" not in pinConfig or pinConfig["DETECT"] == None:
            raise ValueError('Pin DETECT is invalid')

        self._A = pinConfig["A"]                                    # Get pin A
        self._B = pinConfig["B"]                                    # Get pin B
        self._C = pinConfig["C"]                                    # Get pin C
        self._DETECT = pinConfig["DETECT"]                          # Get pin DETECT
        GPIO.setup(self._A, GPIO.OUT)                               # Init first select pin as output
        GPIO.output(self._A, GPIO.LOW)                              # Init first select pin to low
        GPIO.setup(self._B, GPIO.OUT)                               # Init second select pin as output
        GPIO.output(self._B, GPIO.LOW)                              # Init second select pin to low
        GPIO.setup(self._C, GPIO.OUT)                               # Init third select pin as output
        GPIO.output(self._C, GPIO.LOW)                              # Init third select pin to low
        GPIO.setup(self._DETECT, GPIO.IN, GPIO.PUD_DOWN)            # Init the detect pin and set it as input with pull down

    def cleanup(self):
        """Clean up driver when no longer needed."""
        pass


    def getMuxConnected(self):
        """Return True if the detect pin is High, False otherwise."""
        try:
            return GPIO.input(self._DETECT)
        except:
            print('Exception in mux connected')
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
        if muxedPin & 4 == 4:                                   # Test MSB bit set?
            GPIO.output(self._C, GPIO.HIGH)                     # Reflect change on pin C (MSB)
        else:
            GPIO.output(self._C, GPIO.LOW)

        if muxedPin & 2 == 2:                                   # Test middle bit set?
            GPIO.output(self._B, GPIO.HIGH)                     # Reflect change on pin B (middle)
        else:
            GPIO.output(self._B, GPIO.LOW)

        if muxedPin & 1 == 1:                                   # Test LSB bit set?
            GPIO.output(self._A, GPIO.HIGH)                     # Reflect change on pin A (LSB)
        else:
            GPIO.output(self._A, GPIO.LOW)

    def deactivate(self):
        """Deactivate the previously activated MUX pin."""
        # TODO: UNLOCK
        self.LOCK.release()

    def getName(self):
        """Return mux name."""
        return '{}@MUX[{},{},{}]'.format(self._name, self._A, self._B, self._C)

    def getAbout(self):
        """Return device info."""
        return {
            'range': self._range,
            'types': self._types[:]
        }

    def comparePinConfig(self, pinConfig):
        """Check if the same pin config."""
        return ("A" in pinConfig and
                "B" in pinConfig and
                "C" in pinConfig and
                "DETECT" in pinConfig and
                pinConfig["A"] == self._A and
                pinConfig["B"] == self._B and
                pinConfig["C"] == self._C and
                pinConfig["DETECT"] == self._DETECT);
