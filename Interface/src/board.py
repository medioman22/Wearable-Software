# -*- coding: utf-8 -*-
"""
A representation of the physical board connected.

Abstract definition of a physical board representation
"""

class Device():
    """Representation of a physical device."""

    # state
    _state = 0
    # state message
    _stateMessage = 'Offline'

    def __init__(self, name, dir='in', dim=1):
        """Configure a device."""
        # Set device name
        self._name = name;

        # Set device mode
        if (dir != 'in' and dir != 'out'):
            raise ValueError('dir has to be in list [in,out]')
        else:
            self._dir = dir

        # Set device value dimension
        self.dim = dim

        # Set data field
        self._data = []




    def name(self):
        """Return the name."""
        return self._name

    def state(self):
        """Return the state."""
        return self._state, self._stateMessage

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
        if (self._mode != 'out'):
            raise ValueError('device has now permission to write data')
        else:
            self._data = data


class Board():
    """Representation of a physical board."""

    # connection state
    _connected = False
    # busy flag
    _busy = False
    # name
    _name = 'Unknown device'
    # default ip
    _defaultIp = '0.0.0.0'
    # devices
    _deviceList = None


    def __init__(self, name="Unknown Device"):
        """Configure a board."""
        self._name = name;
        self._defaultIp = '192.168.7.2'
        self._deviceList = []


    def name(self):
        """Return the name."""
        return self._name

    def defaultIp(self):
        """Return the default ip."""
        return self._defaultIp

    def connected(self):
        """Return the connected state."""
        return self._connected

    def deviceList(self):
        """Return a shallow copy of the device list."""
        return self._deviceList.copy()


    def processIncomingMessage(self, message):
        """Process incoming message."""
        print(message) # Abstract
