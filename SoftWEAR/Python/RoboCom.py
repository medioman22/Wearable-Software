# -*- coding: utf-8 -*-
"""

"""

import socket as sock
import threading as threading
import json as json
from collections import deque
import logging
import time


class RoboCom:
    def __init__(self, platform='pc'):
        self._comms_thread_run = True
        self._send_queue = deque()
        self._recv_queue = deque()
        # Configure the logger
        self._logger = logging.getLogger('RoboCom')
        self._logger.setLevel(logging.INFO)
        fh = logging.FileHandler('RoboCom.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        self._logger.addHandler(fh)
                
        # Create a TCP socket and set it's timeout
        self._s = sock.socket(sock.AF_INET, sock.SOCK_STREAM)  
        #self._s.setsockopt(sock.IPPROTO_TCP, sock.TCP_NODELAY, 1)
        self._timeout = 0.1
        self._s.settimeout(self._timeout)
        self.port = 12345
        
        if platform is 'pc':
            self.target_ip = '192.168.7.2'  # The IP of the BeagleBone            
            self._platform = 'pc'
            self._state = 'Initialized'
            
        elif platform is 'bb':
            self.target_ip = '192.168.7.1'  # The IP of the PC
            self._platform = 'bb'
            
            # Server side -> bind onto port; set port as reusable
            self._s.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
            self._state = 'Initialized'
            self._s.bind(('', self.port))    
            self._state = 'Bound'
            self._logger.info('Socket bound onto port ' + str(self.port))
            
        else:
            self._logger.error('Wrong platform parameter: ' + str(platform))
            raise ValueError('platform must either be "pc" or "bb"')
           
    def __del__(self):
        self.stop_and_free_resources()
        
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.stop_and_free_resources()
        pass
            
    def _inner_thread(self):
        if self._platform is 'pc':
            remainder = ""
            while True:
                try:
                    self._s.connect((self.target_ip, self.port)) 
                    self._logger.info("Connected to: " + str(self.target_ip))
                    self._state = 'Connected'
                    break
                except sock.timeout:
                    pass            
            while True:
                try:
                    data = self._s.recv(1024)  
                    if not data: break    
                    self._logger.debug("Recieved RAW data: " + str(data))
                    m_list = (remainder + data.decode("utf-8")).split("}")  # Add the recieved data to the previous remainder
                    remainder = ""
                    while len(m_list) > 0:      # After it's split, go through all sub-messages to compose a complete message
                        # If we have a message stub and it's imbalanced (more '{' than '}')
                        if remainder and remainder.count("{") > remainder.count("}"):
                            remainder += m_list.pop(0)   # Add the next sub-message 
                            if len(m_list) > 0:
                                remainder += "}"         # Add terminator only if the split indicates we recieved it
                        elif remainder:     # If we have a message and it's balanced -> we have a complete message
                            self._recv_queue.append(json.loads(remainder))
                            self._logger.info("Recieved data: " + str(remainder))
                            remainder = ""  # After the recieve reset the remainder
                        # If we have no message and the list is almost empty - only "" remains
                        elif len(m_list) == 1 and m_list[0] == "":
                             m_list.pop(0)  # Empty it
                        else:   # If we have no message and the list is not empty -> start a new sub-message
                            remainder += m_list.pop(0)
                            if len(m_list) > 0:
                                remainder += "}"         # Add terminator only if the split indicates we recieved it
                except sock.timeout:
                    pass
                except sock.error as exc:
                    self._logger.error('Socket Error occurred: ' + str(exc))
                    print("Error Occured: " + str(exc))
                    self._state = 'Disconnected'
                    break
                except Exception as exc:
                    self._logger.error('General Error occurred: ' + str(exc) + ' rem: ' + str(remainder))
                while len(self._send_queue) > 0:                    
                    send_message = self._send_queue.popleft()
                    self._s.sendall(str.encode(send_message))
                    self._logger.info("Sent message: " + str(send_message))
                if not self._comms_thread_run:
                    return
        
        elif self._platform is 'bb':
            while True:                
                self._logger.info('Listening for incoming connections')     
                self._s.listen(1)                # Listen for connections
                self._state = 'Listening'
                remainder = ""

                while True:
                    try:
                        conn, addr = self._s.accept()    # Accept any incoming connection  
                        conn.settimeout(self._timeout)
                        #conn.setsockopt(sock.IPPROTO_TCP, sock.TCP_NODELAY, 1)
                        self._logger.info("Connected to: " + str(addr))
                        self._state = 'Connected'
                        break
                    except sock.timeout:
                        if not self._comms_thread_run:
                            return
                while True:
                    try:
                        data = conn.recv(1024)           
                        if not data: break    
                        self._logger.debug("Recieved RAW data: " + str(data))
                        m_list = (remainder + data.decode("utf-8")).split("}")  # Add the recieved data to the previous remainder
                        remainder = ""
                        while len(m_list) > 0:      # After it's split, go through all sub-messages to compose a complete message
                            # If we have a message stub and it's imbalanced (more '{' than '}')
                            if remainder and remainder.count("{") > remainder.count("}"):
                                remainder += m_list.pop(0)     # Add the next sub-message 
                                if len(m_list) > 0:
                                        remainder += "}"       # Add terminator only if the split indicates we recieved it
                            elif remainder:     # If we have a message and it's balanced -> we have a complete message
                                self._recv_queue.append(json.loads(remainder))
                                self._logger.info("Recieved data: " + str(remainder))
                                remainder = ""  # After the recieve reset the remainder
                            # If we have no message and the list is almost empty - only "" remains
                            elif len(m_list) == 1 and m_list[0] == "":
                                 m_list.pop(0)  # Empty it
                            else:   # If we have no message and the list is not empty -> start a new sub-message
                                remainder += m_list.pop(0)
                                if len(m_list) > 0:
                                    remainder += "}"         # Add terminator only if the split indicates we recieved it
                    except sock.timeout:
                        pass
                    except sock.error as exc:
                        self._logger.error('Socket Error occurred: ' + str(exc))
                        print("Error Occured: " + str(exc))
                        self._state = 'Disconnected'
                        break
                    except Exception as exc:
                        self._logger.error('General Error occurred: ' + str(exc))
                    while len(self._send_queue) > 0:
                        send_message = self._send_queue.popleft()
                        conn.sendall(str.encode(send_message))
                        self._logger.info("Sent message: " + str(send_message))
                    if not self._comms_thread_run:
                        return                        
                conn.close()
        
            
    def start_communications(self):
        threading.Thread(target=self._inner_thread).start()
        
    def stop_and_free_resources(self):
        self._comms_thread_run = False
        time.sleep(0.5)
        self._s.close()
        logging.shutdown()
        
    def send_data(self, data_object):
        self._send_queue.append(json.dumps(data_object))
        self._logger.debug('Message added to send queue: ' + str(data_object))
        
    def rcv_data(self):
        ret = []
        while len(self._recv_queue) > 0:
            ret.append(self._recv_queue.popleft())
        self._logger.debug('Messages removed from rcv queue: ' + str(ret))
        return ret
    
    def get_rcv_messages_nb(self):
        return len(self._recv_queue)
    
    def get_state(self):
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
    
