import socket
import pandas as pd

UDP_IP = "127.0.0.1"
UDP_PORT = 12347
MESSAGE = "Hello, World!"

print ("UDP target IP:", UDP_IP)
print ("UDP target port:", UDP_PORT)
print ("message:", MESSAGE)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))

#log_file = pd.read_csv("Recordings/logfile_12347.log")

