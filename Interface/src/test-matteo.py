from connections.beagleboneGreenWirelessConnection import BeagleboneGreenWirelessConnection
import json
import time

c = BeagleboneGreenWirelessConnection()
c.connect()
print('Status: {}'.format(c.getState()))




while True:
#     100% is kinda buggy, use values 0 <= x < 100
    for i in range(3,10):
        c.sendMessages([json.dumps({"dim": i, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
        
    c.sendMessages([json.dumps({"dim": 0, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
    
    
    c.sendMessages([json.dumps({"dim": 1, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
    print('on')
    time.sleep(1)
    c.sendMessages([json.dumps({"dim": 1, "value": 0.0, "type": "Set", "name": "PCA9685@I2C[1]"})])
    print('off')
    time.sleep(1)


def motor_control(dim, duty):
    c.sendMessages([json.dumps({"dim": dim, "value": duty, "type": "Set", "name": "PCA9685@I2C[1]"})])