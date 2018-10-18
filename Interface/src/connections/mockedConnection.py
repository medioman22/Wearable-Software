# -*- coding: utf-8 -*-
"""
Representation of a mocked connection to the physical board

A mocked connection to a mocked board
"""

# import math
import random
import time
import datetime
# import time
import json
from connections.connection import Connection
from utils import Utils

# Global variables
utils = Utils()



class MockedConnection(Connection):
    """Representation of a mocked connection to the mocked board."""

    def __init__(self):
        """Configure the mocked connection."""
        super().__init__('Mocked Connection')

    def __del__(self):
        """Class destructor. This is needed in order to stop any background threads."""
        pass

    def __enter__(self):
        """Needed for usage like: 'with Connection() as c:'."""
        return self

    def __exit__(self):
        """Needed for usage like: 'with Connection() as c:'."""
        pass

    def connect(self):
        """Try to establish the connection."""
        self._status = 'Connected'

    def disconnect(self):
        """Close the connection."""
        self._status = 'Disconnected'

        # Reset data generating functions
        global devicesRegistered
        devicesRegistered = False

    def getMessages(self):
        """Get a list of all the messages that have been recieved since the last call of this function."""
        return defaultBehaviour()

    def sendMessages(self, messages):
        """Send a list of messages."""
        # Sending messages is not implemented in the mocked connection

    def getState(self):
        """Get the connection state."""
        return self._state


################################################### Mock data generation



devicesRegistered = False
tempDeviceRegistered = False
delta = datetime.datetime.now()
def defaultBehaviour():
    """Register some devices and then feed values."""
    # Add devices
    global devicesRegistered, tempDeviceRegistered
    if (devicesRegistered == False):
        registerDeviceMessages = []
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 01 (rand 0-1)',          'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 02 (rand 0-100)',        'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 03 (rand 0-1 x3)',       'dir': 'in', 'dim': 3, 'about': {'dimMap': ['1','2', '3']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 04 (const)',             'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 05 (lin 0-10)',          'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 06 (rect 1,0)',          'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 07 (tri 0-1)',           'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 08 (exp 0-1)',           'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 09 (sin 0,±1)',          'dir': 'in', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 10 (all)',               'dir': 'in', 'dim': 6, 'about': {'dimMap': ['1', '2', '3', '4', '5', '6']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 11',                     'dir': 'out', 'dim': 1, 'about': {'dimMap': ['1']}})
        registerDeviceMessages.append({ 'type': 'Register', 'name': 'Mocked Device 12',                     'dir': 'out', 'dim': 3, 'about': {'dimMap': ['1']}})

        devicesRegistered = True
        # Simulate serialized connection
        return list(map(lambda x: json.dumps(x), registerDeviceMessages))
    # Report values
    else:
        dataMessages = []
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 01 (rand 0-1)', 'values': [random.random()], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 02 (rand 0-100)', 'values': [random.randint(1,101)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 03 (rand 0-1 x3)', 'values': [random.uniform(1,11), random.uniform(11,21), random.uniform(21,31)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 04 (const)', 'values': [utils.constantFunction({'a': 1}, delta)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 05 (lin 0-10)', 'values': [utils.linearFunction({'a': 0.2, 'b': 0, 'lower': -1, 'upper': 1}, delta)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 06 (rect 1,0)', 'values': [utils.rectFunction({'a': 5, 'b': 0, 'lower': 0, 'upper': 1}, delta)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 07 (tri 0-1)', 'values': [utils.triFunction({'a': 5, 'b': 0, 'lower': 0, 'upper': 1}, delta)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 08 (exp 0-1)', 'values': [utils.expFunction({'a': 0.2, 'b': 1, 'lower': 0, 'upper': 1}, delta)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 09 (sin 0,±1)', 'values': [utils.sinFunction({'a': 5, 'b': 0, 'lower': -1, 'upper': 1}, delta)], 'timestamp': time.time()})
        dataMessages.append({'type': 'Data', 'name': 'Mocked Device 10 (all)', 'values': [
            utils.constantFunction({'a': 1}, delta),
            utils.linearFunction({'a': 0.2, 'b': 0, 'lower': -1, 'upper': 1}, delta),
            utils.rectFunction({'a': 5, 'b': 0, 'lower': 0, 'upper': 1}, delta),
            utils.triFunction({'a': 5, 'b': 0, 'lower': 0, 'upper': 1}, delta),
            utils.expFunction({'a': 0.2, 'b': 1, 'lower': 0, 'upper': 1}, delta),
            utils.sinFunction({'a': 5, 'b': 0, 'lower': -1, 'upper': 1}, delta)], 'timestamp': time.time()})

        # TODO: Adapt to new serialized message format
        # De/Register temp device
        # if (math.floor(time.time() / 5 % 2) == 0 and tempDeviceRegistered):
        #     dataMessages.append(Message('Deregister','Mocked Device Temp'))
        #     tempDeviceRegistered = False
        # elif (math.floor(time.time() / 5 % 2) == 1 and not tempDeviceRegistered):
        #     dataMessages.append(Message('Register','Mocked Device Temp', {'dir': 'in', 'dim': 1}))
        #     tempDeviceRegistered = True
        #
        # if (tempDeviceRegistered):
        #     dataMessages.append(Message('Data','Mocked Device Temp', [random.random()]))


        # Simulate serialized connection
        return list(map(lambda x: json.dumps(x), dataMessages))
