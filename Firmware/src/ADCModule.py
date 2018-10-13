# -*- coding: utf-8 -*-
"""
SoftWEAR ADC module.

Adds ADC features and hardware detection capabilities
"""

import time                                                     # Time keeping module to get timestamps
import Adafruit_BBIO.GPIO as GPIO                               # Main peripheral class. Implements GPIO communication

from Config import PIN_MAP                                      # SoftWEAR Config module.
from MuxModule import Mux                                       # SoftWEAR MUX module.

from ADC_BASIC import ADCBasic                                  # Driver module for basic ADC

# TODO: Special drivers for ADCs

# Create a MUX shadow instance as there is only one Mux
MuxShadow = Mux()

# List of all possible drivers
DRIVERS = [ADCBasic]

class ADC:
    """Implements basic input functionality."""

    # List of all connected drivers
    _connectedDrivers = []

    # List of connected devices dictionary. Contains: {chn, subchn, val, cnt, actv}. Subchannel is -1 in case no MUX is connected.
    connectedDevices = []

    def __init__(self):
        """
        Class constructor.

            Initialises the module with the hardware options. This includes the scan pins and the possible MUX objects.
        """
        for pinConfig in PIN_MAP["ADC"]:                        # Loop all available pin configs
            muxSwitch = pinConfig["MUX"]                        # MUX switch pin
            if muxSwitch != None:
                GPIO.setup(muxSwitch, GPIO.IN, GPIO.PUD_DOWN)   # Setup detect pin

    def detectMux(self, pin):
        """Detect if a pin is active."""
        if (pin == None):                                       # Not a mux switch pin
            return False
        else:
            return GPIO.input(pin)                              # Read the value


    def updateValues(self):
        """Update the values of the devices."""
        for device in self.connectedDevices:                    # Loop all connected devices
            for drv in self._connectedDrivers:                  # Loop all connected drivers
                if (device['mux'] == -1):                       # Unmuxed pin
                                                                # Match for drv and device
                    if device['device'] == '{}@ADC[{}]'.format(drv.getDevice(), drv.getPin()):
                        device['vals'] = drv.getValues()        # Update values
                        device['timestamp'] = time.time()       # Update timestamp
                else:
                                                                # Match for drv and device
                    if device['device'] == '{}@ADC[{}:{}]'.format(drv.getDevice(), drv.getPin(), drv.getMuxedPin()):
                        MuxShadow.activate(device['mux'])       # Activate mux pin
                        device['vals'] = drv.getValues()        # Update values
                        MuxShadow.deactivate()                  # Deactivate mux
                        device['timestamp'] = time.time()       # Update timestamp



    def scan(self):
        """Update the connected devices dictionary list."""
        lastConnectedDrivers = self._connectedDrivers           # Keep last connected driver list
        self._connectedDrivers = []                             # Update connected drivers - start by clearing previous results
        self.connectedDevices = []                              # Update connected devices - start by clearing previous results

        for pinConfig in PIN_MAP["ADC"]:                        # Loop all available pin configs
            pin = pinConfig["DATA"]                             # DATA pin
            muxSwitch = pinConfig["MUX"]                        # MUX switch pin

            if not self.detectMux(muxSwitch) or not MuxShadow.detect(): # Not a muxed pin or mux is not enabled
                for lastDrv in lastConnectedDrivers:            # Test last connected drivers
                                                                # Check if drv already loaded and still connected
                    if lastDrv.getPin() == pin and lastDrv.getDeviceConnected():
                        self._connectedDrivers.append(lastDrv)  # Add to connected driver list
                        self.connectedDevices.append({  'pin': pin, # Add to connected device list
                                                        'mux': -1,
                                                        'device': '{}@ADC[{}]'.format(lastDrv.getDevice(), pin),
                                                        'dir': lastDrv.getDir(),
                                                        'dim': lastDrv.getDim(),
                                                        'vals': [],
                                                        'timestamp': time.time()})
                        break                                   # Break to next device
                else:                                           # Try new drivers if no existing was found
                    for DRIVER in DRIVERS:                      # Test all drivers
                        drv = DRIVER(pin)                       # Test the different drivers
                        if not drv.getDeviceConnected():        # Validate driver connected
                            continue                            # Try next driver until none is left
                        drv.configureDevice()                   # Configure device
                        self._connectedDrivers.append(drv)      # Add to connected driver list
                        self.connectedDevices.append({  'pin': pin, # Add to connected device list
                                                        'mux': -1,
                                                        'device': '{}@ADC[{}]'.format(drv.getDevice(), pin),
                                                        'dir': drv.getDir(),
                                                        'dim': drv.getDim(),
                                                        'vals': [],
                                                        'timestamp': time.time()})
                        break                                   # Break to next device
                    else:
                        pass                                    # No suitable driver has been found
            else:
                for muxedPin in range(Mux.range):               # Loop all muxed pins
                    MuxShadow.activate(muxedPin)                # Activate mux pin
                    for lastDrv in lastConnectedDrivers:        # Test last connected drivers
                                                                # Check if drv already loaded and still connected
                        if lastDrv.getPin() == pin and lastDrv.getMuxedPin() == muxedPin and lastDrv.getDeviceConnected():
                            self._connectedDrivers.append(lastDrv) # Add to connected driver list
                            self.connectedDevices.append({  'pin': pin, # Add to connected device list
                                                            'mux': muxedPin,
                                                            'device': '{}@ADC[{}:{}]'.format(lastDrv.getDevice(), pin, muxedPin),
                                                            'dir': lastDrv.getDir(),
                                                            'dim': lastDrv.getDim(),
                                                            'vals': [],
                                                            'timestamp': time.time()})
                            break                               # Break to next device
                    else:                                       # Try new drivers if no existing was found
                        for DRIVER in DRIVERS:                  # Test all drivers
                            drv = DRIVER(pin, muxedPin)         # Test the different drivers
                            if not drv.getDeviceConnected():    # Validate driver connected
                                continue                        # Try next driver until none is left
                            drv.configureDevice()               # Configure device
                            self._connectedDrivers.append(drv)  # Add to connected driver list
                            self.connectedDevices.append({  'pin': pin, # Add to connected device list
                                                            'mux': muxedPin,
                                                            'device': '{}@ADC[{}:{}]'.format(drv.getDevice(), pin, muxedPin),
                                                            'dir': drv.getDir(),
                                                            'dim': drv.getDim(),
                                                            'vals': [],
                                                            'timestamp': time.time()})
                            break                               # Break to next device
                        else:
                            pass                                # No suitable driver has been found
                    MuxShadow.deactivate()                      # Deactivate mux
