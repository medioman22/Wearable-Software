# -*- coding: utf-8 -*-
"""
Representation of a connection to the physical board

Abstract definition of a physical board connection representation
"""

from abc import ABC, abstractmethod

"""Globals"""
# Possible connection states
possibleStatusTypes = ['Disconnected', 'Connected', 'Corrupted']
# Ingoing message types
possibleIncomingMessageTypes = ['Register', 'Deregister', 'D', 'CycleDuration', 'Ping']
# Outgoing message types
possibleOutgoingMessageTypes = ['Data', 'Ping', 'DeviceList', 'Set', 'Settings', 'Scan', 'Frequency']

class Message():
    """Message coming form the board."""

    # type of the message
    type = None
    # name of the device the message belongs
    name = None
    # data object for message
    data = None

    def __init__(self, type, name, data=None):
        """Create a new message."""
        self.type = type
        self.name = name
        self.data = data



class Connection(ABC):
    """Representation of a connection to the physical board."""

    # type
    _type = None
    # connection status
    _status = 'Disconnected'
    # connection ip
    _ip = None
    # connection port
    _port = None



    def __init__(self, type):
        """Configure the connection."""
        self._type = type

    @abstractmethod
    def __del__(self):
        """Class destructor. This is needed in order to stop any background threads."""
        pass

    @abstractmethod
    def __enter__(self):
        """Needed for usage like: 'with Connection() as c:'."""
        pass

    @abstractmethod
    def __exit__(self):
        """Needed for usage like: 'with Connection() as c:'."""
        pass

    @abstractmethod
    def connect(self):
        """Try to establish the connection."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the connection."""
        pass

    @abstractmethod
    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        pass

    @abstractmethod
    def sendMessages(self, messages):
        """Send a list of messages."""
        pass

    def type(self):
        """Get the type."""
        return self._type

    def status(self):
        """Get the status."""
        return self._status

    def ip(self):
        """Get the ip."""
        return self._ip

    def setIp(self, ip):
        """Set the ip (Does not affect the connection, needs reconnect)."""
        self._ip = ip

    def port(self):
        """Get the port."""
        return self._port

    def setPort(self, port):
        """Set the port (Does not affect the connection, needs reconnect)."""
        self._port = int(port)
