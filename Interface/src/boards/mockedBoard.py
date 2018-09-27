# -*- coding: utf-8 -*-
"""A representation of the mocked physical board connected."""

from boards.board import Board

class MockedBoard(Board):
    """Representation of a mocked physical board."""

    def __init__(self):
        """Initialize the mocked board."""
        super().__init__('Mocked Board', 'Mocked Connection', '0.0.0.0', '666')
