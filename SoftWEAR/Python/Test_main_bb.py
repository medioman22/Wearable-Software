# -*- coding: utf-8 -*-
"""

"""

import os as os
import time as time
import RoboCom as com
import RoboADC as r_adc
import RoboPWM as r_pwm
import copy

emg_list = []
imu_list = []
pwm_list = []
last_message = ""
send_last_message = False
conn_message = ""

adc = r_adc.RoboADC()
pwm = r_pwm.RoboPWM()

def print_func():
    global conn_message, last_message
    os.system('clear')                          # Clear console output
    print("manually break to exit program!\n\n")# Print exit condition
    print(conn_message)
    print(last_message + "\n")                  # Print last comm message
    
    # Print EMG informations:
    print("Connected EMGs: " + str(len(emg_list)))
    for elem in adc.all_devices:
        if elem['actv']:
            if len(elem['sublist']) > 0:
                for sub_elem in elem['sublist']:
                    if sub_elem['actv']:
                        print("Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['val']))
            else:
                print("Channel " + str(elem['chn']) + ', value: ' + str(elem['val']))
    
    # Print IMU informations:
    print("\nConnected IMUs: " + str(len(imu_list)))
    
    # Print PWM informations:
    print("\nPWM states:")
    for elem in pwm_list:
        print("Channel: " + str(elem['chn']) + ' value: ' + str(elem['val']))

def adc_aquisition_func():
    global emg_list, adc, last_message, send_last_message
    events = adc.update_devices()
    emg_list = []
    new_last_message = ''
    for elem in adc.connected_devices:
        emg_list.append(elem) 
    for elem in events:
        elem['type'] = 'emg_event'
        if elem['event'] == 'none':
            if elem['mux'] == 'conn':
                new_last_message += 'Connected MUX on Channel ' + str(elem['chn']) + '\n'
            else:
                new_last_message += 'Disconnected MUX on Channel ' + str(elem['chn']) + '\n'
        elif elem['event'] == 'conn':
            if elem['subchn'] == -1:
                new_last_message += 'Connected IMU on Channel ' + str(elem['chn']) + '\n'
            else:
                new_last_message += 'Connected IMU on Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
        else:
            if elem['subchn'] == -1:
                new_last_message += 'Disconnected IMU on Channel ' + str(elem['chn']) + '\n'
            else:
                new_last_message += 'Disconnected IMU on Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
    if new_last_message is not '':
        last_message = new_last_message
        send_last_message = True
    return events, adc.all_devices
        
def pwm_aquisition_func():
    global pwm_list, pwm
    pwm_list = pwm.get_all_values()
    ret_list = copy.deepcopy(pwm_list)
    ret_message = {'type':'pwm_read', 'pwm_list':ret_list}
    return ret_message
    
def main_func():
    global conn_message, last_message, emg_list, send_last_message, pwm
    with com.RoboCom(platform='bb') as c:
        c.start_communications()
        while(True):           
            conn_message = "Conn State: " + c.get_state()
            emg_events, emg_devices = adc_aquisition_func()
            pwm_message = pwm_aquisition_func()
            
            if c.get_state() is 'Connected':
                if send_last_message is True:
                    c.send_data({'type':'message', 'message':last_message})
                    send_last_message = False
                to_send  = {'type':'emg', 'channels':emg_devices}
                c.send_data(to_send)
                for elem in emg_events:
                    c.send_data(elem)
                c.send_data(pwm_message)
            
            recv_data = c.rcv_data()
            for message in recv_data: 
                if message['type'] == 'pwm_set':
                    pwm.write_pin(message['chn'], message['val'])
                    last_message = "New PWM command: cnh:" + str(message['chn']) + " val:" + str(message['val'])
            
            print_func()
            time.sleep(0.1)            
                
        c.stop_and_free_resources()
        
main_func()