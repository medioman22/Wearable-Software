# -*- coding: utf-8 -*-
"""

"""

import os as os
import time as time
import RoboCom as com
import RoboADC as r_adc

emg_list = []
imu_list = []
pwm_list = []
last_message = ""
send_last_message = False
conn_message = ""

adc = r_adc.RoboADC()

def print_func():
    global conn_message, last_message
    os.system('clear')                          # Clear console output
    print("manually break to exit program!\n\n")# Print exit condition
    print(conn_message)
    print(last_message + "\n")                  # Print last comm message
    
    # Print EMG informations:
    print("Connected EMGs: " + str(len(emg_list)))
    for elem in emg_list:
        print("Channel: " + str(elem['chn']) + ' value: ' + str(elem['val']))
    
    # Print IMU informations:
    print("Connected IMUs: " + str(len(imu_list)))
    
    # Print PWM informations:
    print("PWM states (chn/val):")
    msg = ""
    for val in pwm_list:
        msg += str(val['chn']) + "    " + str(val['val'])
    print(msg)

def adc_aquisition_func():
    global emg_list, adc, last_message, send_last_message
    message, events = adc.update_connected_devices()
    if message != "":
        last_message = message
        send_last_message = True
    emg_list = []
    for elem in adc.connected_devices:
        if elem['actv'] == True:
            emg_list.append(elem) 
    for elem in events:
        elem['type'] = 'emg_event'
    return events
        
    
def main_func():
    global conn_message, last_message, emg_list, send_last_message
    with com.RoboCom(platform='bb') as c:
        c.start_communications()
        while(True):           
            conn_message = "Conn State: " + c.get_state()
            emg_events = adc_aquisition_func()
            
            if c.get_state() is 'Connected':
                if send_last_message is True:
                    c.send_data({'type':'message', 'message':last_message})
                    send_last_message = False
                for elem in emg_list:
                    to_send = elem.copy()
                    to_send['type'] = 'emg'
                    c.send_data(to_send)
                for elem in emg_events:
                    c.send_data(elem)
            
            print_func()
            time.sleep(0.1)            
                
        c.stop_and_free_resources()
        
main_func()