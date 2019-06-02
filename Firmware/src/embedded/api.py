# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Wearable Software Embedded API module. The Embedded API provided by this class is a shadow of the actual API and behaves exactly like it.
"""

import json                                                     # Serializing class. All objects sent are serialized
import logging                                                  # This class logs all info - so logging is imported
import time                                                     # For delays in the background thread

class APIConnection():
    """API connection."""

    # connection status
    _status = 'Connected'

    # Timeout in seconds. Affects the sending 'Sampling Period'
    _timeout = 0.1

    # The state of the socket (Initialized, Listening, Connected, Disconnected)
    _state = 'Connected'

    # The IP of the remote location
    _ip = '192.168.7.2'

    # The Application Port
    _port = 12345

    # In Messages
    _inMessages = None

    # Out Messages
    _outMessages = None

    def __init__(self):
        """Class constructor."""
        self._inMessages = []
        self._outMessages = []


    def __del__(self):
        """Class destructor. This is needed in order to stop the background thread."""

    def __enter__(self):
        """Needed for usage like: 'with APIConnection() as c:'."""
        return self

    def __exit__(self, type, value, traceback):
        """Needed for usage like: 'with APIConnection() as c:'."""
        pass


    def connect(self):
        """Start the connection."""
        self._state = 'Connected'
        time.sleep(0.5)


    def disconnect(self):
        """Close the connection."""
        self._state = 'Disconnected'
        time.sleep(0.5)


    def stopAndFreeResources(self):
        """Stop the background thread and shuts down the socket and log."""
        self.disconnect()
        logging.shutdown()

    def sendMessages(self, messages):
        """Send a data object to the remote host."""
        self._outMessages = self._outMessages + messages

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        messages = self._inMessages
        self._inMessages = []
        return messages

    def getState(self):
        """Get the connection state."""
        return self._state

    def status(self):
        """Get the status."""
        return self.getState()

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


if __name__ == '__main__':
    pass
