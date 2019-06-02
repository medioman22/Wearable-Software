import os,sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import select
import socket
import time



def read_last(my_socket):

    data = 't'

    data_ready = False
    data_ready = select.select([my_socket],[],[],0)[0]

    while data_ready:
        data, addr = my_socket.recvfrom(1024) # buffer size is 1024 bytes

        data_ready = False
        data_ready = select.select([my_socket],[],[],0)[0]

    return data


UDP_IP = "127.0.0.1"
UDP_PORT = 12346

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))



while True:

    t = time.time()
    data = read_last(sock)
    print('it took ', time.time() - t, ' ms')

    print(data)

    time.sleep(1)
