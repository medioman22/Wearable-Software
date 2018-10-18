# -*- coding: utf-8 -*-
"""
SoftWEAR demo program displaying the main features. This scripts executes on the
beagle bone. Starts a server and ADC, PWM and I2C SoftWEAR modules are polled;
and their status is reported to the remote location.
"""

import os                                                       # Required for clearing the system display
import time                                                     # Required for controllng the sampling period
import threading                                                # Threading class for the threads
import Config                                                   # SoftWEAR Config
import CommunicationModule                                      # SoftWEAR Communication module
import MuxModule                                                # SoftWEAR MUX module
import InputModule                                              # SoftWEAR Input module
import ADCModule                                                # SoftWEAR ADC module
import I2CModule                                                # SoftWEAR I2C module
#import RoboADC as r_adc                                        # SoftWEAR ADC module
#import RoboPWM as r_pwm                                        # SoftWEAR PWM module
import json                                                     # Serializing class. All objects sent are serialized

BOARD = "Beaglebone Green Wireless v1.0"                        # Name of the Board
SOFTWARE = "SoftWEAR/Firmware-BeagleboneGreenWireless(v0.1)"    # Identifier of the Software

scanForDevices = True                                           # Scanning enabled as default
exit = False                                                    # Exit flag to terminate all threads
c = None                                                        # Connection object

inputList = []                                                  # List of connected Input devices on the GPIO pins
adcList = []                                                    # List of connected ADC devices on the Analog pins
i2cList = []                                                    # List of connected IMU devices on the I2C ports
pwm_list = []                                                   # List of current PWM channels and their state
connectionState = ""                                            # Current connection state to be displayed

MuxShadow = MuxModule.Mux()                                     # Initialize the SoftWEAR Mux Module
input = InputModule.Input()                                     # Initialize the SoftWEAR Input Module
adc = ADCModule.ADC()                                           # Initialize the SoftWEAR ADC Module
i2c = I2CModule.I2C()                                           # Initialize the SoftWEAR I2C Module
#adc = r_adc.RoboADC()                                          # Initialize the SoftWEAR ADC Module
#pwm = r_pwm.RoboPWM()                                          # Initialize the SoftWEAR PWM Module

def print_func():
    """Handle all the prints to the console."""
    global connectionState                                      # Uses the message global variables
    os.system('clear')                                          # Clear console output
    print("****************************************************************")
    print("* Hardware:    {}                  *".format(BOARD))                                        # Display hardware information
    print("* Software:    {} *".format(SOFTWARE))                                                      # Display software information
    print("* Layout:      {}                                       *".format(Config.LAYOUT))           # Display layout information
    print("****************************************************************")
    print("")
    print("Connection:  {}".format(connectionState))            # Print connection status

    # Print Input informations:
    print("\nConnected Inputs: " + str(len(inputList)))
    for el in inputList:                                        # Go through all connected Input devices
        if el['mux'] != -1:                                     # Muxed pin
            print('({}:{}) {}: {} / {}'.format(str(el['pin']), str(el['mux']), el['name'], str(el['about']['dimMap']), str(el['vals'])))
        else:                                                   # Unmuxed pin
            print('({}) {}: {} / {}'.format(str(el['pin']), el['name'], str(el['about']['dimMap']), str(el['vals'])))
    # Print ADC informations:
    print("\nConnected ADCs: " + str(len(adcList)))
    for el in adcList:                                          # Go through all connected ADC devices
        if el['mux'] != -1:                                     # Muxed pin
            print('({}:{}) {}: {} / {}'.format(str(el['pin']), str(el['mux']), el['name'], str(el['about']['dimMap']), str(el['vals'])))
        else:                                                   # Unmuxed pin
            print('({}) {}: {} / {}'.format(str(el['pin']), el['name'], str(el['about']['dimMap']), str(el['vals'])))
    # Print IMU informations:
    print("\nConnected IMUs: " + str(len(i2cList)))
    for el in i2cList:                                        # Go through all connected I2C devices
        print('(Channel {}) {}: {} / {}'.format(str(el['channel']), el['name'], str(el['about']['dimMap']), str(el['vals'])))
    #
    # # Print PWM informations:
    # print("\nPWM states:")
    # for elem in pwm_list:                       # Print all PWM values
    #     print("Channel: " + str(elem['chn']) + ' value: ' + str(elem['val']))

    print("\n\nManually break to exit!")                        # Print exit condition
    print(">> Ctrl-C\n")                                        # Print exit shortcut

def inputScan():
    """Scan for new input devices."""
    global inputList, input
    input.scan()                                                # Scan devices on the input pins
    inputListPrevious = inputList                               # Keep copy of last input devices
    inputList = []                                              # Reset list of connected Input list
    inputListRegister = []                                      # List of new devices that need to be registered
    inputListDeregister = []                                    # List of new devices that need to be deregistered

    for el1 in input.connectedDevices:                          # Check for connected and new devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], inputListPrevious)) > 0):
            inputList.append(el1)                               # Add to connected list
        else:                                                   # Device is not yet registered
            inputListRegister.append(el1)                       # Add to register list
            inputList.append(el1)                               # Add connected list

    for el1 in inputListPrevious:                               # Check for disconnected devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], inputList)) == 0):
            inputListDeregister.append(el1)                     # Add to deregister list

    return inputListRegister, inputListDeregister


def inputUpdate():
    """Update the input devices."""
    input.updateValues()


def adcScan():
    """Scan for new adc devices."""
    global adcList, adc
    adc.scan()                                                  # Scan devices on the analog pins
    adcListPrevious = adcList                                   # Keep copy of last adc devices
    adcList = []                                                # Reset list of connected ADC list
    adcListRegister = []                                        # List of new devices that need to be registered
    adcListDeregister = []                                      # List of new devices that need to be deregistered

    for el1 in adc.connectedDevices:                            # Check for connected and new devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], adcListPrevious)) > 0):
            adcList.append(el1)                                 # Add to connected list
        else:                                                   # Device is not yet registered
            adcListRegister.append(el1)                         # Add to register list
            adcList.append(el1)                                 # Add connected list

    for el1 in adcListPrevious:                                 # Check for disconnected devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], adcList)) == 0):
            adcListDeregister.append(el1)                       # Add to deregister list

    return adcListRegister, adcListDeregister


def adcUpdate():
    """Update the input devices."""
    adc.updateValues()


def i2cScan():
    """Update the status of all I2C devices and saves any connect or disconnect events."""
    global i2cList, i2c
    i2c.scan()                                                  # Scan devices on the I2C channels
    i2cListPrevious = i2cList                                   # Keep copy of last i2c devices
    i2cList = []                                                # Reset list of connected I2C list
    i2cListRegister = []                                        # List of new devices that need to be registered
    i2cListDeregister = []                                      # List of new devices that need to be deregistered

    for el1 in i2c.connectedDevices:                            # Check for connected and new devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], i2cListPrevious)) > 0):
            i2cList.append(el1)                                 # Add to connected list
        else:                                                   # Device is not yet registered
            i2cListRegister.append(el1)                         # Add to register list
            i2cList.append(el1)                                 # Add connected list

    for el1 in i2cListPrevious:                                 # Check for disconnected devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], i2cList)) == 0):
            i2cListDeregister.append(el1)                       # Add to deregister list

    return i2cListRegister, i2cListDeregister

def i2cUpdate():
    """Update the I2C devices."""
    i2c.updateValues()

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
    global c, scanForDevices
    while True:                                                 # Enter the infinite loop
        if not scanForDevices:                                  # Check for scanning
            time.sleep(1)
            continue

        messagesSend = []                                       # List of messages to send

        inputListRegister, inputListDeregister = inputScan()    # Get the Input devices and events
        adcListRegister, adcListDeregister = adcScan()          # Get the ADC devices and events
        i2cListRegister, i2cListDeregister = i2cScan()          # Get the I2C devices and events


        for device in inputListDeregister:                      # Create input device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['name']}))



        for device in inputListRegister:                        # Create input device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['name'],
                                            'dir': device['dir'],
                                            'dim': device['dim'],
                                            'about': device['about'],
                                            'settings': device['settings'],
                                            'mode': device['mode']}))

        for device in adcListDeregister:                        # Create ADC device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['name']}))



        for device in adcListRegister:                          # Create ADC device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['name'],
                                            'dir': device['dir'],
                                            'dim': device['dim'],
                                            'about': device['about'],
                                            'settings': device['settings'],
                                            'mode': device['mode']}))

        for device in i2cListDeregister:                        # Create I2C device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['name']}))



        for device in i2cListRegister:                          # Create I2C device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['name'],
                                            'dir': device['dir'],
                                            'dim': device['dim'],
                                            'about': device['about'],
                                            'settings': device['settings'],
                                            'mode': device['mode'],
                                            'flags': device['flags']}))

        if c.getState() == 'Connected':
            c.sendMessages(messagesSend)                        # Send the messages
        time.sleep(1)                                           # Sleep until next scan period

        if exit:                                                # Exit
            break;


def updateThread():
    """Thread dedicated to get updated values of the devices."""
    global c, scanForDevices
    while True:                                                 # Enter the infinite loop
        messagesSend = []                                       # List of messages to send
        messagesRecv = c.getMessages()                          # Get new messages

        inputUpdate()                                           # Update input devices
        adcUpdate()                                             # Update ADC devices
        i2cUpdate()                                             # Update I2C devices

        for messageString in messagesRecv:
            message = json.loads(messageString)                 # Parse message from string to JSON
            if message['type'] == 'DeviceList':                 # Create device register message for all devices
                for device in inputList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode']}))
                for device in adcList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode']}))
                for device in i2cList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode'],
                                                    'flags': device['flags']}))
            if message['type'] == 'Settings':                   # Change settings for a device
                print(message)
                for device in inputList:
                    if device['name'] == message['name']:       # Check for device name
                        input.settings(message)
                for device in adcList:
                    if device['name'] == message['name']:       # Check for device name
                        adc.settings(message)
                for device in i2cList:
                    if device['name'] == message['name']:       # Check for device name
                        i2c.settings(message)

            if message['type'] == 'Scan':                       # Change scan for a device
                scanForDevices = message['value']

        for device in inputList:                                # Create input device data message
            messagesSend.append(json.dumps({'type': 'Data',
                                            'name': device['name'],
                                            'values': device['vals'],
                                            'timestamp': device['timestamp']}))

        for device in adcList:                                  # Create adc device data message
            messagesSend.append(json.dumps({'type': 'Data',
                                            'name': device['name'],
                                            'values': device['vals'],
                                            'timestamp': device['timestamp']}))


        for device in i2cList:                                  # Create i2c device data message
            messagesSend.append(json.dumps({'type': 'Data',
                                            'name': device['name'],
                                            'values': device['vals'],
                                            'timestamp': device['timestamp']}))


        if c.getState() == 'Connected':
            c.sendMessages(messagesSend)                        # Send the messages
        time.sleep(0.1)                                         # Sleep until next update period

        if exit:                                                # Exit
            break;

def main():
    """Infinite loop function, reads all devices and manages the connection."""
    global connectionState, c, exit

                                                                # Create the communication class. Using 'with' to ensure correct termination.
    c = CommunicationModule.CommunicationConnection()           # Create the communication
    c.connect()                                                 # Start communication thread
    scan = threading.Thread(target=scanThread, name="ScanThread") # Create scan thread
    scan.daemon = True                                          # Set scan thread as daemonic
    scan.start()                                                # Start scan thread
    update = threading.Thread(target=updateThread, name="UpdateThread") # Create update thread
    update.daemon = True                                        # Set update thread as daemonic
    update.start()                                              # Start update thread

    while(True):                                                # Enter the infinite loop
        connectionState = c.getState()                          # Get the connection state for printing reasons
        """Ping"""
        # if c.getState() is 'Connected':
        #     sendMessages = [json.dumps({'type': 'Ping','name':''})]
        #     c.sendMessages(sendMessages)

        print_func()                                            # Call print function
        time.sleep(0.1)                                         # Sleep until next print period

    # If we reach this -> something happened. Close communication channel
    exit = True
    c.stopAndFreeResources()

# Just call the main function.
main()
