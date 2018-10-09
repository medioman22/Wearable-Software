# -*- coding: utf-8 -*-
"""
SoftWEAR Multiplexer module.

    Uses device SN74LV4051A as an analog multiplexer
    with 8 channels. The high level class implements potential MUXes on multiple
    channels. Hardware detection feature provided.
"""

import mraa               # Main peripheral class. Implements basic digital I/O
import RoboUtil as util   # Utility library to keep track of used I/O pins

class RoboMUX:
    """Implements multiplexer capabilities for all possible channels of an peripheral."""

    class MUX:
        """Implements a single multiplexer for one peripheral channel."""

        def __init__(self, peripheral, channel, select_pins, detect_pin):
            """Select pins are from LSB to MSB [A, B, C]."""
            self.peripheral = peripheral    # Save peripheral
            self.chn = channel              # Save channel
            if len(select_pins) is not 3:   # Test input parameter validity
                raise ValueError("Parameter error: the MUX need exactly 3 select pins")

            # Init first select pin as output, and put it to 0
            self._pin_a = mraa.Gpio(util.gpio2mraa[select_pins[0]])
            self._pin_a.dir(mraa.DIR_OUT)
            self._pin_a.write(0)

            # Init second select pin as output, and put it to 0
            self._pin_b = mraa.Gpio(util.gpio2mraa[select_pins[1]])
            self._pin_b.dir(mraa.DIR_OUT)
            self._pin_b.write(0)

            # Init third select pin as output, and put it to 0
            self._pin_c = mraa.Gpio(util.gpio2mraa[select_pins[2]])
            self._pin_c.dir(mraa.DIR_OUT)
            self._pin_c.write(0)

            # Init the detect pin and set it as input
            self._pin_detect = mraa.Gpio(util.gpio2mraa[detect_pin])
            self._pin_detect.dir(mraa.DIR_IN)

        def select(self, mux_chn):
            """Select a MUX channel (0-7). Any future operations will happen on this selected channel."""
            if mux_chn < 0 or mux_chn > 7:  # Test parameter validity
                raise ValueError("Parameter error: the MUX has only 8 channels (0-7)")
            if mux_chn & 4 == 4:            # Test MSB bit set?
                self._pin_c.write(1)        # Reflect change on pin C (MSB)
            else:
                self._pin_c.write(0)

            if mux_chn & 2 == 2:            # Test middle bit set?
                self._pin_b.write(1)        # Reflect change on pin B (middle)
            else:
                self._pin_b.write(0)

            if mux_chn & 1 == 1:            # Test LSB bit set?
                self._pin_a.write(1)        # Reflect change on pin A (LSB)
            else:
                self._pin_a.write(0)

        def isMuxConnected(self):
            """Return True if the detect pin is High, False otherwise."""
            return bool(self._pin_detect.read())

        # The mraa pin objects used by the MUX
        _pin_a = None           # The LSB select pin
        _pin_b = None
        _pin_c = None           # The MSB select pin
        _pin_detect = None      # The detect pin

        # Peripheral type. Can be: ADC, I2C, UART, SPI
        peripheral = ''

        # Channel of the connected peripheral
        chn = '0'

    def __init__(self):
        """MUX handler."""
        self._mux_list = []
        self._peripheral = ''

    def add_mux_slot(self, peripheral, channel, select_pins, detect_pin):
        """Add MUX slot."""
        if peripheral not in ['ADC', 'I2C', 'UART', 'SPI' ]:
            raise ValueError("Parameter error: peripheral should be ADC, I2C, UART or SPI")
        for pin in select_pins:
            if pin not in util.gpio2mraa:
                raise ValueError("Parameter error: Pin is not a valid GPIO pin")
            if pin in util.UsedGPIO.pin_list:
                raise ValueError("Parameter error: Pin is already used elsewhere")
        if detect_pin not in util.gpio2mraa:
            raise ValueError("Parameter error: Pin is not a valid GPIO pin")
        if detect_pin in util.UsedGPIO.pin_list:
            raise ValueError("Parameter error: Pin is already used elsewhere")

        if self._peripheral == '':
            self._peripheral = peripheral
        elif self._peripheral != peripheral:
            raise RuntimeError("Cannot mix MUX peripherals in the same class!")

        new_mux = self.MUX(peripheral, channel, select_pins, detect_pin)
        self._mux_list.append(new_mux)

    def get_muxed_values(self, channel, func, *args, **kwargs):
        """
        Get muxed values.

            Call the given function with all the arguments and returns a list
            of all the return values. If no Mux connected, just returns the
            func result.
        """
        # Get the MUX from the list for the given channel
        c_mux = [mux for mux in self._mux_list if mux.chn == channel]

        if len(c_mux) > 1:  # If more than 1 MUX -> signal error
            raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
        if len(c_mux) == 0: # If no MUX -> execute and return the function
            return func(*args, **kwargs)

        c_mux = c_mux[0]    # Just 1 MUX -> select it
        ret = []            # Initialize return object to an empty list

        # If MUX exists but is disconnected -> execute and return the function
        if c_mux.isMuxConnected() == False:
            return func(*args, **kwargs)

        # If MUX exists and is connected -> go through all channels
        for idx in range(0,8):
            c_mux.select(idx)   # Select MUX channel than execute the function
            ret.append(func(*args, **kwargs))
        return ret              # Return the results

    def func_on_mux_chn(self, channel, mux_chn, func, *args, **kwargs):
        """
        Execute function for MUX.

            Executes and returns the given function on the provided MUX channel.
            If no MUX is connected, just execute and return the function.
        """
        # Get the MUX from the list for the given channel
        c_mux = [mux for mux in self._mux_list if mux.chn == channel]

        if len(c_mux) > 1:  # If more than 1 MUX -> signal error
            raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
        if len(c_mux) == 0: # If no MUX -> execute and return the function
            return func(*args, **kwargs)

        c_mux = c_mux[0]                # Just 1 MUX -> select it
        c_mux.select(mux_chn)           # Select the MUX channel
        return func(*args, **kwargs)    # Execute the function

    def get_mux_connected(self, channel):
        """Return True if the MUX is connected, False otherwise."""
        c_mux = [mux for mux in self._mux_list if mux.chn == channel]

        if len(c_mux) > 1:  # If more than 1 MUX -> signal error
            raise RuntimeError("The " + self._peripheral + " channel " + str(channel) + " has too many MUX objects!")
        if len(c_mux) == 0: # If no MUX -> execute and return the function
            return False

        c_mux = c_mux[0]    # Just 1 MUX -> select it
        return c_mux.isMuxConnected()

    # Internal list of MUX objects. 1 MUX object per channel
    _mux_list = []

    # Peripheral for which this MUX class is instantiated. Does not allow more than 1 peripheral per class instantiation.
    _peripheral = ''
