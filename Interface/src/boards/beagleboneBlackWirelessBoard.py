# -*- coding: utf-8 -*-
"""A representation of the physical Beaglebone Black Wireless board connected."""

from boards.board import Board

class BeagleboneBlackWirelessBoard(Board):
    """Representation of a physical Beaglebone Black Wireless board board."""

    def __init__(self):
        """Initialize the Beaglebone Black Wireless board."""
        super().__init__('Beaglebone Black Wireless', 'TCP/IP', '192.168.7.2', '12345')
