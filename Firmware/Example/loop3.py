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
                        if el['name'] == 'BNO055@I2C[40,2]':
                            if len(el['values']) > 0:
                                v = round(min(10, abs(el['values'][-1][1][2])) / 10 * 8 + 18); # Map to servo values
                                print(v)
                                messagesOut.append(json.dumps({'type': 'Settings', 'name': 'PCA9685@I2C[64,2]', 'dutyFrequency': '100 Hz'}))
                                messagesOut.append(json.dumps({'type': 'Set', 'name': 'PCA9685@I2C[64,2]', 'dim': 0, 'value': v}))
                        ###################################
                break;
            # Send the messages
            self._api.sendMessages(messagesOut)

            # Wait for 0.1s
            time.sleep(0.1)





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
