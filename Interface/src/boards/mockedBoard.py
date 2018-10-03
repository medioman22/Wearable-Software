# -*- coding: utf-8 -*-
"""A representation of the mocked physical board connected."""

import json
from boards.board import Board
from connections.connection import Message

class MockedBoard(Board):
    """Representation of a mocked physical board."""

    def __init__(self):
        """Initialize the mocked board."""
        super().__init__('Mocked Board', 'Mocked Connection', '0.0.0.0', '666')

    def serializeMessage(self, messageObject):
        """Return serialized message as string."""
        Message('Register','Mocked Device 02 (rand 0-100)', {'dir': 'in', 'dim': 1})
        d = messageObject.data.copy()
        d['type'] = messageObject.type
        d['name'] = messageObject.name

        return json.dumps(d)

    def unserializeMessage(self, messageString):
        """Return parsed message as dict."""
        d = json.loads(messageString)
        return Message(d['type'], d['name'], d)
