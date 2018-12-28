# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
LOOP TEMPLATE.
Sample loop script to be embedded into the Firmware while being tested externally. Use this script as a base for further applications.
"""

import time                                                     # Timing package
import json                                                     # Serializing class. All objects sent are serialized

from api import APIConnection                                   # Import API

LOWER_THRESHOLD = 0.1
UPPER_THRESHOLD = 0.4

class Loop():
    """API connection."""

    # The api
    _api = None

    def __init__(self, api):
        """Initialization."""
        self._api = api

    def start(self):
        """Start the loop."""
        ###################################
        # Do some initialization          #
        ###################################

        enabled = True;
        outputs = [0, 0, 0, 0]
        lastOutputs = [0, 0, 0, 0]


        while (1):
            # Get the messages
            messagesIn = self._api.getMessages()
            messagesOut = []

            # Loop all incoming messages
            for messageString in messagesIn:
                # Unserialize the message
                message = json.loads(messageString)

                # Check for type
                if message['type'] == 'D':
                    for el in message['data']:                      # Loop data
                        ###################################
                        if el['name'] == 'INPUT_BASIC@Input[P8_31]':
                            if len(el['values']) > 0:
                                if enabled and (el['values'][-1][1][0]) == 0:
                                    enabled = False;
                                    messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_35]', 'dim': 0, 'value': 0}))
                                    messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_37]', 'dim': 0, 'value': 0}))
                                    messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_39]', 'dim': 0, 'value': 0}))
                                    messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_41]', 'dim': 0, 'value': 0}))
                                elif not enabled and (el['values'][-1][1][0]) == 1:
                                    enabled = True;

                        if enabled:
                            if el['name'] == 'ADC_BASIC@ADC[P9_40]':
                                if len(el['values']) > 0:
                                    if el['values'][-1][1][0] < LOWER_THRESHOLD:
                                        outputs = [1, outputs[1], outputs[2], 0]
                                    elif el['values'][-1][1][0] > UPPER_THRESHOLD:
                                        outputs = [0, outputs[1], outputs[2], 1]
                                    else:
                                        outputs = [0, outputs[1], outputs[2], 0]

                            if el['name'] == 'INPUT_BASIC@Input[P8_27]':
                                if len(el['values']) > 0:
                                    if el['values'][-1][1][0] == 1:
                                        outputs = [outputs[0], 1, 1, outputs[3]]
                                    else:
                                        outputs = [outputs[0], 0, 0, outputs[3]]

                        if outputs[0] != lastOutputs[0]:
                            messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_35]', 'dim': 0, 'value': outputs[0]}))
                        if outputs[1] != lastOutputs[1]:
                            messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_37]', 'dim': 0, 'value': outputs[1]}))
                        if outputs[2] != lastOutputs[2]:
                            messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_39]', 'dim': 0, 'value': outputs[2]}))
                        if outputs[3] != lastOutputs[3]:
                            messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P8_41]', 'dim': 0, 'value': outputs[3]}))

                        lastOutputs = outputs;
                        print(outputs)
                        ###################################
                break;

            # Send the messages
            self._api.sendMessages(messagesOut)

            # Wait for 0.01s
            time.sleep(0.01)





# Start the script when called from terminal else ignore it
if __name__ == '__main__':
    # Create a connection
    a = APIConnection()

    # Connect to the api
    a.connect()

    # Initialize loop
    print('Initialize Loop')
    loop = Loop(a)

    # Start loop
    print('Start Loop …')
    loop.start()
