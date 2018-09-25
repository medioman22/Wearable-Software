#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtCore import (pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QDialog, QPushButton, QLineEdit, QVBoxLayout, QGroupBox)

logging.basicConfig(level=logging.DEBUG)

class ConnectionDialog(QDialog):
    """
    Connection Dialog.

    A dialog to enter the IP of the board
    """

    # Signal for new settings values
    settingsChanged = pyqtSignal(str, str)

    def __init__(self):
        """Initialize the connection dialog."""
        super().__init__()

        # Initialize the dialog UI
        self.setModal(True)
        self.initUI()


    def initUI(self):
        """Initialize the ui of the connection dialog."""
        # Field for the IP address
        ipLine = QLineEdit()
        ipLine.setPlaceholderText('IP')
        self._ipLine = ipLine
        portLine = QLineEdit()
        portLine.setPlaceholderText('PORT')
        self._portLine = portLine

        # Confirmation button
        okButton = QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self._changeSettingsListener)

        # Cancel button
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)

        # Layout for connection settings fields
        connectionSettingsLayout = QVBoxLayout()
        connectionSettingsLayout.addWidget(ipLine)
        connectionSettingsLayout.addWidget(portLine)

        # Group informations
        groupLayout = QGroupBox('Connection Settings')
        groupLayout.setLayout(connectionSettingsLayout)

        # Dialog layout
        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(groupLayout)
        bodyLayout.addWidget(cancelButton)
        bodyLayout.addWidget(okButton)

        self.setLayout(bodyLayout)

    def setValues(self, ip, port):
        """
        Set the values.

        Values: ip, port, …
        """
        self._ipLine.setText(ip)
        self._portLine.setText(port)


    @pyqtSlot()
    def _changeSettingsListener(self):
        """Update connection settings."""
        self.settingsChanged.emit(self._ipLine.text(), self._portLine.text())
        self.close()
