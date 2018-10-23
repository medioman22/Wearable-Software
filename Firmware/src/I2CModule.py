# -*- coding: utf-8 -*-
"""
SoftWEAR I2C module. Adds MUX features and hardware detection to normal I2C.
"""

from Config import PIN_MAP                                      # SoftWEAR Config module.
from MuxModule import Mux                                       # SoftWEAR MUX module.

from drivers.I2C_BNO055 import BNO055                           # Driver module for the BNO055 device
from drivers.I2C_PCA9685 import PCA9685                         # Driver module for the PCA9685 device
#import I2C_MPU6050                                             # Driver for the MPU6050 device


"""
DEDICATED I2C MULTIPLEXER
https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/overview
"""

# Create a MUX shadow instance as there is only one Mux
MuxShadow = Mux()

# List of all possible drivers
DRIVERS = [BNO055, PCA9685]

class I2C:
    """Implements I2C functionality."""

    # List of all connected drivers
    _connectedDrivers = []

    # List of connected devices dictionary. Contains: {chn, subchn, val, cnt, actv}. Subchannel is -1 in case no MUX is connected.
    connectedDevices = []


    def __init__(self):
        """Initialize the device drivers and the MUX object associated with I2C."""
        pass

    def detectMux(self):
        """Detect if a mux is active."""
        return False # TODO: Implement mux for I2C

    def scan(self):
        """Update the connected devices dictionary list."""
        lastConnectedDrivers = self._connectedDrivers           # Keep last connected driver list
        self._connectedDrivers = []                             # Update connected drivers - start by clearing previous results
        self.connectedDevices = []                              # Update connected devices - start by clearing previous results
        disconnectedDriver = []                                 # Disconnected drivers

        for pinConfig in PIN_MAP["I2C"]:                        # Loop all available pin configs
            channel = pinConfig["CHANNEL"]                      # CHANNEL pin

            if not self.detectMux() or not MuxShadow.detect():  # Not a muxed pin or mux is not enabled
                for lastDrv in lastConnectedDrivers:            # Test last connected drivers
                                                                # Check if drv already loaded and still connected
                    if not lastDrv.getDeviceConnected():        # Device is disconnected
                        disconnectedDriver.append(lastDrv)
                    elif lastDrv.getChannel() == channel:       # Device still connected
                        self._connectedDrivers.append(lastDrv)  # Add to connected driver list
                        self.connectedDevices.append({  'channel': channel, # Add to connected device list
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
                                                        'vals': []})
                        break                                   # Break to next device
                else:                                           # Try new drivers if no existing was found
                    for DRIVER in DRIVERS:                      # Test all drivers
                        drv = DRIVER(channel)                   # Test the different drivers
                        if not drv.getDeviceConnected():        # Validate driver connected
                            continue                            # Try next driver until none is left
                        drv.configureDevice()                   # Configure device
                        self._connectedDrivers.append(drv)      # Add to connected driver list
                        self.connectedDevices.append({  'channel': channel, # Add to connected device list
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
                                                        'vals': []})
                        break                                   # Break to next device
                    else:
                        pass                                    # No suitable driver has been found
            # else:
            #     pass
            #     for muxedChannel in range(Mux.range):           # Loop all muxed pins
            #         MuxShadow.activate(muxedChannel)            # Activate mux pin
            #         for lastDrv in lastConnectedDrivers:        # Test last connected drivers
            #                                                     # Check if drv already loaded and still connected
            #             if lastDrv.getChannel() == channel and lastDrv.getMuxedChannel() == muxedChannel and lastDrv.getDeviceConnected():
            #                 self._connectedDrivers.append(lastDrv) # Add to connected driver list
            #                 self.connectedDevices.append({  'channel': channel, # Add to connected device list
            #                                                 'mux': muxedChannel,
            #                                                 'device': '{}@I2C[{}:{}]'.format(lastDrv.getDevice(), channel, muxedChannel),
            #                                                 'dir': lastDrv.getDir(),
            #                                                 'dim': lastDrv.getDim(),
            #                                                 'vals': []})
            #                 break                               # Break to next device
            #         else:                                       # Try new drivers if no existing was found
            #             for DRIVER in DRIVERS:                  # Test all drivers
            #                 drv = DRIVER(channel, muxedChannel) # Test the different drivers
            #                 if not drv.getDeviceConnected():    # Validate driver connected
            #                     continue                        # Try next driver until none is left
            #                 drv.configureDevice()               # Configure device
            #                 self._connectedDrivers.append(drv)  # Add to connected driver list
            #                 self.connectedDevices.append({  'channel': channel, # Add to connected device list
            #                                                 'mux': muxedChannel,
            #                                                 'device': '{}@I2C[{}:{}]'.format(drv.getDevice(), channel, muxedChannel),
            #                                                 'dir': drv.getDir(),
            #                                                 'dim': drv.getDim(),
            #                                                 'vals': []})
            #                 break                               # Break to next device
            #             else:
            #                 pass                                # No suitable driver has been found
            #         MuxShadow.deactivate()                      # Deactivate mux
        for drv in disconnectedDriver:                          # Clean up disconnected drivers
            drv.cleanup()


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
