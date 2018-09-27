# -*- coding: utf-8 -*-
"""
A representation of the connection to the physical board.

Abstract definition of a connection to the physical board representation
"""

"""Globals"""
# Allowed directions for the dataflow
allowedDirTypes = ['in', 'out']

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
        """Return the data[s]."""
        return self._data

    def setData(self, data):
        """Return the data(s)."""
        if (self._dir != 'out'):
            raise ValueError('device has now permission to write data')
        else:
            self._data = data


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

    def deviceList(self):
        """Return a shallow copy of the device list."""
        return self._deviceList.copy()

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
                    self._deviceList.remove(device)
                    break
            else:
                raise ValueError('device is not registered')

    def updateData(self, name, data):
        """Update data of a device."""
        for registeredDevice in self._deviceList:
            if (registeredDevice.name() == name):
                # Access private field of 'friend' object
                registeredDevice._data = data
                break
        else:
            raise ValueError('device is not registered')

    def reset(self):
        """Reset the board to default."""
        self._deviceList = []
