# -*- coding: utf-8 -*-
"""
A representation of the connection to the physical board.

Abstract definition of a connection to the physical board representation
"""

import datetime                                                 # Time and date keeping package
import logging                                                  # This class logs all info - so logging is imported

"""Globals"""
# Allowed directions for the dataflow
allowedDirTypes = ['in', 'out']
# Max past points stored
maxPoints = 256

LOG_LEVEL_PRINT = logging.WARN
LOG_LEVEL_SAVE = logging.DEBUG


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
    # timestamp (Accessible by the 'friend' object board)
    _timestamp = None
    # Past data values
    _pastData = None
    # Past timestamps
    _pastTimestamps = None
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
    # Ignore device
    _ignore = False
    # The logger
    _logger = None


    def __init__(self, name="Unknown Device", dir=allowedDirTypes[0], dim=1):
        """Configure a device."""
        # Configure the logger
        self._logger = logging.getLogger('Device')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        fh = logging.FileHandler('../Logs/Device({}).log'.format(name), 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        self._logger.addHandler(fh)

        # Set device name
        self._name = name;

        # Validate dir values
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

        # Set data fields in respect to provided dimension
        self._data = []
        self._pastData = [[] for x in range(dim)]

        # Set timestamp fields
        self._timestamp = None
        self._pastTimestamps = []

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

    def timestamp(self):
        """Return the timestamp."""
        return self._timestamp

    def pastData(self):
        """Return a shallow copy of the past data lists."""
        return self._pastData.copy()

    def pastTimestamps(self):
        """Return a shallow copy of the past timestamp list."""
        return self._pastTimestamps.copy()

    def function(self, i):
        """Return the function."""
        return self._functions[i], self._parameters[i], self._startTimestamps[i]

    def functionRunning(self):
        """Return whether the function is running."""
        return self._functionRunning

    def fileName(self):
        """Return the file name."""
        return self._fileName

    def ignore(self):
        """Return the ignore flag."""
        return self._ignore

    def setFunction(self, dim, function, parameters):
        """Set a function and parameters."""
        if (self._dir != 'out'):                                # Function is only available for out devices
            raise ValueError('device has now permission to send data')
        else:
            self._functions[dim] = function                     # Set function type
            self._parameters[dim] = parameters                  # Set function parameter
            self._startTimestamps[dim] = datetime.datetime.now() # Set t=0

    def setFunctionRunning(self, running):
        """Set a function running."""
        if (self._dir != 'out'):                                # Function is only available for out devices
            raise ValueError('device has now permission to send data')
        else:
            for i in range(self._dim):
                self._startTimestamps[i] = datetime.datetime.now() # Set t=0
            self._functionRunning = running                     # Start function

    def setData(self, data):
        """Set data for device."""
        if (self._dir != 'out'):                                # Set data is only available for out devices
            raise ValueError('device has now permission to send data')
        else:
            for i, dataI in enumerate(self._data):              # Store new data
                self._pastData[i].append(dataI)                 # Add current data to past data
                while (maxPoints < len(self._pastData[i])):     # Create overflow for past data
                    self._pastData[i].pop(0)

            self._data = data                                   # Set most recent data

    def setFileName(self, fileName):
        """Set the file name."""
        self._fileName = fileName

    def setIgnore(self, ignore):
        """Set the ignore flag."""
        self._ignore = ignore



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
    # The logger
    _logger = None


    def __init__(self, name, connectionType, defaultIp='192.168.7.2', defaultPort='12345'):
        """Configure the board."""
        # Configure the logger
        self._logger = logging.getLogger('Board')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        fh = logging.FileHandler('../Logs/Board({}).log'.format(name), 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        self._logger.addHandler(fh)

        self._name = name
        self._connectionType = connectionType
        self._defaultIp = defaultIp
        self._defaultPort = defaultPort
        self._deviceList = []                                   # Clear device list


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
        if (not isinstance(device, Device)):                    # Only device objects can be registered
            raise ValueError('object is not a device')
        else:
            for registeredDevice in self._deviceList:           # Check for device to register
                if (registeredDevice.name() == device.name()):
                    break                                       # Device already registered
            else:
                self._deviceList.append(device)                 # Register device

    def deregisterDevice(self, device):
        """Register a device to the board."""
        if (not isinstance(device, Device)):                    # Only device objects can be deregistered
            raise ValueError('object is not a device')
        else:
            for registeredDevice in self._deviceList:           # Check for device to deregister
                if (registeredDevice.name() == device.name()):
                    self._deviceList.remove(registeredDevice)   # Remove from boards device lists
                    break
            else:                                               # Tried to deregister a non-registered device
                self._logger.debug('device {} is not registered'.format(device.name()))

    def updateData(self, name, data, timestamp):
        """Update data of a device."""
        for registeredDevice in self._deviceList:
            if (registeredDevice.name() == name):
                                                                # Add current timestamp to past timestamps of 'friend' object
                registeredDevice._pastTimestamps.append(registeredDevice._timestamp)
                while (maxPoints < len(registeredDevice._pastTimestamps)): # Create overflow for past timestamps of 'friend' object
                    registeredDevice._pastTimestamps.pop(0)
                for i, dataI in enumerate(registeredDevice._data): # Access private field of 'friend' object
                    registeredDevice._pastData[i].append(dataI) # Add current data to past data of 'friend' object
                    while (maxPoints < len(registeredDevice._pastData[i])): # Create overflow for past values of 'friend' object
                        registeredDevice._pastData[i].pop(0)

                registeredDevice._data = data                   # Set most recent data
                registeredDevice._timestamp = timestamp         # Set most recent timestamp


                break
        else:                                                   # Tried to update data for a non-registered device
            self._logger.debug('device {} is not registered'.format(name))

    def reset(self):
        """Reset the board to default."""
        self._deviceList = []                                   # Clear device list
