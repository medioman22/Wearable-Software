# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
SoftWEAR Communications module. The API provided by this class is asynchronous;
i.e. there is a background thread doing all the work and calls are non-blocking.
"""

import socket as sock                                           # Standard socket API. Communication is over TCP/IP
import threading                                                # Threading class for the background thread
import json                                                     # Serializing class. All objects sent are serialized
from collections import deque                                   # Queues will be used for recieving and sending
import logging                                                  # This class logs all info - so logging is imported
import time                                                     # For delays in the background thread
from connections.connection import Connection


LOG_LEVEL_PRINT = logging.WARN
LOG_LEVEL_SAVE = logging.DEBUG


class BeagleboneGreenWirelessConnection(Connection):
    """BeagleboneGreenWirelessConnection connection."""

    # Timeout in seconds. Affects the sending 'Sampling Period'
    _timeout = 0.1

    # Send queue
    _sendQueue = deque()

    # Recv queue
    _recvQueue = deque()

    # Logger object used by the class to create the log file
    _logger = logging.getLogger('BeagleboneGreenWireless')

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

    # The logger
    _logger = None

    def __init__(self):
        """
        Class constructor.

        Creates (and binds) the socket, starts the logger and sets all communication options.
        """
        super().__init__('BeagleboneGreenWirelessConnection')

        self._commsThreadRun = True                             # Initialize the thread enable boolean
        self._sendQueue = deque()                               # Initialize the send queue
        self._recvQueue = deque()                               # Initialize the recieve queue

        # Configure the logger
        self._logger = logging.getLogger('BeagleboneGreenWirelessConnection')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        # fh = logging.FileHandler('../Logs/BeagleboneGreenWirelessConnection.log', 'w')
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        # fh.setFormatter(formatter)
        # fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        # self._logger.addHandler(fh)

        # Set ip and port
        self._port = 12345
        self._ip = '192.168.7.2'

        self._state = 'Initialized'

        # Start never ending thread
        self.communicationThread = threading.Thread(target=self._innerThread, name="CommunicationThread")
        self.communicationThread.daemon = True                       # Set thread as daemonic
        self.communicationThread.start()

    def __del__(self):
        """Class destructor. This is needed in order to stop the background thread."""
        self.stopAndFreeResources()

    def __enter__(self):
        """Needed for usage like: 'with BeagleboneGreenWirelessConnection() as c:'."""
        return self

    def __exit__(self, type, value, traceback):
        """Needed for usage like: 'with BeagleboneGreenWirelessConnection() as c:'."""
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
                if not data: continue #break                    # This means remote location closed socket
                self._logger.debug("Recieved RAW data: " + str(data))
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
                        self._logger.info("Recieved data: " + str(remainder))
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
                self._logger.error('Socket Error occurred: ' + str(exc))
                print("Error Occured: " + str(exc))
                self._state = 'Disconnected'
                continue #break
            except Exception as exc:                            # Log generic errors
                self._logger.error('General Error occurred: ' + str(exc) + ' rem: ' + str(remainder))
            while len(self._sendQueue) > 0:                     # Pop all elements from the sending queue and send them all
                send_message = self._sendQueue.popleft()
                self._s.sendall(str.encode(send_message))
                self._logger.info("Sent message: " + str(send_message))
            if not self._commsThreadRun:                        # Terminate the background thread
                return



    def connect(self):
        """Start the background communication thread."""
        self._state = 'Connecting'
        try:                                                # Socket timeout will throw an exception
            self._s = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # Create a TCP socket and set it's timeout
            self._s.settimeout(0.1)                         # Timeout is for blocking calls
            self._s.connect((self._ip, self._port))         # Specify ip/port of the socket
            self._logger.info("Connected to: " + str(self._ip))
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
        self._logger.info("Disconneted from: " + str(self._ip))


    def stopAndFreeResources(self):
        """Stop the background thread and shuts down the socket and log."""
        self.disconnect()
        self._commsThreadRun = False
        logging.shutdown()

    def sendMessages(self, messages):
        """Send a data object to the remote host."""
        for message in messages:
            self._sendQueue.append(message)
            self._logger.debug('Message added to send queue: ' + str(message))

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        messages = []                                           # return object initialized as an empty list
        while len(self._recvQueue) > 0:                         # Pop all messages from the recieve queue and add them to the return list
            message = self._recvQueue.popleft()
            self._logger.debug('Message removed from rcv queue: ' + str(message))
            messages.append(message)
        return list(map(lambda x: json.dumps(x), messages))     # Messages returned need to be stringified JSON objects

    def getState(self):
        """Get the connection state."""
        return self._state

    def status(self):
        """Get the status."""
        return self.getState()
