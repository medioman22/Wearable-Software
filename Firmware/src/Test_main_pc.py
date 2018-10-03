# -*- coding: utf-8 -*-
"""

"""

import os as os
import time as time
import RoboCom as com

emg_list = []
imu_list = []
pwm_rcv_list = []
pwm_send_list = [{'channel':1, 'val':50}, {'channel':2, 'val':25}, {'channel':3, 'val':75}]

last_message = ""
conn_message = ""



def print_func():
    global conn_message, last_message, emg_list
    os.system('cls')                            # Clear console output
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
    for val in pwm_rcv_list:
        msg += str(val['chn']) + "    " + str(val['val'])
    print(msg)
    
def process_emg(message):
    """ Processes a new emg message """
    global last_message, emg_list
    if message['type'] == 'emg':
        try:    # Try and see if we can fetch the channel to update the value
            temp = next(item for item in emg_list if item['chn'] == message['chn'])
            temp['val'] = message['val']
        except: # If not, create a new element with the channel and value
            new_item = {'chn':message['chn'], 'val':message['val']}
            emg_list.append(new_item)
    elif message['type'] == 'emg_event' and message['event'] == 'disc':
        to_del_idx = next((idx for idx, e in enumerate(emg_list) if e["chn"] == message['chn']))
        del emg_list[to_del_idx]
    
def main_func():
    global conn_message, last_message
    with com.RoboCom(platform='pc') as c:
        
        c.start_communications()
            
        while(True):     
            conn_message = "Conn State: " + c.get_state()
            
            recv_data = c.rcv_data()
            for message in recv_data: 
                if message['type'] == 'message':
                    last_message = message['message']
                if 'emg' in message['type']:
                    process_emg(message)
                elif 'imu' in message['type']:
                    pass
                    
            print_func()
            time.sleep(0.1)            
                
        c.stop_and_free_resources()
        
main_func()