# -*- coding: utf-8 -*-
"""
SoftWEAR demo program displaying the main features. This scripts executes on the
beagle bone. Starts a server and ADC, PWM and I2C SoftWEAR modules are polled;
and their status is reported to the remote location.
"""

import os                   # Required for clearing the system display
import time                 # Required for controllng the sampling period
import threading               # Threading class for the threads
import RoboComConnection as com # SoftWEAR Communication module
import MuxModule            # SoftWEAR MUX module
import InputModule          # SoftWEAR Input module
#import RoboADC as r_adc     # SoftWEAR ADC module
#import RoboPWM as r_pwm     # SoftWEAR PWM module
import RoboI2C as r_i2c     # SoftWEAR I2C module
#import copy                 # Required for deepcopy on dictionary lists
import json                 # Serializing class. All objects sent are serialized

exit = False                # Exit flag to terminate all threads
c = None                    # Connection object

inputList = []             # List of connected Input devices on the GPIO pins
emg_list = []               # List of connected EMG devices on the ADC ports
i2c_list = []               # List of connected IMU devices on the I2C ports
pwm_list = []               # List of current PWM channels and their state
last_message = ""           # Current text message to be displayed to the user
send_last_message = False   # Becomes True when last message has changed.
conn_message = ""           # Current connection status to be displayed

input = InputModule.Input() # Initialize the SoftWEAR Input Module
#adc = r_adc.RoboADC()      # Initialize the SoftWEAR ADC Module
#pwm = r_pwm.RoboPWM()      # Initialize the SoftWEAR PWM Module
i2c = r_i2c.RoboI2C()       # Initialize the SoftWEAR I2C Module

def print_func():
    """Handle all the prints to the console."""
    global conn_message, last_message           # Uses the message global variables
    os.system('clear')                          # Clear console output
    print("manually break to exit program!\n")  # Print exit condition
    print(conn_message)                         # Print connection status
    print(last_message + "\n")                  # Print last comm message

    # Print Input informations:
    print("\nConnected Inputs: " + str(len(inputList)))
    for el in inputList:                        # Go through all connected Input devices
        # if len(elem['sublist']) > 0:            # Check if we have a MUX
        #     for sub_elem in elem['sublist']:
        #         if sub_elem['actv']:            # Print all elements of the MUX
        #             print("Channel " + str(elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['vals']))
        # else:                                   # No MUX -> print element
        if el['mux'] != -1:                     # Muxed pin
            print("Pin " + str(el['pin']) + ':' + str(el['mux']) + ' type: ' + el['device'] +', values: ' + str(el['vals']))
        else:                                   # Unmuxed pin
            print("Pin " + str(el['pin']) + ' type: ' + el['device'] +', values: ' + str(el['vals']))
    # # Print EMG informations:
    # print("Connected EMGs: " + str(len(emg_list)))
    # for elem in adc.all_devices:                # Go through all ADC devices
    #     if elem['actv']:                        # Only print active elements
    #         if len(elem['sublist']) > 0:        # Check if we hava a MUX
    #             for sub_elem in elem['sublist']:
    #                 if sub_elem['actv']:        # Print all elements of the MUX
    #                     print("Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['val']))
    #         else:                               # No MUX -> print element
    #             print("Channel " + str(elem['chn']) + ', value: ' + str(elem['val']))
    #
    # Print IMU informations:
    print("\nConnected IMUs: " + str(len(i2c_list)))
    for elem in i2c_list:                       # Go through all connected I2C devices
        # if len(elem['sublist']) > 0:            # Check if we have a MUX
        #     for sub_elem in elem['sublist']:
        #         if sub_elem['actv']:            # Print all elements of the MUX
        #             print("Channel " + str(elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['vals']))
        # else:                                   # No MUX -> print element
        print("Channel " + str(elem['chn']) + ' type: ' + elem['device'] +', values: ' + str(elem['vals']))
    #
    # # Print PWM informations:
    # print("\nPWM states:")
    # for elem in pwm_list:                       # Print all PWM values
    #     print("Channel: " + str(elem['chn']) + ' value: ' + str(elem['val']))

# def adc_aquisition_func():
#     """ Function updates the status of all ADC devices and saves any connnect
#         or disconnect events. """
#     global emg_list, adc, last_message, send_last_message
#     events = adc.update_devices()       # SoftWEAR ADC update devices on the ADC channels
#     emg_list = []                       # Reset list of connected emg list
#     new_last_message = ''               # Test if we have a new connect / disconnect message
#     for elem in adc.connected_devices:
#         emg_list.append(elem)           # Add all connected devices to the emg_list
#     for elem in events:                 # Go through all ADC events
#         elem['type'] = 'emg_event'      # Add the type for return reasons
#         if elem['event'] == 'none':     # 'none' here means MUX event
#             if elem['mux'] == 'conn':   # MUX connected event
#                 new_last_message += 'Connected MUX on ADC Channel ' + str(elem['chn']) + '\n'
#             else:                       # MUX disconnected event
#                 new_last_message += 'Disconnected MUX on ADC Channel ' + str(elem['chn']) + '\n'
#         elif elem['event'] == 'conn':   # Channel Connected event
#             if elem['subchn'] == -1:    # Connected directly (not through MUX)
#                 new_last_message += 'Connected EMG on ADC Channel ' + str(elem['chn']) + '\n'
#             else:                       # Connected through MUX
#                 new_last_message += 'Connected EMG on ADC Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
#         else:                           # Channel Disconnected event
#             if elem['subchn'] == -1:    # Direct disconnnection (not through MUX)
#                 new_last_message += 'Disconnected EMG on ADC Channel ' + str(elem['chn']) + '\n'
#             else:                       # Disconnected on MUX
#                 new_last_message += 'Disconnected EMG on ADC Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
#
#     if new_last_message is not '':      # Check for any event present
#         last_message = new_last_message # IF we have an event -> save text message
#         send_last_message = True        # and mark it for sending
#     return events, adc.all_devices
#
def inputScan():
    """Scan for new input devices."""
    global inputList, input, last_message, send_last_message
    input.scan()                                            # Update devices on the input pins
    inputListPrevious = inputList                           # Keep copy of last input devices
    inputList = []                                          # Reset list of connected Input list
    inputListRegister = []                                  # List of new devices that need to be registered
    inputListDeregister = []                                # List of new devices that need to be deregistered
    new_last_message = ''                                   # Test if we have a new connect / disconnect message

    for el1 in input.connectedDevices:                      # Check for connected and new devices
        if (len(filter(lambda el2: el2['device'] == el1['device'], inputListPrevious)) > 0):
            inputList.append(el1)                           # Add to connected list
        else:                                               # Device is not yet registered
            inputListRegister.append(el1)                   # Add to register list
            inputList.append(el1)                           # Add connected list

    for el1 in inputListPrevious:                           # Check for disconnected devices
        if (len(filter(lambda el2: el2['device'] == el1['device'], inputList)) == 0):
            inputListDeregister.append(el1)                 # Add to deregister list

    if new_last_message is not '':                          # Check for any event present
        last_message = new_last_message                     # IF we have an event -> save text message
        send_last_message = True                            # and mark it for sending
    return inputListRegister, inputListDeregister


def inputUpdate():
    """Update the input devices."""
    input.updateValues()


def i2c_scan():
    """Update the status of all I2C devices and saves any connect or disconnect events."""
    global i2c_list, i2c, last_message, send_last_message
    i2c.update()                                            # Update devices on the I2C channels
    i2c_list_previous = i2c_list                            # Keep copy of last i2c devices
    i2c_list = []                                           # Reset list of connected I2C list
    i2c_list_register = []                                  # List of new devices that need to be registered
    i2c_list_deregister = []                                # List of new devices that need to be deregistered
    new_last_message = ''                                   # Test if we have a new connect / disconnect message

    for el1 in i2c.connected_devices:                       # Check for connected and new devices
        if (len(filter(lambda el2: el2['device'] == el1['device'], i2c_list_previous)) > 0):
            i2c_list.append(el1)                            # Add to connected list
        else:                                               # Device is not yet registered
            i2c_list_register.append(el1)                   # Add to register list
            i2c_list.append(el1)                            # Add connected list

    for el1 in i2c_list_previous:                           # Check for disconnected devices
        if (len(filter(lambda el2: el2['device'] == el1['device'], i2c_list)) == 0):
            i2c_list_deregister.append(el1)                 # Add to deregister list

    # for elem in events:                                     # Go through all I2C events
    #     elem['type'] = 'imu_event'                          # Add the type for return reasons
    #     if elem['event'] == 'none':                         # 'none' here means MUX event
    #         if elem['mux'] == 'conn':                       # MUX connected event
    #             new_last_message += 'Connected MUX on I2C Channel ' + str(elem['chn']) + '\n'
    #         else:                                           # MUX disconnected event
    #             new_last_message += 'Disconnected MUX on I2C Channel ' + str(elem['chn']) + '\n'
    #     elif elem['event'] == 'conn':                       # Channel Connected event
    #         if elem['subchn'] == -1:                        # Connected directly (not through MUX)
    #             new_last_message += 'Connected IMU on I2C Channel ' + str(elem['chn']) + '\n'
    #         else:                                           # Connected through MUX
    #             new_last_message += 'Connected IMU on I2C Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'
    #     else:                                               # Channel Disconnected event
    #         if elem['subchn'] == -1:                        # Direct disconnnection (not through MUX)
    #             new_last_message += 'Disconnected IMU on I2C Channel ' + str(elem['chn']) + '\n'
    #         else:                                           # Disconnected on MUX
    #             new_last_message += 'Disconnected IMU on I2C Channel ' + str(elem['chn']) + ' Mux ' + str(elem['subchn']) + '\n'

    if new_last_message is not '':                          # Check for any event present
        last_message = new_last_message                     # IF we have an event -> save text message
        send_last_message = True                            # and mark it for sending
    return i2c_list_register, i2c_list_deregister

# def pwm_aquisition_func():
#     """ Function updates the status of all PWM channels """
#     global pwm_list, pwm
#     pwm_list = pwm.get_all_values()     # SoftWEAR read all PWM channels
#     ret_list = copy.deepcopy(pwm_list)  # Deep copy the dictionary list
#
#     # Add the type to the return object. This will be sent on the network
#     ret_message = {'type':'pwm_read', 'pwm_list':ret_list}
#     return ret_message

def scanThread():
    """Thread dedicated to scan for new devices."""
    global c
    while True:                                                     # Enter the infinite loop
        messagesSend = []                                           # List of messages to send

        i2c_list_register, i2c_list_deregister = i2c_scan()         # Get the I2C devices and events
        inputListRegister, inputListDeregister = inputScan()        # Get the Input devices and events


        for device in i2c_list_deregister:                          # Create i2c device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['device']}))



        for device in i2c_list_register:                            # Create i2c device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['device'],
                                            'dir': device['dir'],
                                            'dim': device['dim']}))

        for device in inputListDeregister:                          # Create input device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['device']}))



        for device in inputListRegister:                            # Create input device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['device'],
                                            'dir': device['dir'],
                                            'dim': device['dim']}))


        c.sendMessages(messagesSend)                                # Send the messages
        time.sleep(1)                                               # Sleep until next scan period

        if exit:                                                    # Exit
            break;


def updateThread():
    """Thread dedicated to get updated values of the devices."""
    global c
    while True:                                                     # Enter the infinite loop
        messagesSend = []                                           # List of messages to send
        messagesRecv = c.getMessages()                              # Get new messages

        inputUpdate()                                               # Update input devices

        for messageString in messagesRecv:
            message = json.loads(messageString)                     # Parse message from string to JSON
            if message['type'] == 'DeviceList':                     # Create i2c device register message for all devices
                for device in i2c_list:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['device'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim']}))


        for device in i2c_list:                                     # Create i2c device data message
            messagesSend.append(json.dumps({'type': 'Data',
                                            'name': device['device'],
                                            'values': device['vals']}))


        for device in inputList:                                   # Create input device data message
            messagesSend.append(json.dumps({'type': 'Data',
                                            'name': device['device'],
                                            'values': device['vals']}))


        c.sendMessages(messagesSend)                                # Send the messages
        time.sleep(0.1)                                             # Sleep until next update period

        if exit:                                                    # Exit
            break;

def main():
    """Infinite loop function, reads all devices and manages the connection."""
    global conn_message, last_message, emg_list, send_last_message, pwm, c, exit
                                                                    # Create the communication class. Using 'with' to ensure correct termination.
    c = com.RoboComConnection()                                     # Create the communication
    c.connect()                                                     # Start communication thread
    scan = threading.Thread(target=scanThread, name="ScanThread")   # Create scan thread
    scan.daemon = True                                              # Set scan thread as daemonic
    scan.start()                                                    # Start scan thread
    update = threading.Thread(target=updateThread, name="UpdateThread") # Create update thread
    update.daemon = True                                            # Set update thread as daemonic
    update.start()                                                  # Start update thread
    while(True):                                                    # Enter the infinite loop
        conn_message = "Conn State: " + c.getState()                # Get the connection state for printing reasons
        """Ping"""
        # if c.getState() is 'Connected':
        #     sendMessages = [json.dumps({'type': 'Ping','name':''})]
        #     c.sendMessages(sendMessages)

        print_func()                                                # Call print function
        time.sleep(0.1)                                             # Sleep until next print period

    # If we reach this -> something happened. Close communication channel
    exit = True
    c.stopAndFreeResources()

# Just call the main function.
main()
