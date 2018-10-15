# -*- coding: utf-8 -*-
"""
SoftWEAR I2C module. Adds MUX features and hardware detection to normal I2C.
"""
import time                                                     # Time keeping module to get timestamps

from Config import PIN_MAP                                      # SoftWEAR Config module.
from MuxModule import Mux                                       # SoftWEAR MUX module.

from I2C_BNO055 import BNO055                                   # Driver module for the BNO055 device
#import I2C_MPU6050                                             # Driver for the MPU6050 device


"""
DEDICATED I2C MULTIPLEXER
https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/overview
"""

# Create a MUX shadow instance as there is only one Mux
MuxShadow = Mux()

# List of all possible drivers
DRIVERS = [BNO055]

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

    def updateValues(self):
        """Update the values of the devices."""
        for device in self.connectedDevices:                    # Loop all connected devices
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if (device['mux'] == -1):                       # Unmuxed pin
                                                                # Match for drv and device
                    if device['name'] == drv.getName():
                        device['vals'] = drv.getValues()        # Update values
                        device['timestamp'] = time.time()       # Update timestamp
                # else:                                           # Match for drv and device
                #     if device['device'] == drv.getName():
                #         MuxShadow.activate(device['mux'])       # Activate mux pin
                #         device['vals'] = drv.getValues()        # Update values
                #         print(device['vals'])
                #         MuxShadow.deactivate()                  # Deactivate mux
                #         device['timestamp'] = time.time()       # Update timestamp


    def scan(self):
        """Update the connected devices dictionary list."""
        lastConnectedDrivers = self._connectedDrivers           # Keep last connected driver list
        self._connectedDrivers = []                             # Update connected drivers - start by clearing previous results
        self.connectedDevices = []                              # Update connected devices - start by clearing previous results

        for pinConfig in PIN_MAP["I2C"]:                        # Loop all available pin configs
            channel = pinConfig["CHANNEL"]                      # CHANNEL pin

            if not self.detectMux() or not MuxShadow.detect():  # Not a muxed pin or mux is not enabled
                for lastDrv in lastConnectedDrivers:            # Test last connected drivers
                                                                # Check if drv already loaded and still connected
                    if lastDrv.getChannel() == channel and lastDrv.getDeviceConnected():
                        self._connectedDrivers.append(lastDrv)  # Add to connected driver list
                        self.connectedDevices.append({  'channel': channel, # Add to connected device list
                                                        'mux': -1,
                                                        'name': lastDrv.getName(),
                                                        'settings': lastDrv.getSettings(),
                                                        'dir': lastDrv.getDir(),
                                                        'dim': lastDrv.getDim(),
                                                        'mode': lastDrv.getMode(),
                                                        'vals': [],
                                                        'timestamp': time.time()})
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
                                                        'settings': drv.getSettings(),
                                                        'dir': drv.getDir(),
                                                        'dim': drv.getDim(),
                                                        'mode': drv.getMode(),
                                                        'vals': [],
                                                        'timestamp': time.time()})
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


    def settings(self, settingsMessage):
        """Change settings of a device."""
        drv = None
        for el in self._connectedDrivers:                       # Check for driver
            print(el.getName(), settingsMessage['name'])
            if (el.getName() == settingsMessage['name']):
                drv = el
                break
        else:
            raise ReferenceError('Driver not registered')

        if ('mode' in settingsMessage):                         # Check for mode settings
            try:                                                # Try to set the mode
                drv.setMode(settingsMessage['mode'])
            except ValueError:
                raise ValueError                                # Pass on the value error
