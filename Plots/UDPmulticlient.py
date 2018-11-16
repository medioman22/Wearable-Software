import socket
import logging
import random
import random
import sys
from threading import Thread
import time
import atexit
from pathlib import Path

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


class UDPClient(Thread):

    """Thread that will open an UDP socket on creation with the specified UDP ip and Port"""
    """ Messages recieved on the UDP socket will be stored in a LOG file with the port written"""

    def __init__(self, UDP_IP, UDP_Port):
        Thread.__init__(self)
        self.UDP_Port = UDP_Port
        self.UDP_IP = UDP_IP
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
            print ("Socket created on port " + str(self.UDP_Port))
        except socket.error as msg:
            print ("Failed to creat the socket "+str(self.UDP_Port)+" . Error Code: " + str(msg[0])+" Message "+msg[1])

        try:
            self.sock.bind((self.UDP_IP, self.UDP_Port))
        except socket.error as msg:
            print ("Failed to bind the socket "+str(self.UDP_Port)+" . Error Code: "+str(msg[0])+" Message " + msg[1])

    def run(self):
        """Read and decode data from the UDP socket and stors them in a LOG file"""

        self.logger = setup_logger("logfile_"+str(self.UDP_Port),("Recordings/logfile_"+str(self.UDP_Port)+".log"))
        #self.logger = logging.basicConfig(level=logging.DEBUG, filename=("logfile_"+str(self.UDP_Port)), filemode="a+",
         #                   format="%(asctime)-15s %(levelname)-8s %(message)s")
        while True:
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            self.logger.info(data.decode())
            print("For port: "+ str(self.UDP_Port) +"  Data: "+ data.decode())

    def stop(self):
        self.sock.close()


def exit_handler():
    print ('My application is ending!')
    thread_1.stop()
    thread_2.stop()
    thread_3.stop()


def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT1 = 12347
    UDP_PORT2 = 12343
    UDP_PORT3 = 12342



    # Thread creation for a number of UDP client
    thread_1 = UDPClient(UDP_IP, UDP_PORT1)
    thread_2 = UDPClient(UDP_IP, UDP_PORT2)
    thread_3 = UDPClient(UDP_IP, UDP_PORT3)

    # Thread starting 
    thread_1.start()
    thread_2.start()
    thread_3.start()

    # Wait forever that the thread one finishes
    thread_1.join()

    atexit.register(exit_handler)

if __name__ == "__main__":
    main()



