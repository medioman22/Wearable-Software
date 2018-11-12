# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
SoftWEAR I2C module. Adds MUX features and hardware detection to normal I2C.
"""

from Config import PIN_MAP                                      # SoftWEAR Config module.
from MuxModule import GetMux                                    # SoftWEAR MUX module.

from drivers.I2C_BNO055 import BNO055                           # Driver module for the BNO055 device
from drivers.I2C_PCA9685 import PCA9685                         # Driver module for the PCA9685 device
#import I2C_MPU6050                                             # Driver for the MPU6050 device


"""
DEDICATED I2C MULTIPLEXER
https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/overview
"""

# Create a MUX shadow instance as there is only one Mux
MuxModule = GetMux()

# List of all possible drivers
DRIVERS = [BNO055, PCA9685]

class I2C:
    """Implements I2C functionality."""

    # List of all connected drivers
    _connectedDrivers = []

    # List of connected devices dictionary
    connectedDevices = []


    def __init__(self):
        """Initialize the device drivers and the MUX object associated with I2C."""
        pass

    def detectMux(self):
        """Detect if a mux is active."""
        return False # TODO: Implement mux for I2C

    def scan(self):
        """Update the connected devices dictionary list."""
        lastConnectedDrivers = self._connectedDrivers[:]        # Keep last connected driver list
        connectedDrivers = []                                   # New connected driver list
        connectedDevices = []                                   # New connected devices list
        disconnectedDriver = []                                 # Disconnected drivers

        muxList = MuxModule.listFor('I2C')                      # Get a list of muxes registered for I2C

        for pinConfig in PIN_MAP["I2C"]:                        # Loop all available pin configs
            if len(muxList) == 0:                               # Non muxed i2c channels
                for lastDrv in lastConnectedDrivers:            # Test last connected drivers
                                                                # Check if drv already loaded and still connected
                    if not lastDrv.getDeviceConnected():        # Device is disconnected
                        disconnectedDriver.append(lastDrv)
                    elif lastDrv.comparePinConfig(pinConfig):   # Device still connected
                        connectedDrivers.append(lastDrv)        # Add to connected driver list
                        connectedDevices.append({   'address': pinConfig["ADDRESS"], # Add to connected device list
                                                    'bus': pinConfig["BUSNUM"],
                                                    'mux': -1,
                                                    'name': lastDrv.getName(),
                                                    'about': lastDrv.getAbout(),
                                                    'settings': lastDrv.getSettings(),
                                                    'dir': lastDrv.getDir(),
                                                    'dim': lastDrv.getDim(),
                                                    'mode': lastDrv.getMode(),
                                                    'frequency': lastDrv.getFrequency(),
                                                    'dutyFrequency': lastDrv.getDutyFrequency(),
                                                    'flags': lastDrv.getFlags(),
                                                    'val': 0,
                                                    'vals': [],
                                                    'cycle': 0})
                        break                                   # Break to next device
                else:                                           # Try new drivers if no existing was found
                    for DRIVER in DRIVERS:                      # Test all drivers
                        drv = DRIVER(pinConfig)                 # Test the different drivers
                        if not drv.getDeviceConnected():        # Validate driver connected
                            continue                            # Try next driver until none is left
                        drv.configureDevice()                   # Configure device
                        connectedDrivers.append(drv)            # Add to connected driver list
                        connectedDevices.append({   'address': pinConfig["ADDRESS"], # Add to connected device list
                                                    'bus': pinConfig["BUSNUM"],
                                                    'mux': -1,
                                                    'name': drv.getName(),
                                                    'about': drv.getAbout(),
                                                    'settings': drv.getSettings(),
                                                    'dir': drv.getDir(),
                                                    'dim': drv.getDim(),
                                                    'mode': drv.getMode(),
                                                    'frequency': drv.getFrequency(),
                                                    'dutyFrequency': drv.getDutyFrequency(),
                                                    'flags': drv.getFlags(),
                                                    'val': 0,
                                                    'vals': [],
                                                    'cycle': 0})
                        break                                   # Break to next device
                    else:
                        pass                                    # No suitable driver has been found
            else:                                               # Muxes have been detected
                for muxName in muxList:                         # Loop all mux channels
                    if MuxModule.detect(muxName):               # Check if mux is detected
                        muxRange = MuxModule.about(muxName)['range'] # Get mux range
                        for muxedChannel in range(muxRange):    # Loop all muxed channels
                            for lastDrv in lastConnectedDrivers: # Test last connected drivers
                                if not lastDrv.comparePinConfig(pinConfig, muxedChannel): # Wrong driver
                                    pass
                                                                # Check if drv already loaded and still connected
                                elif not lastDrv.getDeviceConnected(): # Device is disconnected
                                    print('remove', lastDrv.getName())
                                    disconnectedDriver.append(lastDrv)
                                else:                           # Device still connected
                                    connectedDrivers.append(lastDrv) # Add to connected driver list
                                    connectedDevices.append({   'address': pinConfig["ADDRESS"], # Add to connected device list
                                                                'bus': pinConfig["BUSNUM"],
                                                                'mux': muxedChannel,
                                                                'name': lastDrv.getName(),
                                                                'muxName': muxName,
                                                                'about': lastDrv.getAbout(),
                                                                'settings': lastDrv.getSettings(),
                                                                'dir': lastDrv.getDir(),
                                                                'dim': lastDrv.getDim(),
                                                                'mode': lastDrv.getMode(),
                                                                'frequency': lastDrv.getFrequency(),
                                                                'dutyFrequency': lastDrv.getDutyFrequency(),
                                                                'flags': lastDrv.getFlags(),
                                                                'val': 0,
                                                                'vals': [],
                                                                'cycle': 0})
                                    break                       # Break to next device
                            else:                               # Try new drivers if no existing was found
                                for DRIVER in DRIVERS:          # Test all drivers
                                    drv = DRIVER(pinConfig, muxedChannel, muxName) # Test the different drivers
                                    if not drv.getDeviceConnected(): # Validate driver connected
                                        continue                # Try next driver until none is left
                                    print('add', drv.getName())
                                    drv.configureDevice()       # Configure device
                                    connectedDrivers.append(drv) # Add to connected driver list
                                    connectedDevices.append({   'address': pinConfig["ADDRESS"], # Add to connected device list
                                                                'bus': pinConfig["BUSNUM"],
                                                                'mux': muxedChannel,
                                                                'name': drv.getName(),
                                                                'muxName': muxName,
                                                                'about': drv.getAbout(),
                                                                'settings': drv.getSettings(),
                                                                'dir': drv.getDir(),
                                                                'dim': drv.getDim(),
                                                                'mode': drv.getMode(),
                                                                'frequency': drv.getFrequency(),
                                                                'dutyFrequency': drv.getDutyFrequency(),
                                                                'flags': drv.getFlags(),
                                                                'val': 0,
                                                                'vals': [],
                                                                'cycle': 0})
                                    break                       # Break to next device
                                else:
                                    pass                        # No suitable driver has been found
        for drv in disconnectedDriver:                          # Clean up disconnected drivers
            drv.cleanup()
        self._connectedDrivers = connectedDrivers
        self.connectedDevices = connectedDevices

    def getValues(self):
        """Get values of a device."""
        for device in self.connectedDevices:                    # Loop all connected devices
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if device['name'] == drv.getName():             # Match for drv and device
                    values = drv.getValues()                    # Get last values from device and clear them
                    cycleDuration = drv.getCycleDuration()      # Get cycle duration for driver
                    if len(values) > 0:                         # Check if new data is available
                        device['val'] = values[-1][1]           # Get most recent value
                        device['vals'] = values                 # Get all new values
                        device['cycle'] = cycleDuration         # Get cycle duration


    def setValue(self, name, dim, value):
        """Set value for dim of a device."""
        for drv in self._connectedDrivers:                      # Check for driver
            if (drv.getName() == name):                         # If driver exists, set the value
                drv.setValue(dim, value)
                break

    def settings(self, settingsMessage):
        """Change settings of a device."""
        drv = None
        for el in self._connectedDrivers:                       # Check for driver
            if (el.getName() == settingsMessage['name']):
                drv = el
                break
        else:
            return

        if ('mode' in settingsMessage):                         # Check for mode settings
            try:                                                # Try to set the mode
                drv.setMode(settingsMessage['mode'])
            except ValueError:
                raise ValueError                                # Pass on the value error

        if ('flag' in settingsMessage):                         # Check for flag settings
            try:                                                # Try to set the flag
                drv.setFlag(settingsMessage['flag'], settingsMessage['value'])
            except ValueError:
                raise ValueError                                # Pass on the value error

        if ('frequency' in settingsMessage):                    # Check for frequency settings
            try:                                                # Try to set the frequency
                drv.setFrequency(settingsMessage['frequency'])
            except ValueError:
                raise ValueError                                # Pass on the value error

        if ('dutyFrequency' in settingsMessage):                # Check for dutyFrequency settings
            try:                                                # Try to set the duty frequency
                drv.setDutyFrequency(settingsMessage['dutyFrequency'])
            except ValueError:
                raise ValueError                                # Pass on the value error
