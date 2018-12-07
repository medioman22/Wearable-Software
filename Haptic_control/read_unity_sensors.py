# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 01:08:42 2018

@author: macchini
"""


import numpy as np
import socket
import struct

UDP_IP = "127.0.0.1"
UDP_PORT = 35000

many_data = 1000000     # this is abuot 55 minutes of acquisition with 3 markers
                        # (increase for longer acquisition time)

correction = [None] * many_data

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

count = 0

#while True:
data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
print("acquired marker data, counter = ", count)

strs = 'ffffffffffffff'

data_ump = struct.unpack(strs, data)

corr = data_ump[-2:]

correction[count] = np.array(corr)

print(corr)

count = count + 1
    
# press ctrl + c when acquisition is finished
# then run te_csv.py
