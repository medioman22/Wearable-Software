# -*- coding: utf-8 -*-
"""A representation of the physical Beaglebone Green Wireless board connected."""

import json
from boards.board import Board
from connections.connection import Message

class BeagleboneGreenWirelessBoard(Board):
    """Representation of a physical Beaglebone Green Wireless board board."""

    def __init__(self):
        """Initialize the Beaglebone Green Wireless board."""
        super().__init__('Beaglebone Green Wireless', 'RoboComConnection', '192.168.7.2', '12345')

    def serializeMessage(self, messageObject):
        """Return serialized message as string."""
        global d
        d = {}
        if messageObject.data != None:
            d = messageObject.data.copy()
        d['type'] = messageObject.type
        d['name'] = messageObject.name

        return json.dumps(d)

    def unserializeMessage(self, messageString):
        """Return parsed message as dict."""
        d = json.loads(messageString)
        return Message(d['type'], d['name'], d)
