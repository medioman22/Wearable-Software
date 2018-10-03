# -*- coding: utf-8 -*-
"""
Representation of a tcp/ip connection to the physical board

A tcp/ip connection to a physical board
"""

from connections.connection import Connection




class TCPIPConnection(Connection):
    """Representation of a tcp/ip connection to the physical board."""

    def __init__(self):
        """Configure the tcp/ip connection."""
        super().__init__('TCP/IP')

    def __del__(self):
        """Class destructor. This is needed in order to stop any background threads."""
        pass

    def __enter__(self):
        """Needed for usage like: 'with Connection() as c:'."""
        return self

    def __exit__(self):
        """Needed for usage like: 'with Connection() as c:'."""
        pass

    def connect(self):
        """Try to establish the connection."""
        raise ConnectionError('Not Implmented')

    def disconnect(self):
        """Close the connection."""
        pass

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        pass

    def sendMessages(self, messages):
        """Send a list of messages."""
        pass

    def getState(self):
        """Get the connection state."""
        return self._state
