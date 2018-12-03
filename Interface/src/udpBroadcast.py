# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018

## Use wireshark to check for packages in the loopback

import socket                                                   # Socket package for UDP
import logging                                                  # Logging package
import time                                                     # Timing

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging

class UDPBroadcast():
    """Class to send serialized messages via udp protocol."""

    # Socket
    _socket = None
    # Ip
    _ip = None
    # Port
    _port = None
    # Logger module
    _logger = None


    def __init__(self, ip='127.0.0.1', port=12346):
        """Initialize broadcast with port and ip."""
        # Configure the logger
        self._logger = logging.getLogger('UDPBroadcast')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        # fh = logging.FileHandler('../Logs/UDPBroadcast.log', 'w')
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        # fh.setFormatter(formatter)
        # fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        # self._logger.addHandler(fh)

        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._logger.info("Configure UDP socket with {}/{}".format(ip,port))

    def __del__(self):
        """Class destructor. This is needed in order to close the socket."""
        self._socket.close()                                    # Close socket
        self._logger.info("Close UDP socket")

    def __enter__(self):
        """Needed for usage like: 'with UPDBroadcast() as b:'."""
        return self

    def __exit__(self, type, value, traceback):
        """Needed for usage like: 'with UPDBroadcast() as b:'."""
        self._socket.close()                                    # Close socket
        self._logger.info("Close UDP socket")

    def send(self, string):
        """Send serialized message."""
        self._socket.sendto(bytes(string, "utf-8"), ('<broadcast>', self._port)) # Send message via socket




# Test udp broadcast
if __name__ == '__main__':

    # Default IP/Port settings to test
    UDP_IP = "127.0.0.1"
    UDP_PORT = 12346
    TEST_MESSAGE = "I am a loopback/broadcast UDP package."

    # Send test message
    print("UDP target IP:", UDP_IP)
    print("UDP target port:", UDP_PORT)
    print("Message:", TEST_MESSAGE)

    while True:
        broadcast = UDPBroadcast(UDP_IP, UDP_PORT)
        broadcast.send(TEST_MESSAGE)

        time.sleep(0.2)
