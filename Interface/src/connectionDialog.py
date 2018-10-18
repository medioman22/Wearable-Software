#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging                                              # Logging package
from PyQt5.QtCore import (  pyqtSignal,                     # Core functionality from Qt
                            pyqtSlot)
from PyQt5.QtWidgets import (   QDialog,                    # Widget objects for GUI from Qt
                                QLabel,
                                QPushButton,
                                QLineEdit,
                                QVBoxLayout,
                                QGroupBox)

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging

class ConnectionDialog(QDialog):
    """
    Connection Dialog.

    A dialog to enter the IP of the board
    """

    # Signal for new settings values
    settingsChanged = pyqtSignal(str, str)

    # Logger module
    _logger = None

    def __init__(self):
        """Initialize the connection dialog."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('ConnectionDialog')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        fh = logging.FileHandler('../Logs/ConnectionDialog.log', 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        self._logger.addHandler(fh)

        self._logger.info("Connection dialog initializing …")

        # Initialize the dialog UI
        self.setWindowTitle('Connection Settings')
        self.resize(360, 240)
        self.setModal(True)
        self.initUI()
        self._logger.info("Connection dialog initialized")


    def initUI(self):
        """Initialize the ui of the connection dialog."""
        # Field for the IP address
        ipLine = QLineEdit()
        ipLine.setPlaceholderText('IP')
        self._ipLine = ipLine
        portLine = QLineEdit()
        portLine.setPlaceholderText('PORT')
        self._portLine = portLine
        self._logger.debug("Connection dialog UI fields created")

        # Confirmation button
        okButton = QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self._changeSettingsListener)

        # Cancel button
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        self._logger.debug("Connection dialog UI buttons created")

        # Layout for connection settings fields
        connectionSettingsLayout = QVBoxLayout()
        connectionSettingsLayout.addWidget(QLabel('IP'))
        connectionSettingsLayout.addWidget(ipLine)
        connectionSettingsLayout.addWidget(QLabel('Port'))
        connectionSettingsLayout.addWidget(portLine)

        # Group informations
        groupLayout = QGroupBox()
        groupLayout.setLayout(connectionSettingsLayout)

        # Dialog layout
        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(groupLayout)
        bodyLayout.addWidget(cancelButton)
        bodyLayout.addWidget(okButton)

        self.setLayout(bodyLayout)
        self._logger.debug("Connection dialog UI layout created")

    def setValues(self, ip, port):
        """
        Set the values.

        Values: ip, port, …
        """
        self._ipLine.setText(ip)
        self._portLine.setText(port)
        self._logger.debug("Set values")


    @pyqtSlot()
    def _changeSettingsListener(self):
        """Update connection settings."""
        self.settingsChanged.emit(self._ipLine.text(), self._portLine.text())
        self.close()
        self._logger.debug("Values updated")
        self._logger.info("Close")
