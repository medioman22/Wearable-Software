# -*- coding: utf-8 -*-
"""
Representation of a mocked connection to the physical board

A mocked connection to a mocked board
"""

from connections.connection import Connection




class MockedConnection(Connection):
    """Representation of a mocked connection to the mocked board."""

    def __init__(self):
        """Configure the mocked connection."""
        super().__init__('Mocked Connection')

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
        self._status = 'Connected'

    def disconnect(self):
        """Close the connection."""
        self._status = 'Disconnected'

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        pass

    def sendMessages(self, messages):
        """Send a list of messages."""
        pass # Sending messages is not implemented in the mocked connection

    def getState(self):
        """Get the connection state."""
        return self._state
