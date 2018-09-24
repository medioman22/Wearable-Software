# -*- coding: utf-8 -*-
"""
SoftWEAR demo program displaying the main features. This scripts executes on the
beagle bone. Starts a server and ADC, PWM and I2C SoftWEAR modules are polled;
and their status is reported to the remote location.
"""

import os                   # Required for clearing the system display
import time                 # Required for controllng the sampling period
#import RoboCom as com       # SoftWEAR Communication module
#import RoboADC as r_adc     # SoftWEAR ADC module
import RoboPWM as r_pwm     # SoftWEAR PWM module
#import RoboI2C as r_i2c     # SoftWEAR I2C module
import copy                 # Required for deepcopy on dictionary lists

emg_list = []               # List of connected EMG devices on the ADC ports
imu_list = []               # List of connected IMU devices on the I2C ports
pwm_list = []               # List of current PWM channels and their state
last_message = ""           # Current text message to be displayed to the user
send_last_message = False   # Becomes True when last message has changed.
conn_message = ""           # Current connection status to be displayed

#adc = r_adc.RoboADC()       # Initialize the SoftWEAR ADC Module
pwm = r_pwm.RoboPWM()       # Initialize the SoftWEAR PWM Module
#i2c = r_i2c.RoboI2C()       # Initialize the SoftWEAR I2C Module

def print_func():
    """ This function handles all the prints to the console. """
    global conn_message, last_message           # Uses the message global variables
    os.system('clear')                          # Clear console output
    print("manually break to exit program!\n")  # Print exit condition
    print(conn_message)                         # Print connection status
    print(last_message + "\n")                  # Print last comm message

    # Print EMG informations:
    """
    print("Connected EMGs: " + str(len(emg_list)))
    for elem in adc.all_devices:                # Go through all ADC devices
        if elem['actv']:                        # Only print active elements
            if len(elem['sublist']) > 0:        # Check if we hava a MUX
                for sub_elem in elem['sublist']:
                    if sub_elem['actv']:        # Print all elements of the MUX
                        print("Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['val']))
            else:                               # No MUX -> print element
                print("Channel " + str(elem['chn']) + ', value: ' + str(elem['val']))

    # Print IMU informations:
    print("\nConnected IMUs: " + str(len(imu_list)))
    for elem in i2c.all_devices:                # Go through all I2C devices
        if elem['actv']:                        # Only print active elements
            if len(elem['sublist']) > 0:        # Check if we have a MUX
                for sub_elem in elem['sublist']:
                    if sub_elem['actv']:        # Print all elements of the MUX
                        print("Channel " + str(elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['vals']))
            else:                               # No MUX -> print element
                print("Channel " + str(elem['chn']) + ' type: ' + elem['device'] +', values: ' + str(elem['vals']))
    """
    # Print PWM informations:
    print("\nPWM states:")
    for elem in pwm_list:                       # Print all PWM values
        print("Channel: " + str(elem['chn']) + ' value: ' + str(elem['val']))

def adc_aquisition_func():
    """ Function updates the status of all ADC devices and saves any connnect
        or disconnect events. """
    global emg_list, adc, last_message, send_last_message
    events = adc.update_devices()       # SoftWEAR ADC update devices on the ADC channels
    emg_list = []                       # Reset list of connected emg list
    new_last_message = ''               # Test if we have a new connect / disconnect message
    for elem in adc.connected_devices:
        emg_list.append(elem)           # Add all connected devices to the emg_list
    for elem in events:                 # Go through all ADC events
        elem['type'] = 'emg_event'      # Add the type for return reasons
        if elem['event'] == 'none':     # 'none' here means MUX event
            if elem['mux'] == 'conn':   # MUX connected event
                new_last_message += 'Connected MUX on ADC Channel ' + str(elem['chn']) + '\n'
            else:                       # MUX disconnected event
                new_last_message += 'Disconnected MUX on ADC Channel ' + str(elem['chn']) + '\n'
        elif elem['event'] == 'conn':   # Channel Connected event
            if elem['subchn'] == -1:    # Connected directly (not through MUX)
                new_last_message += 'Connected EMG on ADC Channel ' + str(elem['chn']) + '\n'
            else:                       # Connected through MUX
                new_last_message += 'Connected EMG on ADC Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
        else:                           # Channel Disconnected event
            if elem['subchn'] == -1:    # Direct disconnnection (not through MUX)
                new_last_message += 'Disconnected EMG on ADC Channel ' + str(elem['chn']) + '\n'
            else:                       # Disconnected on MUX
                new_last_message += 'Disconnected EMG on ADC Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'

    if new_last_message is not '':      # Check for any event present
        last_message = new_last_message # IF we have an event -> save text message
        send_last_message = True        # and mark it for sending
    return events, adc.all_devices

def i2c_aquisition_func():
    """ Function updates the status of all ADC devices and saves any connnect
        or disconnect events. """
    global imu_list, i2c, last_message, send_last_message
    events = i2c.update_devices()       # SoftWEAR ADC update devices on the I2C channels
    imu_list = []                       # Reset list of connected I2C list
    new_last_message = ''               # Test if we have a new connect / disconnect message
    for elem in i2c.connected_devices:
        imu_list.append(elem)           # Add all connected devices to the imu_list
    for elem in events:                 # Go through all I2C events
        elem['type'] = 'imu_event'      # Add the type for return reasons
        if elem['event'] == 'none':     # 'none' here means MUX event
            if elem['mux'] == 'conn':   # MUX connected event
                new_last_message += 'Connected MUX on I2C Channel ' + str(elem['chn']) + '\n'
            else:                       # MUX disconnected event
                new_last_message += 'Disconnected MUX on I2C Channel ' + str(elem['chn']) + '\n'
        elif elem['event'] == 'conn':   # Channel Connected event
            if elem['subchn'] == -1:    # Connected directly (not through MUX)
                new_last_message += 'Connected IMU on I2C Channel ' + str(elem['chn']) + '\n'
            else:                       # Connected through MUX
                new_last_message += 'Connected IMU on I2C Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
        else:                           # Channel Disconnected event
            if elem['subchn'] == -1:    # Direct disconnnection (not through MUX)
                new_last_message += 'Disconnected IMU on I2C Channel ' + str(elem['chn']) + '\n'
            else:                       # Disconnected on MUX
                new_last_message += 'Disconnected IMU on I2C Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'

    if new_last_message is not '':      # Check for any event present
        last_message = new_last_message # IF we have an event -> save text message
        send_last_message = True        # and mark it for sending
    return events, i2c.all_devices

def pwm_aquisition_func():
    """ Function updates the status of all PWM channels """
    global pwm_list, pwm
    pwm_list = pwm.get_all_values()     # SoftWEAR read all PWM channels
    ret_list = copy.deepcopy(pwm_list)  # Deep copy the dictionary list

    # Add the type to the return object. This will be sent on the network
    ret_message = {'type':'pwm_read', 'pwm_list':ret_list}
    return ret_message

def main_func():
    """ Main infinite loop function. Reads all devices and manages the connection. """
    global conn_message, last_message, emg_list, send_last_message, pwm
    # Create the communication class. Using 'with' to ensure correct termination.
    with com.RoboCom(platform='bb') as c:
        c.start_communications()        # Start the communication
        while(True):                    # Enter the infinite loop
            # Get the connection state for printing reasons
            conn_message = "Conn State: " + c.get_state()

            # Get the ADC devices and events
            emg_events, emg_devices = adc_aquisition_func()

            # Get the PWM values
            pwm_message = pwm_aquisition_func()

            # Get the I2C devices and events
            i2c_events, i2c_devices = i2c_aquisition_func()

            if c.get_state() is 'Connected':
                # Send Text message
                if send_last_message is True:
                    c.send_data({'type':'message', 'message':last_message})
                    send_last_message = False

                # Handle EMGs on the ADC channels
                to_send  = {'type':'emg', 'channels':emg_devices}
                c.send_data(to_send)
                for elem in emg_events:
                    c.send_data(elem)   # Send the ADC device info over the network

                # Handle IMUs on the I2C channels
                to_send  = {'type':'imu', 'channels':i2c_devices}
                c.send_data(to_send)
                for elem in i2c_events:
                    c.send_data(elem)   # Send the I2C device info over the network

                # Send the PWM state
                c.send_data(pwm_message)

            recv_data = c.rcv_data()
            for message in recv_data:
                if message['type'] == 'pwm_set':
                    # Pwm command from the remote location
                    pwm.write_pin(message['chn'], message['val'])
                    last_message = "New PWM command: cnh:" + str(message['chn']) + " val:" + str(message['val'])

            print_func()                # Call print function
            time.sleep(0.1)             # Sleep until next sampling period

        # If we reach this -> something happened. Close communication channel
        c.stop_and_free_resources()

# Just call the main function.
main_func()
