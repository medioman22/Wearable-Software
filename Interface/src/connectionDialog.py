#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtCore import (pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QDialog, QPushButton, QLineEdit, QVBoxLayout)

logging.basicConfig(level=logging.DEBUG)

class ConnectionDialog(QDialog):
    """
    Connection Dialog.

    A dialog to enter the IP of the board
    """

    settingsChanged = pyqtSignal(str)

    def __init__(self):
        """Initialize the connection dialog."""
        super().__init__()

        self.setModal(True)
        self.initUI()


    def initUI(self):
        """Initialize the ui of the connection dialog."""
        ipLine = QLineEdit()
        ipLine.setPlaceholderText('IP')
        self._ipLine = ipLine
        okButton = QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self._changeSettingsListener)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)


        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(ipLine)
        bodyLayout.addWidget(cancelButton)
        bodyLayout.addWidget(okButton)

        self.setLayout(bodyLayout)

    def setValues(self, ip):
        """
        Set the values.

        Values: ip, …
        """
        self._ipLine.setText(ip)


    @pyqtSlot()
    def _changeSettingsListener(self):
        """Update connection settings."""
        self.settingsChanged.emit(self._ipLine.text())
        self.close()
