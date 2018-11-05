# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
SoftWEAR Multiplexer module.

    Uses device SN74LV4051A as an analog multiplexer
    with 8 channels. The high level class implements potential MUXes on multiple
    channels. Hardware detection feature provided.
"""

import threading                                                # Threading class for the thread locks
import Adafruit_BBIO.GPIO as GPIO                               # Main peripheral class. Implements GPIO communication

from Config import PIN_MAP                                      # SoftWEAR Config module.

# Constants
MUX_ADDRESS_LENGTH = 3                                          # How many pin are needed to address
MUX_RANGE = 8                                                   # How many pins can me muxed


class Mux:
    """Implements a multiplexing functionality that can be switch for different devices."""

    # Lock for the mux – One lock is created for all mux instances because they share all the same pins
    LOCK = threading.Lock()

    # Pin A
    _A = PIN_MAP["MUX"]["A"]

    # Pin B
    _B = PIN_MAP["MUX"]["B"]

    # Pin C
    _C = PIN_MAP["MUX"]["C"]

    # Detect pin
    _DETECT = PIN_MAP["MUX"]["DETECT"]

    # Range of the mux
    range = MUX_RANGE

    GPIO.setup(_A, GPIO.OUT)                                    # Init first select pin as output
    GPIO.output(_A, GPIO.LOW)                                   # Init first select pin to low
    GPIO.setup(_B, GPIO.OUT)                                    # Init second select pin as output
    GPIO.output(_B, GPIO.LOW)                                   # Init second select pin to low
    GPIO.setup(_C, GPIO.OUT)                                    # Init third select pin as output
    GPIO.output(_C, GPIO.LOW)                                   # Init third select pin to low
    GPIO.setup(_DETECT, GPIO.IN, GPIO.PUD_DOWN)                 # Init the detect pin and set it as input with pull down

    def activate(self, muxedPin):
        """Activate a MUX pin (0-#). Any future operations will happen on this selected channel."""
        # TODO: CHECK IF IT IS NEEDED TO WAIT A BIT
        self.LOCK.acquire()

        if muxedPin < 0 or muxedPin > MUX_RANGE-1:              # Test parameter validity
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

    def detect(self):
        """Return True if the detect pin is High, False otherwise."""
        return GPIO.input(self._DETECT)


# class RoboMUX:
#     """Implements multiplexer capabilities for all possible channels of an peripheral."""
#
#     # Internal list of MUX objects. 1 MUX object per channel
#     _muxList = []
#
#     # Peripheral for which this MUX class is instantiated. Does not allow more than 1 peripheral per class instantiation.
#     _peripheral = ''
#
#     class MUX:
#         """Implements a single multiplexer for one peripheral channel."""
#
#         # Peripheral type. Can be: ADC, I2C, UART, SPI
#         peripheral = ''
#
#         # Channel of the connected peripheral
#         chn = '0'
#
#         # Select pins
#         _selectPins = None
#
#         # Detect pin
#         _detectPin = None
#
#         def __init__(self, peripheral, channel, selectPins, detectPin):
#             """Select pins are from LSB to MSB [A, B, C]."""
#             self.peripheral = peripheral                        # Save peripheral
#             self.chn = channel                                  # Save channel
#             if len(selectPins) is not 3:                        # Test input parameter validity
#                 raise ValueError("Parameter error: the MUX need exactly 3 select pins")
#
#             self._selectPins = selectPins                       # Save select pins
#             self._detectPin = detectPin                         # Save detect pin
#             GPIO.setup(selectPins[0], GPIO.OUT)                 # Init first select pin as output
#             GPIO.output(selectPins[0], GPIO.LOW)                # Init first select pin to low
#             GPIO.setup(selectPins[1], GPIO.OUT)                 # Init second select pin as output
#             GPIO.output(selectPins[1], GPIO.LOW)                # Init second select pin to low
#             GPIO.setup(selectPins[2], GPIO.OUT)                 # Init third select pin as output
#             GPIO.output(selectPins[2], GPIO.LOW)                # Init third select pin to low
#             GPIO.setup(detectPin, GPIO.IN)                      # Init the detect pin and set it as input
#
#         def select(self, muxChn):
#             """Select a MUX channel (0-7). Any future operations will happen on this selected channel."""
#             if muxChn < 0 or muxChn > 7:                        # Test parameter validity
#                 raise ValueError("Parameter error: the MUX has only 8 channels (0-7)")
#             if muxChn & 4 == 4:                                 # Test MSB bit set?
#                 GPIO.output(self._selectPins[2], GPIO.HIGH)     # Reflect change on pin C (MSB)
#             else:
#                 GPIO.output(self._selectPins[2], GPIO.LOW)
#
#             if muxChn & 2 == 2:                                 # Test middle bit set?
#                 GPIO.output(self._selectPins[1], GPIO.HIGH)     # Reflect change on pin B (middle)
#             else:
#                 GPIO.output(self._selectPins[1], GPIO.LOW)
#
#             if muxChn & 1 == 1:                                 # Test LSB bit set?
#                 GPIO.output(self._selectPins[0], GPIO.HIGH)     # Reflect change on pin A (LSB)
#             else:
#                 GPIO.output(self._selectPins[0], GPIO.LOW)
#
#         def isMuxConnected(self):
#             """Return True if the detect pin is High, False otherwise."""
#             return bool(GPIO.input(self._detectPin))
#
#     def __init__(self):
#         """MUX handler."""
#         self._muxList = []
#         self._peripheral = ''
#
#     def addMuxSlot(self, peripheral, channel, selectPins, detectPin):
#         """Add MUX slot."""
#         if peripheral not in ['ADC', 'I2C', 'UART', 'SPI' ]:
#             raise ValueError("Parameter error: peripheral should be ADC, I2C, UART or SPI")
#         # for pin in selectPins:
#         #     if pin not in util.gpio2mraa:
#         #         raise ValueError("Parameter error: Pin is not a valid GPIO pin")
#         #     if pin in util.UsedGPIO.pin_list:
#         #         raise ValueError("Parameter error: Pin is already used elsewhere")
#         # if detectPin not in util.gpio2mraa:
#         #     raise ValueError("Parameter error: Pin is not a valid GPIO pin")
#         # if detectPin in util.UsedGPIO.pin_list:
#         #     raise ValueError("Parameter error: Pin is already used elsewhere")
#
#         # if self._peripheral == '':
#         #     self._peripheral = peripheral
#         # elif self._peripheral != peripheral:
#         #     raise RuntimeError("Cannot mix MUX peripherals in the same class!")
#
#         newMux = self.MUX(peripheral, channel, selectPins, detectPin)
#         self._muxList.append(newMux)
#
#     def getMuxedValues(self, channel, func, *args, **kwargs):
#         """
#         Get muxed values.
#
#             Call the given function with all the arguments and returns a list
#             of all the return values. If no Mux connected, just returns the
#             func result.
#         """
#
#         cMux = [mux for mux in self._muxList if mux.chn == channel] # Get the MUX from the list for the given channel
#
#         if len(cMux) > 1:                                           # If more than 1 MUX -> signal error
#             raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
#         if len(cMux) == 0:                                          # If no MUX -> execute and return the function
#             return func(*args, **kwargs)
#
#         cMux = cMux[0]                                              # Just 1 MUX -> select it
#         ret = []                                                    # Initialize return object to an empty list
#
#         if cMux.isMuxConnected() == False:                          # If MUX exists but is disconnected -> execute and return the function
#             return func(*args, **kwargs)
#
#
#         for idx in range(0,8):                                      # If MUX exists and is connected -> go through all channels
#             cMux.select(idx)                                        # Select MUX channel than execute the function
#             ret.append(func(*args, **kwargs))
#         return ret                                                  # Return the results
#
#     def funcOnMuxChn(self, channel, muxChn, func, *args, **kwargs):
#         """
#         Execute function for MUX.
#
#             Executes and returns the given function on the provided MUX channel.
#             If no MUX is connected, just execute and return the function.
#         """
#         cMux = [mux for mux in self._muxList if mux.chn == channel] # Get the MUX from the list for the given channel
#
#         if len(cMux) > 1:                                           # If more than 1 MUX -> signal error
#             raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
#         if len(cMux) == 0:                                          # If no MUX -> execute and return the function
#             return func(*args, **kwargs)
#
#         cMux = cMux[0]                                              # Just 1 MUX -> select it
#         cMux.select(muxChn)                                         # Select the MUX channel
#         return func(*args, **kwargs)                                # Execute the function
#
#     def getMuxConnected(self, channel):
#         """Return True if the MUX is connected, False otherwise."""
#         cMux = [mux for mux in self._muxList if mux.chn == channel]
#
#         if len(cMux) > 1:                                           # If more than 1 MUX -> signal error
#             raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
#         if len(cMux) == 0:                                          # If no MUX -> execute and return the function
#             return False
#
#         cMux = cMux[0]                                              # Just 1 MUX -> select it
#         return cMux.isMuxConnected()
