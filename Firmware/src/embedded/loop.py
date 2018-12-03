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

class Loop():
    """API connection."""

    # The api
    _api = None

    def __init__(self, api):
        """Initialization."""
        self._api = api

    def start(self):
        """Start the loop."""
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
                        # Basic Feedback: INPUT ~> OUTPUT #
                        if el['name'] == 'INPUT_BASIC@Input[P8_27]': # Check for device
                            if len(el['values']) > 0:               # Check if data is avail
                                messagesOut.append(json.dumps({'type': 'Set', 'name': 'OUTPUT_BASIC@Output[P9_23]', 'dim': 0, 'value': el['values'][-1][1][0]}))
                        ###################################

                        ###################################
                        # Basic Feedback: ADC ~> PWM      #
                        if el['name'] == 'ADC_BASIC@ADC[P9_39]':    # Check for device
                            if len(el['values']) > 0:               # Check if data is avail
                                v = el['values'][-1][1][0] * 100    # [0,1] -> [0,100]
                                messagesOut.append(json.dumps({'type': 'Set', 'name': 'PWM_BASIC@PWM[P9_16]', 'dim': 0, 'value': v}))
                        ###################################

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
