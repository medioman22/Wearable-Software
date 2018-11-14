# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Wearable Software API module. The API provided by this class is asynchronous;
i.e. there is a background thread doing all the work and calls are non-blocking.
"""

import socket as sock                                           # Standard socket API. Communication is over TCP/IP
import threading                                                # Threading class for the background thread
import json                                                     # Serializing class. All objects sent are serialized
from collections import deque                                   # Queues will be used for recieving and sending
import logging                                                  # This class logs all info - so logging is imported
import time                                                     # For delays in the background thread
import os                                                       # For console printing

class APIConnection():
    """API connection."""

    # connection status
    _status = 'Disconnected'

    # connection ip
    _ip = None

    # connection port
    _port = None

    # Timeout in seconds. Affects the sending 'Sampling Period'
    _timeout = 0.1

    # Send queue
    _sendQueue = deque()

    # Recv queue
    _recvQueue = deque()

    # Inner communications thread object
    _commsThreadRun = True

    # The Connection Socket
    _s = None

    # The state of the socket (Initialized, Listening, Connected, Disconnected)
    _state = 'Initialized'

    # The IP of the remote location
    _ip = '192.168.7.2'

    # The Application Port
    _port = 12345

    def __init__(self):
        """
        Class constructor.

        Creates (and binds) the socket and sets all communication options.
        """

        self._commsThreadRun = True                             # Initialize the thread enable boolean
        self._sendQueue = deque()                               # Initialize the send queue
        self._recvQueue = deque()                               # Initialize the recieve queue

        # Set ip and port
        self._port = 12345
        self._ip = '192.168.7.2'

        self._state = 'Initialized'

        # Start never ending thread
        communicationThread = threading.Thread(target=self._innerThread, name="CommunicationThread")
        communicationThread.daemon = True                       # Set thread as daemonic
        communicationThread.start()

    def __del__(self):
        """Class destructor. This is needed in order to stop the background thread."""
        self.stopAndFreeResources()

    def __enter__(self):
        """Needed for usage like: 'with APIConnection() as c:'."""
        return self

    def __exit__(self, type, value, traceback):
        """Needed for usage like: 'with APIConnection() as c:'."""
        self.stopAndFreeResources()
        pass

    def _innerThread(self):
        """Inner thread function, does all socket sending and recieving."""
        remainder = ""                                          # Remainder mechanism for TCP incomplete transmissions
        while True:                                             # While loop dedicated to recieving and sending data
            if (self._s == None):                               # Check if a socket is created
                time.sleep(0.5);                                # Wait a bit
                continue;                                       # Retry on next loop
            try:                                                # Socket timeout will throw an exception
                data = self._s.recv(1024)
                if not data: break                              # This means remote location closed socket
                m_list = (remainder + data.decode("utf-8")).split("}")  # Add the recieved data to the previous remainder
                remainder = ""
                while len(m_list) > 0:                          # After it's split, go through all sub-messages to compose a complete message
                                                                # If we have a message stub and it's imbalanced (more '{' than '}')
                    if remainder and remainder.count("{") > remainder.count("}"):
                        remainder += m_list.pop(0)              # Add the next sub-message
                        if len(m_list) > 0:
                            remainder += "}"                    # Add terminator only if the split indicates we recieved it
                    elif remainder:                             # If we have a message and it's balanced -> we have a complete message
                        self._recvQueue.append(json.loads(remainder))
                        remainder = ""                          # After the recieve reset the remainder
                                                                # If we have no message and the list is almost empty - only "" remains
                    elif len(m_list) == 1 and m_list[0] == "":
                         m_list.pop(0)                          # Empty it
                    else:                                       # If we have no message and the list is not empty -> start a new sub-message
                        remainder += m_list.pop(0)
                        if len(m_list) > 0:
                            remainder += "}"                    # Add terminator only if the split indicates we recieved it
            except sock.timeout:                                # We expect timeouts, as we have non-blocking calls
                pass
            except sock.error as exc:                           # Socket error occured. Log it and mark the disconnect
                print("Error Occured: " + str(exc))
                self._state = 'Disconnected'
                break
            except Exception:                                   # Log generic errors
                pass
            while len(self._sendQueue) > 0:                     # Pop all elements from the sending queue and send them all
                send_message = self._sendQueue.popleft()
                self._s.sendall(str.encode(send_message))
            if not self._commsThreadRun:                        # Terminate the background thread
                return



    def connect(self):
        """Start the background communication thread."""
        self._state = 'Connecting'
        try:                                                # Socket timeout will throw an exception
            self._s = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # Create a TCP socket and set it's timeout
            self._s.settimeout(0.1)                         # Timeout is for blocking calls
            self._s.connect((self._ip, self._port))         # Specify ip/port of the socket
            self._state = 'Connected'                       # Report new state
        except sock.timeout:                                # Since we've set the timeout to 100ms, it's Ok to timeout
            self._state = 'Disconnected'
            raise ConnectionRefusedError('Could not established TCP/IP connection')


    def disconnect(self):
        """Close the connection and stop the communication thread."""
        if (self._s != None):                               # Close socket if open
            self._s.close()
        self._s = None
        time.sleep(0.5)
        self._state = 'Disconnected'


    def stopAndFreeResources(self):
        """Stop the background thread and shuts down the socket and log."""
        self.disconnect()
        self._commsThreadRun = False
        logging.shutdown()

    def sendMessages(self, messages):
        """Send a data object to the remote host."""
        for message in messages:
            self._sendQueue.append(message)

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        messages = []                                           # return object initialized as an empty list
        while len(self._recvQueue) > 0:                         # Pop all messages from the recieve queue and add them to the return list
            message = self._recvQueue.popleft()
            messages.append(message)
        return list(map(lambda x: json.dumps(x), messages))     # Messages returned need to be stringified JSON objects

    def getState(self):
        """Get the connection state."""
        return self._state

    def status(self):
        """Get the status."""
        return self.getState()

    def type(self):
        """Get the type."""
        return self._type

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


# Example usage when module is called as script
if __name__ == '__main__':

    # Create a connection
    c = APIConnection()

    # Connect to the socket
    c.connect()

    # Variables
    devices = {}
    lastEvents = []
    updateCycleDuration = 0
    scanCycleDuration = 0

    # Request device list
    c.sendMessages([json.dumps({'type': 'DeviceList'})])

    # Infinite loop
    while True:
        stringToPrint = ""                                      # String to print
        stringToPrint += "***************\n"
        stringToPrint += "* API Example *\n"                    # Display title
        stringToPrint += "***************\n"
        stringToPrint += "\n"
        # stringToPrint += "Update cycle:  "                          # Print update cycle time
        # stringToPrint += colored("{:.2f} ms / {:.2f} ms\n".format(updateDuration * 1000, UPDATE_PERIODE * 1000), 'grey') # Print update cycle time
        # if scanForDevices:
        #     stringToPrint += "Scan   cycle:  "                      # Print scan cycle time
        #     stringToPrint += colored("{:.2f} ms / {:.2f} ms\n".format(scanDuration * 1000, SCAN_PERIODE * 1000), 'grey') # Print scan cycle time
        # else:
        #     stringToPrint += "Scan   cycle: -\n"                    # Print scan disabled


        # Get all messages
        messagesIn = c.getMessages()

        # Loop all incoming messages
        for messageString in messagesIn:
            # Unserialize the message
            message = json.loads(messageString)

            # Check for type
            if message['type'] == 'Register':
                devices[message['name']] = { 'values': [], 'timestamp': time.time() } # Register the device
                lastEvents.append("Register: {}\n".format(message['name'])) # Save the event
            elif message['type'] == 'Deregister':
                devices[message['name']] = None                 # Deregister the device
                lastEvents.append("Deregister: {}\n".format(message['name'])) # Save the event
            elif message['type'] == 'CycleDuration':
                updateCycleDuration = message['values']['update'] # Get update cycle duration
                scanCycleDuration = message['values']['scan']   # Get scan cycle duration
            elif message['type'] == 'D':
                for el in message['data']:                      # Loop data
                    if (el['name'] in devices and len(el['values']) > 0): # Check if device exists and there is new data
                        device = devices[el['name']]            # Get device
                        device['timestamp'] = el['values'][-1][0] # Get timestamp
                        device['values'] = el['values'][-1][1]  # Get values


        # Show cycle durations
        stringToPrint += "Update: {:.2f} ms | Scan: {:.2f} ms\n\n".format(updateCycleDuration * 1000, scanCycleDuration * 1000)


        # Log the live data
        stringToPrint += "\nVALUES\n"
        stringToPrint += "******\n"
        for name, device in devices.items():
            stringToPrint += "{}: {}\n".format(name, str(device['values']))
        stringToPrint += "******\n"

        # Remove old events
        while (12 < len(lastEvents)):
            lastEvents.pop(0)

        # Print last events
        stringToPrint += "\nEVENTS\n"
        stringToPrint += "******\n"
        for lastEvent in lastEvents:
            stringToPrint += lastEvent
        stringToPrint += "******\n"

        # PRINT
        stringToPrint += "\n\nManually break to exit!\n"            # Print exit condition
        stringToPrint += ">> Ctrl-C\n"                              # Print exit shortcut
        os.system('clear')                                          # Clear console output
        print(stringToPrint)

        # Wait a bit
        time.sleep(0.1)
