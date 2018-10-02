# -*- coding: utf-8 -*-
"""
A representation of the connection to the physical board.

Abstract definition of a connection to the physical board representation
"""

import datetime

"""Globals"""
# Allowed directions for the dataflow
allowedDirTypes = ['in', 'out']
# Max past points stored
maxPoints = 256

class Device():
    """Representation of a physical device."""

    # name
    _name = 'Unknown Device'
    # direction
    _dir = 'in'
    # dimension (length of value vector)
    _dim = 1
    # data (Accessible by the 'friend' object board)
    _data = None
    # Past data values
    _pastData = None
    # Functions
    _functions = None
    # Parameters
    _parameters = None
    # Start timestamps
    _startTimestamps = None
    # Whether the function is running four outgoing device
    _functionRunning = None
    # Save to file
    _fileName = None



    def __init__(self, name="Unknown Device", dir=allowedDirTypes[0], dim=1):
        """Configure a device."""
        # Set device name
        self._name = name;

        # Set device mode
        if (dir not in allowedDirTypes):
            raise ValueError("dir has to be in list: {}".format(allowedDirTypes))
        else:
            self._dir = dir

        # Set device value dimension
        if (dim <= 0):
            raise ValueError("dim '{}' has to be positive".format(dim))
        elif (isinstance(dim, int) == False):
            raise ValueError("dim '{}' has to be an int".format(dim))
        else:
            self._dim = dim

        # Set data field
        self._data = []
        self._pastData = [[] for x in range(dim)]

        # Set functions
        self._functions = [None for x in range(dim)]
        self._parameters = [None for x in range(dim)]
        self._startTimestamps = [None for x in range(dim)]
        self._functionRunning = False


    def name(self):
        """Return the name."""
        return self._name

    def dir(self):
        """Return the dir."""
        return self._dir

    def dim(self):
        """Return the dim."""
        return self._dim

    def data(self):
        """Return the data list."""
        return self._data

    def pastData(self):
        """Return a shallow copy of the past data lists."""
        return self._pastData.copy()

    def function(self, i):
        """Return the function."""
        return self._functions[i], self._parameters[i], self._startTimestamps[i]

    def functionRunning(self):
        """Return whether the function is running."""
        return self._functionRunning

    def fileName(self):
        """Return the file name."""
        return self._fileName

    def setFunction(self, dim, function, parameters):
        """Set a function and parameters."""
        if (self._dir != 'out'):
            raise ValueError('device has now permission to send data')
        else:
            print(dim, function, parameters)
            self._functions[dim] = function
            self._parameters[dim] = parameters
            # Set t=0
            self._startTimestamps[dim] = datetime.datetime.now()

    def setFunctionRunning(self, running):
        """Set a function running."""
        if (self._dir != 'out'):
            raise ValueError('device has now permission to send data')
        else:
            # Set t=0
            for i in range(self._dim):
                self._startTimestamps[i] = datetime.datetime.now()
            self._functionRunning = running

    def setData(self, data):
        """Set data for device."""
        if (self._dir != 'out'):
            raise ValueError('device has now permission to send data')
        else:
            for i, dataI in enumerate(self._data):
                # Add current data to past data
                self._pastData[i].append(dataI)
                # Create overflow for past self
                while (maxPoints < len(self._pastData[i])):
                    self._pastData[i].pop(0)

            # Set new data
            self._data = data

    def setFileName(self, fileName):
        """Set the file name."""
        self._fileName = fileName



class Board():
    """Representation of a physical board."""

    # name
    _name = None
    # connection type
    _connectionType = None
    # default ip
    _defaultIp = None
    # default port
    _defaultPort = None
    # devices
    _deviceList = None
    # Save to file
    _fileName = None


    def __init__(self, name, connectionType, defaultIp='192.168.7.2', defaultPort='12345'):
        """Configure the board."""
        self._name = name
        self._connectionType = connectionType
        self._defaultIp = defaultIp
        self._defaultPort = defaultPort
        self._deviceList = [] # Empty list


    def name(self):
        """Return the name."""
        return self._name

    def connectionType(self):
        """Return the connection type."""
        return self._connectionType

    def defaultIp(self):
        """Return the default ip."""
        return self._defaultIp

    def defaultPort(self):
        """Return the default port."""
        return self._defaultPort

    def serializeMessage(self, message):
        """Return serialized message as string."""
        return None

    def unserializeMessage(self, message):
        """Return parsed message as dict."""
        return None

    def deviceList(self):
        """Return a shallow copy of the device list."""
        return self._deviceList.copy()

    def fileName(self):
        """Return the file name."""
        return self._fileName

    def setFileName(self, fileName):
        """Set the file name."""
        self._fileName = fileName

    def registerDevice(self, device):
        """Register a device to the board."""
        if (not isinstance(device, Device)):
            raise ValueError('object is not a device')
        else:
            self._deviceList.append(device)

    def deregisterDevice(self, device):
        """Register a device to the board."""
        if (not isinstance(device, Device)):
            raise ValueError('object is not a device')
        else:
            for registeredDevice in self._deviceList:
                if (registeredDevice.name() == device.name()):
                    self._deviceList.remove(registeredDevice)
                    break
            else:
                raise ValueError('device is not registered')

    def updateData(self, name, data):
        """Update data of a device."""
        for registeredDevice in self._deviceList:
            if (registeredDevice.name() == name):
                # Access private field of 'friend' object
                for i, dataI in enumerate(registeredDevice._data):
                    # Add current data to past data
                    registeredDevice._pastData[i].append(dataI)
                    # Create overflow for past values
                    while (maxPoints < len(registeredDevice._pastData[i])):
                        registeredDevice._pastData[i].pop(0)

                # Set new data
                registeredDevice._data = data


                break
        else:
            raise ValueError('device is not registered')

    def reset(self):
        """Reset the board to default."""
        self._deviceList = []
