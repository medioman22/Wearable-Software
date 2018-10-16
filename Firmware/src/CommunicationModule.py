# -*- coding: utf-8 -*-
"""
SoftWEAR Communications module.

    The API provided by this class is asynchronous;
    i.e. there is a background thread doing all the work and calls are non-blocking.
    Inspired by the RoboCom.
"""

import os                                                       # Operating system functionality
import socket as sock                                           # Standard socket API. Communication is over TCP/IP
import threading                                                # Threading class for the background thread
import json                                                     # Serializing class. All objects sent are serialized
from collections import deque                                   # Queues will be used for recieving and sending
import logging                                                  # This class logs all info - so logging is imported
import time                                                     # For delays in the background thread


LOG_LEVEL_PRINT = logging.DEBUG
LOG_LEVEL_SAVE = logging.DEBUG

class CommunicationConnection:
    """CommunicationConnection connection."""

    # Timeout in seconds. Affects the sending 'Sampling Period'
    _timeout = 0.1

    # Send queue
    _sendQueue = deque()

    # Recv queue
    _recvQueue = deque()

    # Logger object used by the class to create the log file
    _logger = logging.getLogger('Communication')

    # Inner communications thread object
    _commsThreadRun = True

    # The Connection Socket
    _s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)

    # The state of the socket (Initialized, Listening, Connected, Disconnected)
    _state = 'Initialized'

    # The IP of the remote location
    _ip = '192.168.7.2'

    # The Application Port
    _port = 12345

    def __init__(self, platform='pc'):
        """
        Class constructor.

        Creates (and binds) the socket, starts the logger and sets all communication options.
        """
        self._commsThreadRun = True                             # Initialize the thread enable boolean
        self._sendQueue = deque()                               # Initialize the send queue
        self._recvQueue = deque()                               # Initialize the recieve queue

        # Configure the logger
        self._logger = logging.getLogger('RoboComConnection')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL_PRINT} level or above will be saved
        fh = logging.FileHandler('roboComConnection.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL_SAVE} level or above will be saved
        self._logger.addHandler(fh)

        # Create a TCP socket and set it's timeout
        self._s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self._timeout = 0.1                                     # Init timeout to 100ms
        self._s.settimeout(self._timeout)                       # Timeout is for blocking calls

        # Set ip and port
        self._port = 12345                                      # Set the port
        self._ip = '192.168.7.1'                                # The IP of the Host

        # Server side -> bind onto port; set port as reusable
        self._s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
        self._state = 'Initialized'
        self._s.bind(('', self._port))                          # Bind the socket - since this is server
        self._state = 'Bound'
        self._logger.info('Socket bound onto port ' + str(self._port))

    def __del__(self):
        """Class destructor. This is needed in order to stop the background thread."""
        self.stopAndFreeResources()

    def __enter__(self):
        """Needed for usage like: 'with RoboComConnection() as c:'."""
        return self

    def __exit__(self, type, value, traceback):
        """Needed for usage like: 'with RoboComConnection() as c:'."""
        self.stopAndFreeResources()
        pass

    def _innerThread(self):
        """Inner thread function, does all socket sendind and recieving."""
        while True:                                             # Infinite loop of servicing requests
            self._logger.info('Listening for incoming connections')
            self._s.listen(1)                                   # Listen for connections
            self._state = 'Listening'
            remainder = ""                                      # Remainder mechanism for TCP incomplete transmissions

            while True:                                         # While loop for the accept call
                try:                                            # Since we are non-blocking, timeouts can/will occur
                    conn, addr = self._s.accept()               # Accept any incoming connection
                    conn.settimeout(self._timeout)              # Set new socket timeout
                    self._logger.info("Connected to: " + str(addr))
                    self._state = 'Connected'
                    break
                except sock.timeout:                            # We expect timeouts, as we have non-blocking calls
                    if not self._commsThreadRun:
                        return                                  # This line terminates the background thread

            while True:                                         # While loop dedicated to recieving and sending data
                try:                                            # We will be using the connection socket
                    data = conn.recv(1024)
                    if not data: break                          # This means remote location closed socket
                    self._logger.debug("Recieved RAW data: " + str(data))
                    m_list = (remainder + data.decode("utf-8")).split("}")  # Add the recieved data to the previous remainder
                    remainder = ""
                    while len(m_list) > 0:                      # After it's split, go through all sub-messages to compose a complete message
                                                                # If we have a message stub and it's imbalanced (more '{' than '}')
                        if remainder and remainder.count("{") > remainder.count("}"):
                            remainder += m_list.pop(0)          # Add the next sub-message
                            if len(m_list) > 0:
                                    remainder += "}"            # Add terminator only if the split indicates we recieved it
                        elif remainder:                         # If we have a message and it's balanced -> we have a complete message
                            self._recvQueue.append(json.loads(remainder))
                            self._logger.info("Recieved data: " + str(remainder))
                            remainder = ""                      # After the recieve reset the remainder
                                                                # If we have no message and the list is almost empty - only "" remains
                        elif len(m_list) == 1 and m_list[0] == "":
                             m_list.pop(0)                      # Empty it
                        else:                                   # If we have no message and the list is not empty -> start a new sub-message
                            remainder += m_list.pop(0)
                            if len(m_list) > 0:
                                remainder += "}"                # Add terminator only if the split indicates we recieved it
                except sock.timeout:                            # We expect timeouts, as we have non-blocking calls
                    pass
                except IOError as exc:
                    self._logger.error('IOError Error occurred: ' + str(exc))
                except sock.error as exc:
                                                                # Socket error occured. Log it and mark the disconnect
                    self._logger.error('Socket Error occurred: ' + str(exc))
                    print("Error Occured: " + str(exc))
                    self._state = 'Disconnected'
                    break
                except Exception as exc:
                                                                # Log generic errors
                    self._logger.error('General Error occurred: ' + str(exc))
                while len(self._sendQueue) > 0:
                    try:
                                                                # Pop all elements from the sending queue and send them all
                        send_message = self._sendQueue.popleft()
                        conn.sendall(str.encode(send_message))
                        self._logger.info("Sent message: " + str(send_message))
                    except IOError as exc:
                        self._logger.error('IOError Error occurred: ' + str(exc))
                    except sock.error as exc:
                                                                # Socket error occured. Log it and mark the disconnect
                        self._logger.error('Socket Error occurred: ' + str(exc))
                        print("Error Occured: " + str(exc))
                        self._state = 'Disconnected'
                    except Exception as exc:
                                                                # Log generic errors
                        self._logger.error('General Error occurred: ' + str(exc))
                if not self._commsThreadRun:
                    return                                      # This line terminates the background thread
            conn.close()                                        # Close connection if we ever reach here


    def connect(self):
        """Start the background communication thread."""
        communicationThread = threading.Thread(target=self._innerThread, name="CommunicationThread")
        communicationThread.daemon = True                       # Set thread as daemonic
        communicationThread.start()                             # Start the thread


    def disconnect(self):
        """Close the connection and stop the communication thread."""
        self._status = 'Disconnected'

                                                                # Stop the thread but keep everything else
        self._commsThreadRun = False

    def stopAndFreeResources(self):
        """Stop the background thread and shuts down the socket and log."""
        self._commsThreadRun = False                            # Set communication flag to false
        time.sleep(0.5)
        self._s.close()                                         # Close socket
        logging.shutdown()

    def sendMessages(self, messages):
        """Send a data object to the remote host."""
        for message in messages:
            self._sendQueue.append(message)                     # Add messages to queue to send
        self._logger.debug('Messages added to send queue: ' + str(messages))

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        messages = []                                           # Return object initialized as an empty list
        while len(self._recvQueue) > 0:
            messages.append(self._recvQueue.popleft())          # Pop all messages from the recieve queue and add them to the return list
        self._logger.debug('Messages removed from rcv queue: ' + str(messages))
        return list(map(lambda x: json.dumps(x), messages))

    def countRecvMessages(self):
        """Get the number of message currently in the recieve queue."""
        return len(self._recvQueue)

    def getState(self):
        """Get the connection state."""
        return self._state


# Test the connection
if __name__ == '__main__':

    def test():
        """Infinite loop function. Reads all devices and manages the connection."""
        global connMessage
        global lastMessage

        with CommunicationConnection() as c:                    # Create the communication class. Using 'with' to ensure correct termination.
            c.connect()                                         # Start the communication
            lastMessage = 'Waiting for messages'                # Set last message
            while(True):                                        # Enter the infinite loop
                connMessage = "Conn State: " + c.getState()     # Get the connection state for printing reasons

                if c.getState() is 'Connected':
                    sendMessages = [json.dumps({'type': 'Ping'})]
                    c.sendMessages(sendMessages)

                getMessages = c.getMessages()
                if (len(getMessages) > 0):
                    lastMessage = getMessages.pop();

                os.system('clear')                              # Clear console output
                print("manually break to exit program!\n")      # Print exit condition
                print(connMessage)                              # Print connection status
                print(lastMessage + "\n")                       # Print last comm message

                time.sleep(0.1)                                 # Sleep until next sampling period

            # If we reach this -> something happened. Close communication channel
            c.stopAndFreeResources()

    # Run test
    test()
