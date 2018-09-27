# -*- coding: utf-8 -*-
"""
Representation of a mocked connection to the physical board

A mocked connection to a mocked board
"""

from connections.connection import Connection, Message
import random



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

        # Reset data generating functions
        global devicesRegistered
        devicesRegistered = False

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        return defaultBehaviour()

    def sendMessages(self, messages):
        """Send a list of messages."""
        pass # Sending messages is not implemented in the mocked connection

    def getState(self):
        """Get the connection state."""
        return self._state



devicesRegistered = False
def defaultBehaviour():
    """Register some devices and then feed values."""
    # Add devices
    global devicesRegistered
    if (devicesRegistered == False):
        registerDeviceMessages = []
        registerDeviceMessages.append(Message('Register','Mocked Device 1', {'dir': 'in', 'dim': 1}))
        registerDeviceMessages.append(Message('Register','Mocked Device 2', {'dir': 'in', 'dim': 1}))
        registerDeviceMessages.append(Message('Register','Mocked Device 3', {'dir': 'in', 'dim': 2}))
        registerDeviceMessages.append(Message('Register','Mocked Device 4', {'dir': 'in', 'dim': 3}))

        devicesRegistered = True
        return registerDeviceMessages
    # Report values
    else:
        dataMessages = []
        dataMessages.append(Message('Data','Mocked Device 1', [random.random()]))
        dataMessages.append(Message('Data','Mocked Device 2', [random.randint(1,101)]))
        dataMessages.append(Message('Data','Mocked Device 3', [random.uniform(1,101),random.uniform(-100,0)]))
        dataMessages.append(Message('Data','Mocked Device 4', [random.uniform(1,11),random.uniform(11,21),random.uniform(21,31)]))

        return dataMessages
