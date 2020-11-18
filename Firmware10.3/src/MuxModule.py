# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
SoftWEAR Multiplexer module.

    Uses device SN74LV4051A as an analog multiplexer
    with 8 channels. The high level class implements potential MUXes on multiple
    channels. Hardware detection feature provided.
"""

import Adafruit_BBIO.GPIO as GPIO                               # Main peripheral class. Implements GPIO communication

from Config import PIN_MAP                                      # SoftWEAR Config module.

from muxDrivers.BASIC_MUX_8 import BasicMux8                    # Driver module for basic mux
from muxDrivers.I2C_TCA9548A_MUX_8 import I2CTCA9548AMux8       # Driver module for i2c mux

################################################################
# WARNING: There is only one multiplexer allowed for INPUT and ANALOG
# List of all possible muxes
DRIVERS = [
    # One mux driver for INPUT and ANALOG
    BasicMux8,
    # n mux driver for I2C
    I2CTCA9548AMux8
]
################################################################

################################################################
# WARNING: Once a MUX has been connected, no other type of devices are allowed to be unmuxed.
# Only MUX are allowed to be on the unmuxed channel, as they cannot be distinguished if one mux channel us active.
################################################################


class Mux:
    """Implements basic mux functionality."""

    # List of all connected drivers
    _connectedDrivers = []

    # List of connected muxes dictionary. Contains: {}
    connectedMuxes = []

    def __init__(self):
        """
        Class constructor.

            Initialises the module with the hardware options.
        """

    def detectMux(self, pin):
        """Detect if a mux is active."""
        if (pin == None):                                       # Not a mux switch pin
            return False
        else:
            return GPIO.input(pin)                              # Read the value


    def scan(self):
        """Update the connected devices dictionary list."""
        lastConnectedDrivers = self._connectedDrivers[:]        # Keep last connected driver list
        connectedDrivers = []                                   # New connected driver list
        connectedMuxes = []                                     # New connected muxes list
        disconnectedDriver = []                                 # Disconnected drivers

        for pinConfig in PIN_MAP["MUX"]:                        # Loop all available pin configs
            for lastDrv in lastConnectedDrivers:                # Test last connected drivers
                                                                # Check if drv already loaded and still connected
                if not lastDrv.getMuxConnected():               # Device is disconnected
                    disconnectedDriver.append(lastDrv)
                elif lastDrv.comparePinConfig(pinConfig):       # Device still connected
                    connectedDrivers.append(lastDrv)            # Add to connected driver list
                    connectedMuxes.append({    'config': pinConfig,# Add to connected device list
                                                    'name': lastDrv.getName()})
                    break                                       # Break to next device
            else:                                               # Try new drivers if no existing was found
                for DRIVER in DRIVERS:                          # Test all drivers
                    try:
                        drv = DRIVER(pinConfig)                 # Test the different drivers
                    except:
                        continue
                    if not drv.getMuxConnected():               # Validate driver connected
                        continue                                # Try next driver until none is left
                    drv.configureDevice()                       # Configure device
                    connectedDrivers.append(drv)                # Add to connected driver list
                    connectedMuxes.append({    'config': pinConfig,# Add to connected device list
                                                    'name': drv.getName()})
                    break                                       # Break to next device
                else:
                    pass                                        # No suitable driver has been found
        for drv in disconnectedDriver:                          # Clean up disconnected drivers
            drv.cleanup()
        self._connectedDrivers = connectedDrivers
        self.connectedMuxes = connectedMuxes

    def activate(self, name, muxedPin):
        """Activate a MUX pin (0-#). Any future operations will happen on this selected channel."""
        for device in self.connectedMuxes:                      # Loop all connected muxes
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if name == drv.getName():                       # Match for drv and device
                    drv.activate(muxedPin)                      # Activate the pin on the mux
                    return

    def deactivate(self, name):
        """Deactivate the previously activated MUX pin."""
        for device in self.connectedMuxes:                      # Loop all connected muxes
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if name == drv.getName():                       # Match for drv and device
                    drv.deactivate()                            # Deactivate any pin on the mux
                    return

    def listFor(self, deviceType):
        """Return a list of connected muxes with device type (Input, ADC, I2C)."""
        muxes = []
        for device in self.connectedMuxes:                      # Loop all connected muxes
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if device['name'] == drv.getName():             # Match for drv and device
                    if (deviceType in drv.getAbout()['types']): # Check for the device type
                        muxes.append(drv.getName())             # Collect driver
        return muxes


    def detect(self, name):
        """Return True if the detect pin is High, False otherwise."""
        for device in self.connectedMuxes:                      # Loop all connected muxes
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if name == drv.getName():                       # Match for drv and device
                    return drv.getMuxConnected()                # Detect a mux

    def about(self, name):
        """Return information about the mux."""
        for device in self.connectedMuxes:                      # Loop all connected muxes
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if name == drv.getName():                       # Match for drv and device
                    return drv.getAbout()                       # Get information about mux

# Single mux
MUX = Mux()

def GetMux():
    """Get the single mux object."""
    return MUX
