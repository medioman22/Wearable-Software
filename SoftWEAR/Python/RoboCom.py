# -*- coding: utf-8 -*-
"""
SoftWEAR Communications module. The API provided by this class is asynchronous;
i.e. there is a background thread doing all the work and calls are non-blocking.
"""

import socket as sock          # Standard socket API. Communication is over TCP/IP
import threading               # Threading class for the background thread
import json                    # Serializing class. All objects sent are serialized
from collections import deque  # Queues will be used for recieving and sending
import logging                 # This class logs all info - so logging is imported
import time                    # For delats in the background thread


class RoboCom:
    def __init__(self, platform='pc'):
        """ Class constructor. Creates (and binds) the socket, starts the logger
            and sets all communication options. platform is either 'bb' or 'pc' """
        self._comms_thread_run = True       # Initialize the thread enable boolean
        self._send_queue = deque()          # Initialize the send queue
        self._recv_queue = deque()          # Initialize the recieve queue
        
        # Configure the logger
        self._logger = logging.getLogger('RoboCom')
        self._logger.setLevel(logging.INFO) # Only INFO level or above will be saved
        fh = logging.FileHandler('RoboCom.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)           # Only INFO level or above will be saved
        self._logger.addHandler(fh)
                
        # Create a TCP socket and set it's timeout
        self._s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)  
        self._timeout = 0.1                 # Init timeout to 100ms
        self._s.settimeout(self._timeout)   # Timeout is for blocking calls
        self.port = 12345                   # Set the port
        
        if platform is 'pc':                # 'pc' means we will be the client
            self.target_ip = '192.168.7.2'  # The IP of the BeagleBone            
            self._platform = 'pc'
            self._state = 'Initialized'
            
        elif platform is 'bb':              # 'bb' means we will be the server
            self.target_ip = '192.168.7.1'  # The IP of the PC
            self._platform = 'bb'
            
            # Server side -> bind onto port; set port as reusable
            self._s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
            self._state = 'Initialized'
            self._s.bind(('', self.port))   # Bind the socket - since this is server
            self._state = 'Bound'
            self._logger.info('Socket bound onto port ' + str(self.port))
            
        else:                               # platform HAS to be either 'bb' or 'pc'
            self._logger.error('Wrong platform parameter: ' + str(platform))
            raise ValueError('Platform must either be "pc" or "bb"')
           
    def __del__(self):
        """ Class destructor. This is needed in order to stop the background thread """
        self.stop_and_free_resources()
        
    def __enter__(self):
        """ Needed for usage like: 'with RoboCom() as c:' """
        return self
    
    def __exit__(self, type, value, traceback):
        """ Needed for usage like: 'with RoboCom() as c:' """
        self.stop_and_free_resources()
        pass
            
    def _inner_thread(self):
        """ Inner thread function. Does all socket sendind and recieving. """
        if self._platform is 'pc':      # We are the client -> we have to connect
            remainder = ""              # Remainder mechanism for TCP incomplete transmissions
            while True:                 # While loop dedicated for connecting
                try:                    # Socket timeout will throw an exception
                    self._s.connect((self.target_ip, self.port)) 
                    # When above functions exits without exception, we are connnected!
                    self._logger.info("Connected to: " + str(self.target_ip))
                    self._state = 'Connected'
                    break
                except sock.timeout:    # Since we've set the timeout to 100ms, it's Ok to timeout
                    pass            
            while True:                 # While loop dedicated to recieving and sending data
                try:                    # Socket timeout will throw an exception
                    data = self._s.recv(1024)                      
                    if not data: break  # This means remote location closed socket   
                    self._logger.debug("Recieved RAW data: " + str(data))
                    m_list = (remainder + data.decode("utf-8")).split("}")  # Add the recieved data to the previous remainder
                    remainder = ""
                    while len(m_list) > 0:      # After it's split, go through all sub-messages to compose a complete message
                        # If we have a message stub and it's imbalanced (more '{' than '}')
                        if remainder and remainder.count("{") > remainder.count("}"):
                            remainder += m_list.pop(0)   # Add the next sub-message 
                            if len(m_list) > 0:
                                remainder += "}"         # Add terminator only if the split indicates we recieved it
                        elif remainder: # If we have a message and it's balanced -> we have a complete message
                            self._recv_queue.append(json.loads(remainder))
                            self._logger.info("Recieved data: " + str(remainder))
                            remainder = ""      # After the recieve reset the remainder
                        # If we have no message and the list is almost empty - only "" remains
                        elif len(m_list) == 1 and m_list[0] == "":
                             m_list.pop(0)      # Empty it
                        else:           # If we have no message and the list is not empty -> start a new sub-message
                            remainder += m_list.pop(0)
                            if len(m_list) > 0:
                                remainder += "}"# Add terminator only if the split indicates we recieved it
                except sock.timeout:    # We expect timeouts, as we have non-blocking calls
                    pass
                except sock.error as exc:
                    # Socket error occured. Log it and mark the disconnect
                    self._logger.error('Socket Error occurred: ' + str(exc))
                    print("Error Occured: " + str(exc))
                    self._state = 'Disconnected'
                    break
                except Exception as exc:
                    # Log generic errors
                    self._logger.error('General Error occurred: ' + str(exc) + ' rem: ' + str(remainder))
                while len(self._send_queue) > 0: 
                    # Pop all elements from the sending queue and send them all
                    send_message = self._send_queue.popleft()
                    self._s.sendall(str.encode(send_message))
                    self._logger.info("Sent message: " + str(send_message))
                if not self._comms_thread_run:
                    return              # This line terminates the background thread
        
        elif self._platform is 'bb':    # We are the server -> we have to listen
            while True:                 # Infinite loop of servicing requests
                self._logger.info('Listening for incoming connections')     
                self._s.listen(1)       # Listen for connections
                self._state = 'Listening'
                remainder = ""          # Remainder mechanism for TCP incomplete transmissions

                while True:             # While loop for the accept call
                    try:                # Since we are non-blocking, timeouts can/will occur
                        conn, addr = self._s.accept()   # Accept any incoming connection  
                        conn.settimeout(self._timeout)  # Set new socket timeout
                        self._logger.info("Connected to: " + str(addr))
                        self._state = 'Connected'
                        break
                    except sock.timeout:# We expect timeouts, as we have non-blocking calls 
                        if not self._comms_thread_run:
                            return      # This line terminates the background thread
                        
                while True:             # While loop dedicated to recieving and sending data 
                    try:                # We will be using the connection socket
                        data = conn.recv(1024)           
                        if not data: break          # This means remote location closed socket  
                        self._logger.debug("Recieved RAW data: " + str(data))
                        m_list = (remainder + data.decode("utf-8")).split("}")  # Add the recieved data to the previous remainder
                        remainder = ""
                        while len(m_list) > 0:      # After it's split, go through all sub-messages to compose a complete message
                            # If we have a message stub and it's imbalanced (more '{' than '}')
                            if remainder and remainder.count("{") > remainder.count("}"):
                                remainder += m_list.pop(0)     # Add the next sub-message 
                                if len(m_list) > 0:
                                        remainder += "}"       # Add terminator only if the split indicates we recieved it
                            elif remainder:         # If we have a message and it's balanced -> we have a complete message
                                self._recv_queue.append(json.loads(remainder))
                                self._logger.info("Recieved data: " + str(remainder))
                                remainder = ""      # After the recieve reset the remainder
                            # If we have no message and the list is almost empty - only "" remains
                            elif len(m_list) == 1 and m_list[0] == "":
                                 m_list.pop(0)      # Empty it
                            else:   # If we have no message and the list is not empty -> start a new sub-message
                                remainder += m_list.pop(0)
                                if len(m_list) > 0:
                                    remainder += "}"# Add terminator only if the split indicates we recieved it
                    except sock.timeout:            # We expect timeouts, as we have non-blocking calls
                        pass
                    except sock.error as exc:
                        # Socket error occured. Log it and mark the disconnect
                        self._logger.error('Socket Error occurred: ' + str(exc))
                        print("Error Occured: " + str(exc))
                        self._state = 'Disconnected'
                        break
                    except Exception as exc:
                        # Log generic errors
                        self._logger.error('General Error occurred: ' + str(exc))
                    while len(self._send_queue) > 0:
                        # Pop all elements from the sending queue and send them all
                        send_message = self._send_queue.popleft()
                        conn.sendall(str.encode(send_message))
                        self._logger.info("Sent message: " + str(send_message))
                    if not self._comms_thread_run:
                        return          # This line terminates the background thread                
                conn.close()            # Close connection if we ever reach here
        
            
    def start_communications(self):
        """ Function starts the background communications thread """
        threading.Thread(target=self._inner_thread).start()
        
    def stop_and_free_resources(self):
        """ Stops the background thread and shuts down the socket and log """
        self._comms_thread_run = False
        time.sleep(0.5)
        self._s.close()
        logging.shutdown()
        
    def send_data(self, data_object):
        """ Sends a data object to the remote host. """
        self._send_queue.append(json.dumps(data_object))
        self._logger.debug('Message added to send queue: ' + str(data_object))
        
    def rcv_data(self):
        """ Gets a list of all the messages that have been recieved since the
            last call of this function. """
        ret = []    # return object initialized as an empty list
        while len(self._recv_queue) > 0:
            # Pop all messages from the recieve queue and add them to the return list
            ret.append(self._recv_queue.popleft())
        self._logger.debug('Messages removed from rcv queue: ' + str(ret))
        return ret
    
    def get_rcv_messages_nb(self):
        """ Gets the number of message currently in the recieve queue """
        return len(self._recv_queue)
    
    def get_state(self):
        """ Gets the connection state """
        return self._state
    
    """ The Platform on which the COM is run. 'pc' or 'bb' """
    _platform = 'pc'
    
    """ Timeout in seconds. Affects the sending 'Sampling Period' """
    _timeout = 0.1
    
    """ Send queue """
    _send_queue = deque()
    
    """ Recv queue """
    _recv_queue = deque()
    
    """ Logger object used by the class to create the log file """
    _logger = logging.getLogger('RoboCom')
    
    """ Inner communications thread object """
    _comms_thread_run = True
    
    """ The Connection Socket """
    _s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    
    """ The state of the socket """
    _state = 'Initialized'
    
    """ The IP of the remote location (target). """
    target_ip = '192.168.7.2'
    
    """ The Application Port. """
    port = 12345 
    
