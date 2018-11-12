# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
SoftWEAR demo program displaying the main features. This scripts executes on the
beagle bone. Starts a server and ADC, PWM and I2C SoftWEAR modules are polled;
and their status is reported to the remote location.
"""

import os                                                       # Required for clearing the system display
import sys                                                      # Required for get input args
import time                                                     # Required for controllng the sampling period
import threading                                                # Threading class for the threads
import Config                                                   # SoftWEAR Config
import CommunicationModule                                      # SoftWEAR Communication module
import MuxModule                                                # SoftWEAR MUX module
import InputModule                                              # SoftWEAR Input module
import OutputModule                                             # SoftWEAR Output module
import PWMModule                                                # SoftWEAR PWM module
import ADCModule                                                # SoftWEAR ADC module
import I2CModule                                                # SoftWEAR I2C module
import json                                                     # Serializing class. All objects sent are serialized
from termcolor import colored                                   # Color printing in the console
import cProfile                                                 # Used to profile the script

BOARD = "Beaglebone Green Wireless v1.0"                        # Name of the Board
SOFTWARE = "SoftWEAR/Firmware-BeagleboneGreenWireless(v0.1)"    # Identifier of the Software

LIVE_PRINT = False                                              # Flag whether live printing should be enabled in the console
DIAG_LOG = False                                                # Flag whether diagnostics should be logged to a file
DATA_LOG = False                                                # Flag whether data should be logged to a file
EVENT_LOG = False                                               # Flag whether events should be logged to a file

PRINT_PERIODE = 0.2                                             # Print periode to display values of devices in terminal
UPDATE_PERIODE = 0.1                                            # Update periode to refresh values
SCAN_PERIODE = 2                                                # Scan periode to refresh values

scanForDevices = True                                           # Scanning enabled as default
exit = False                                                    # Exit flag to terminate all threads
c = None                                                        # Connection object

inputList = []                                                  # List of connected Input devices on the GPIO pins
outputList = []                                                 # List of connected Output devices on the GPIO pins
pwmList = []                                                     # List of connected PWM devices on the GPIO pins
adcList = []                                                    # List of connected ADC devices on the Analog pins
i2cList = []                                                    # List of connected IMU devices on the I2C ports
connectionState = ""                                            # Current connection state to be displayed
updateDuration = 0                                              # Cycle duration needed to update values
scanDuration = 0                                                # Cycle duration needed to scan for new devices

mux = MuxModule.GetMux()                                        # Initialize the SoftWEAR Mux Module
input = InputModule.Input()                                     # Initialize the SoftWEAR Input Module
output = OutputModule.Output()                                  # Initialize the SoftWEAR Output Module
pwm = PWMModule.PWM()                                           # Initialize the SoftWEAR PWM Module
adc = ADCModule.ADC()                                           # Initialize the SoftWEAR ADC Module
i2c = I2CModule.I2C()                                           # Initialize the SoftWEAR I2C Module

def muxScan():
    """Scan for new mux devices."""
    global mux
    mux.scan()                                                  # Scan devices on the mux pins

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
    input.getValues()

def outputScan():
    """Scan for new output devices."""
    global outputList, output
    output.scan()                                               # Scan devices on the output pins
    outputListPrevious = outputList                             # Keep copy of last output devices
    outputList = []                                             # Reset list of connected Output list
    outputListRegister = []                                     # List of new devices that need to be registered
    outputListDeregister = []                                   # List of new devices that need to be deregistered

    for el1 in output.connectedDevices:                         # Check for connected and new devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], outputListPrevious)) > 0):
            outputList.append(el1)                              # Add to connected list
        else:                                                   # Device is not yet registered
            outputListRegister.append(el1)                      # Add to register list
            outputList.append(el1)                              # Add connected list

    for el1 in outputListPrevious:                              # Check for disconnected devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], outputList)) == 0):
            outputListDeregister.append(el1)                    # Add to deregister list

    return outputListRegister, outputListDeregister

def outputUpdate():
    """Update the output devices."""
    output.getValues()

def pwmScan():
    """Scan for new pwm devices."""
    global pwmList, pwm
    pwm.scan()                                                  # Scan devices on the pwm pins
    pwmListPrevious = pwmList                                   # Keep copy of last pwm devices
    pwmList = []                                                # Reset list of connected PWM list
    pwmListRegister = []                                        # List of new devices that need to be registered
    pwmListDeregister = []                                      # List of new devices that need to be deregistered

    for el1 in pwm.connectedDevices:                            # Check for connected and new devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], pwmListPrevious)) > 0):
            pwmList.append(el1)                                 # Add to connected list
        else:                                                   # Device is not yet registered
            pwmListRegister.append(el1)                         # Add to register list
            pwmList.append(el1)                                 # Add connected list

    for el1 in pwmListPrevious:                                 # Check for disconnected devices
        if (len(filter(lambda el2: el2['name'] == el1['name'], pwmList)) == 0):
            pwmListDeregister.append(el1)                       # Add to deregister list

    return pwmListRegister, pwmListDeregister

def pwmUpdate():
    """Update the pwm devices."""
    pwm.getValues()

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
    adc.getValues()


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
    i2c.getValues()

def scanThread():
    """Thread dedicated to scan for new devices."""
    global c, scanForDevices, scanDuration
    while True:                                                 # Enter the infinite loop
        if not scanForDevices:                                  # Check for scanning
            scanDuration = 0                                    # No scanning
            time.sleep(SCAN_PERIODE)
            continue
        startTime = time.time()                                 # Save start time of update cycle

        messagesSend = []                                       # List of messages to send

        muxScan()                                               # Scan for muxes
        inputListRegister, inputListDeregister = inputScan()    # Get the Input devices and events
        outputListRegister, outputListDeregister = outputScan() # Get the Output devices and events
        pwmListRegister, pwmListDeregister = pwmScan()          # Get the PWM devices and events
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
                                            'mode': device['mode'],
                                            'flags': device['flags'],
                                            'frequency': device['frequency'],
                                            'dutyFrequency': device['dutyFrequency']}))

        for device in outputListDeregister:                     # Create output device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['name']}))



        for device in outputListRegister:                       # Create output device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['name'],
                                            'dir': device['dir'],
                                            'dim': device['dim'],
                                            'about': device['about'],
                                            'settings': device['settings'],
                                            'mode': device['mode'],
                                            'flags': device['flags'],
                                            'frequency': device['frequency'],
                                            'dutyFrequency': device['dutyFrequency']}))

        for device in pwmListDeregister:                        # Create pwm device deregister message
            messagesSend.append(json.dumps({'type': 'Deregister',
                                            'name': device['name']}))



        for device in pwmListRegister:                          # Create pwm device register message
            messagesSend.append(json.dumps({'type': 'Register',
                                            'name': device['name'],
                                            'dir': device['dir'],
                                            'dim': device['dim'],
                                            'about': device['about'],
                                            'settings': device['settings'],
                                            'mode': device['mode'],
                                            'flags': device['flags'],
                                            'frequency': device['frequency'],
                                            'dutyFrequency': device['dutyFrequency']}))

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
                                            'mode': device['mode'],
                                            'flags': device['flags'],
                                            'frequency': device['frequency'],
                                            'dutyFrequency': device['dutyFrequency']}))

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
                                            'flags': device['flags'],
                                            'frequency': device['frequency'],
                                            'dutyFrequency': device['dutyFrequency']}))

        if c.getState() == 'Connected':
            c.sendMessages(messagesSend)                        # Send the messages
        if EVENT_LOG:                                           # Check for event log
            eventLog(messagesSend)                              # Call event log function

        endTime = time.time()                                   # Save end time of update cycle
        scanDuration = endTime - startTime                      # Calculate time used to scan for devices

        if (scanDuration < SCAN_PERIODE):
            time.sleep(SCAN_PERIODE - scanDuration)             # Sleep until next scan period

        if exit:                                                # Exit
            break;


def updateThread():
    """Thread dedicated to get updated values of the devices."""
    global c, scanForDevices, updateDuration, UPDATE_PERIODE
    while True:                                                 # Enter the infinite loop
        startTime = time.time()                                 # Save start time of update cycle
        messagesSend = []                                       # List of messages to send
        messagesRecv = c.getMessages()                          # Get new messages

        inputUpdate()                                           # Update input devices
        outputUpdate()                                          # Update output devices
        pwmUpdate()                                             # Update PWM devices
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
                                                    'mode': device['mode'],
                                                    'flags': device['flags'],
                                                    'frequency': device['frequency'],
                                                    'dutyFrequency': device['dutyFrequency']}))
                for device in outputList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode'],
                                                    'flags': device['flags'],
                                                    'frequency': device['frequency'],
                                                    'dutyFrequency': device['dutyFrequency']}))
                for device in pwmList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode'],
                                                    'flags': device['flags'],
                                                    'frequency': device['frequency'],
                                                    'dutyFrequency': device['dutyFrequency']}))
                for device in adcList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode'],
                                                    'flags': device['flags'],
                                                    'frequency': device['frequency'],
                                                    'dutyFrequency': device['dutyFrequency']}))
                for device in i2cList:
                    messagesSend.append(json.dumps({'type': 'Register',
                                                    'name': device['name'],
                                                    'dir': device['dir'],
                                                    'dim': device['dim'],
                                                    'about': device['about'],
                                                    'settings': device['settings'],
                                                    'mode': device['mode'],
                                                    'flags': device['flags'],
                                                    'frequency': device['frequency'],
                                                    'dutyFrequency': device['dutyFrequency']}))
            if message['type'] == 'Set':                        # Get set message for a device and check for devices
                output.setValue(message['name'], message['dim'], message['value'])
                pwm.setValue(message['name'], message['dim'], message['value'])
                i2c.setValue(message['name'], message['dim'], message['value'])

            if message['type'] == 'Settings':                   # Change settings for a device
                input.settings(message)
                output.settings(message)
                pwm.settings(message)
                adc.settings(message)
                i2c.settings(message)

            if message['type'] == 'Scan':                       # Change scan for a device
                scanForDevices = message['value']

            if message['type'] == 'Ping':                       # Ping back
                messagesSend.append(json.dumps({'type': 'Ping','name':''}))

        dataMessage = {'type': 'D', 'data': []}                 # Create data message
        for device in inputList:                                # Create input device data message
            dataMessage['data'].append({'name': device['name'], 'values': device['vals'], 'cycle': device['cycle']})
        for device in outputList:                               # Create output device data message
            dataMessage['data'].append({'name': device['name'], 'values': device['vals'], 'cycle': device['cycle']})
        for device in pwmList:                                  # Create pwm device data message
            dataMessage['data'].append({'name': device['name'], 'values': device['vals'], 'cycle': device['cycle']})
        for device in adcList:                                  # Create adc device data message
            dataMessage['data'].append({'name': device['name'], 'values': device['vals'], 'cycle': device['cycle']})
        for device in i2cList:                                  # Create i2c device data message
            dataMessage['data'].append({'name': device['name'], 'values': device['vals'], 'cycle': device['cycle']})

        if len(dataMessage['data']) > 0:
            messagesSend.append(json.dumps(dataMessage))         # Send data message

        if c.getState() == 'Connected':
            c.sendMessages(messagesSend)                        # Send the messages
        if DATA_LOG:                                            # Check for data log
            dataLog(messagesSend)                               # Call data log function
        endTime = time.time()                                   # Save end time of update cycle
        updateDuration = endTime - startTime                    # Calculate time used to update values

        if (updateDuration < UPDATE_PERIODE):
            time.sleep(UPDATE_PERIODE - updateDuration)         # Sleep until next update period

        if exit:                                                # Exit
            break;


def livePrint():
    """Handle all the prints to the console."""
    global connectionState                                      # Uses the message global variables
    stringToPrint = ""                                          # String to print
    stringToPrint += colored("****************************************************************\n", 'green')
    stringToPrint += colored("* Hardware:    {}                  *\n".format(BOARD), 'green') # Display hardware information
    stringToPrint += colored("* Software:    {} *\n".format(SOFTWARE), 'green') # Display software information
    stringToPrint += colored("* Layout:      {}                                       *\n".format(Config.LAYOUT), 'green') # Display layout information
    stringToPrint += colored("****************************************************************\n", 'green')
    stringToPrint += "\n"
    stringToPrint += "Connection:  {}".format(colored(connectionState, attrs=['bold', 'dark'])) # Print connection status
    stringToPrint += "\n"
    stringToPrint += "Update cycle:  "                          # Print update cycle time
    stringToPrint += colored("{:.2f} ms / {:.2f} ms\n".format(updateDuration * 1000, UPDATE_PERIODE * 1000), 'grey') # Print update cycle time
    if scanForDevices:
        stringToPrint += "Scan   cycle:  "                      # Print scan cycle time
        stringToPrint += colored("{:.2f} ms / {:.2f} ms\n".format(scanDuration * 1000, SCAN_PERIODE * 1000), 'grey') # Print scan cycle time
    else:
        stringToPrint += "Scan   cycle: -\n"                    # Print scan disabled

    # Print Input informations:
    stringToPrint += "\nConnected Inputs: {}\n".format(colored(len(inputList), attrs=['bold', 'dark']))
    for el in inputList:                                        # Go through all connected Input devices
        if ('mux' in el and 'pin' in el and 'name' in el and 'about' in el and 'val' in el and 'cycle' in el):
            if el['mux'] != -1:                                 # Muxed pin
                stringToPrint += '({}:{}) {}: {} / {} | {:.2f} ms\n'.format(str(el['pin']), str(el['mux']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)
            else:                                               # Unmuxed pin
                stringToPrint += '({}) {}: {} / {} | {:.2f} ms\n'.format(str(el['pin']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)

    # Print Output informations:
    stringToPrint += "\nConnected Outputs: {}\n".format(colored(len(outputList), attrs=['bold', 'dark']))
    for el in outputList:                                       # Go through all connected Output devices
        if ('pin' in el and 'name' in el and 'about' in el and 'val' in el and 'cycle' in el):
            stringToPrint += '({}) {}: {} / {} | {:.2f} ms\n'.format(str(el['pin']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)

    # Print PWM informations:
    stringToPrint += "\nConnected PWMs: {}\n".format(colored(len(pwmList), attrs=['bold', 'dark']))
    for el in pwmList:                                          # Go through all connected PWM devices
        if ('pin' in el and 'name' in el and 'about' in el and 'val' in el and 'cycle' in el):
            stringToPrint += '({}) {}: {} / {} | {:.2f} ms\n'.format(str(el['pin']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)

    # Print ADC informations:
    stringToPrint += "\nConnected ADCs: {}\n".format(colored(len(adcList), attrs=['bold', 'dark']))
    for el in adcList:                                          # Go through all connected ADC devices
        if ('mux' in el and 'pin' in el and 'name' in el and 'about' in el and 'val' in el and 'cycle' in el):
            if el['mux'] != -1:                                 # Muxed pin
                stringToPrint += '({}:{}) {}: {} / {} | {:.2f} ms\n'.format(str(el['pin']), str(el['mux']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)
            else:                                               # Unmuxed pin
                stringToPrint += '({}) {}: {} / {} | {:.2f} ms\n'.format(str(el['pin']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)

    # Print I2C informations:
    stringToPrint += "\nConnected I2Cs: {}\n".format(colored(len(i2cList), attrs=['bold', 'dark']))
    for el in i2cList:                                        # Go through all connected I2C devices
        if ('bus' in el and 'name' in el and 'about' in el and 'val' in el and 'cycle' in el):
            stringToPrint += '(BUS {}) {}: {} / {} | {:.2f} ms\n'.format(str(el['bus']), el['name'], colored(str(el['about']['dimMap']), 'blue'), colored(str(el['val']), 'blue'), el['cycle'] * 1000.)

    stringToPrint += "\n\nManually break to exit!\n"            # Print exit condition
    stringToPrint += ">> Ctrl-C\n"                              # Print exit shortcut
    os.system('clear')                                          # Clear console output
    print(stringToPrint)                                        # Print live data

def diagLog():
    """Log diagnostics of the firmware."""
    with open("../Logs/diag.log", "a") as f:                    # Open diag file
        f.write("System,Scan,{}\n".format(scanDuration))        # Log scan duration
        f.write("System,Update,{}\n".format(updateDuration))    # Log update duration
        for el in inputList:                                    # Loop input device
            if ('name' in el and 'cycle' in el):                # Check for values
                f.write("Device,{},{}\n".format(el['name'], el['cycle'] * 1000.)) # Log device loop duration
        for el in outputList:                                   # Loop output device
            if ('name' in el and 'cycle' in el):                # Check for values
                f.write("Device,{},{}\n".format(el['name'], el['cycle'] * 1000.)) # Log device loop duration
        for el in pwmList:                                      # Loop pwm device
            if ('name' in el and 'cycle' in el):                # Check for values
                f.write("Device,{},{}\n".format(el['name'], el['cycle'] * 1000.)) # Log device loop duration
        for el in adcList:                                      # Loop adc device
            if ('name' in el and 'cycle' in el):                # Check for values
                f.write("Device,{},{}\n".format(el['name'], el['cycle'] * 1000.)) # Log device loop duration
        for el in i2cList:                                      # Loop i2c device
            if ('name' in el and 'cycle' in el):                # Check for values
                f.write("Device,{},{}\n".format(el['name'], el['cycle'] * 1000.)) # Log device loop duration




def dataLog(messages):
    """Log data streamed by the firmware."""
    with open("../Logs/data.log", "a") as f:                    # Open log file
        for message in messages:                                # Loop all messages
            f.write(message)                                    # Write message
            f.write('\n')                                       # Next line

def eventLog(messages):
    """Log events streamed by the firmware."""
    with open("../Logs/event.log", "a") as f:                   # Open log file
        for message in messages:                                # Loop all messages
            f.write(message)                                    # Write message
            f.write('\n')                                       # Next line

def main():
    """Infinite loop function, reads all devices and manages the connection."""
    global connectionState, c, exit, LIVE_PRINT, DIAG_LOG, DATA_LOG, EVENT_LOG

    if ('l' in sys.argv):                                       # Check live plot parameter
        LIVE_PRINT = True
    if ('d' in sys.argv):                                       # Check diag log parameter
        DIAG_LOG = True
        with open("../Logs/diag.log", "w"):                     # Clear diag file
            pass                                                # Write message
    if ('m' in sys.argv):                                       # Check data log parameter
        DATA_LOG = True
        with open("../Logs/data.log", "w"):                     # Clear log file
            pass                                                # Write message
    if ('e' in sys.argv):                                       # Check event log parameter
        EVENT_LOG = True
        with open("../Logs/event.log", "w"):                    # Clear log file
            pass                                                # Write message

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
        if c.getState() is 'Connected':
        #     sendMessages = [json.dumps({'type': 'Ping','name':''})]
        #     c.sendMessages(sendMessages)
            sendMessages = [json.dumps({'type': 'CycleDuration','name':'', 'values': {'update': updateDuration, 'scan': scanDuration}})]
            c.sendMessages(sendMessages)

        if LIVE_PRINT:                                          # Check for live plotting
            livePrint()                                         # Call print function
        if DIAG_LOG:                                            # Check for diag log
            diagLog()                                           # Call diag function
        time.sleep(PRINT_PERIODE)                               # Sleep until next print period

    # If we reach this -> something happened. Close communication channel
    exit = True
    c.stopAndFreeResources()

# Just call the main function.
if ('p' in sys.argv):                                           # Check profile parameter
    with open("../Logs/stats.log", "w"):                        # Clear log file
        pass                                                    # Write message
    cProfile.run('main()', '../Logs/stats.log')
else:
    main()
