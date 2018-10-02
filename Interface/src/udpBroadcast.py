# -*- coding: utf-8 -*-

## Use wireshark to check for packages in the loopback

import socket

class UDPBroadcast():
    """Class to send serialized messages via udp protocol."""

    # Socket
    _socket = None

    # Ip
    _ip = None

    # Port
    _port = None


    def __init__(self, ip='127.0.0.1', port=12346):
        """Initialize broadcast with port and ip."""
        self._ip = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

    def __del__(self):
        """Class destructor. This is needed in order to close the socket."""
        self._socket.close()

    def __enter__(self):
        """Needed for usage like: 'with UPDBroadcast() as b:'."""
        return self

    def __exit__(self, type, value, traceback):
        """Needed for usage like: 'with UPDBroadcast() as b:'."""
        self._socket.close()

    def send(self, string):
        """Send serialized message."""
        self._socket.sendto(bytes(string, "utf-8"), (self._ip, self._port))




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

    broadcast = UDPBroadcast(UDP_IP, UDP_PORT)
    broadcast.send(TEST_MESSAGE)
