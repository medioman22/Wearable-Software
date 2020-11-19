# -*- coding: utf-8 -*-
# Author: Paul Moineville
# Date: November 2020

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
   

class CloudDialog(QDialog):
    """
    Cloud Dialog to enter url, org, bucket and token

    A dialog to enter the IP of the board
    """

    # Signal for new settings values
    settingsChanged = pyqtSignal(str, str, str, str)

    # Logger module
    _logger = None

    def __init__(self):
        """Initialize the cloud dialog."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('CloudDialog')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        self._logger.info("Cloud dialog initializing …")

        # Initialize the dialog UI
        self.setWindowTitle('Cloud Settings')
        self.resize(370, 240)
        self.setModal(True)
        self.initUI()
        self._logger.info("Cloud dialog initialized")


    def initUI(self):
        """Initialize the ui of the cloud dialog."""
        
        # Link to InfluxDB cloud sign up/login
        link = QLabel('Sign Up / Login: <a href="https://cloud2.influxdata.com/signup">cloud2.influxdata.com</a>')
        link.setOpenExternalLinks(True)
        # Field for the URL
        urlLine = QLineEdit()
        urlLine.setPlaceholderText('https://us-central1-1.gcp.cloud2.influxdata.com')
        self._urlLine = urlLine
        # Field for the org 
        orgLine = QLineEdit()
        orgLine.setPlaceholderText('Jane.Doe@exemple.com')
        self._orgLine = orgLine
        # Field for the bucket 
        bucketLine = QLineEdit()
        bucketLine.setPlaceholderText('Jane.Doe\'s Bucket')
        self._bucketLine = bucketLine
        # Field for the token 
        tokenLine = QLineEdit()
        self._tokenLine = tokenLine

        self._logger.debug("Cloud dialog UI fields created")

        # Confirmation button
        okButton = QPushButton("OK")
        okButton.setDefault(True)
        okButton.clicked.connect(self._changeSettingsListener)

        # Cancel button
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        self._logger.debug("Cloud dialog UI buttons created")
        
        # Layout for connection settings fields
        cloudSettingsLayout = QVBoxLayout()
        cloudSettingsLayout.addWidget(link)
        cloudSettingsLayout.addWidget(QLabel('URL'))
        cloudSettingsLayout.addWidget(urlLine)
        cloudSettingsLayout.addWidget(QLabel('Username'))
        cloudSettingsLayout.addWidget(orgLine)
        cloudSettingsLayout.addWidget(QLabel('Bucket'))
        cloudSettingsLayout.addWidget(bucketLine)
        cloudSettingsLayout.addWidget(QLabel('Token'))
        cloudSettingsLayout.addWidget(tokenLine)

        # Group informations
        groupLayout = QGroupBox()
        groupLayout.setLayout(cloudSettingsLayout)

        # Dialog layout
        bodyLayout = QVBoxLayout()
        bodyLayout.addWidget(groupLayout)
        bodyLayout.addWidget(cancelButton)
        bodyLayout.addWidget(okButton)

        self.setLayout(bodyLayout)
        self._logger.debug("Cloud dialog UI layout created")

    def setValues(self, url, org, bucket, token):
        """
        Set the values.

        Values: url, org, bucket, token
        """
        self._urlLine.setText(url)
        self._orgLine.setText(org)
        self._bucketLine.setText(bucket)
        self._tokenLine.setText(token)
        self._logger.debug("Set values")


    @pyqtSlot()
    def _changeSettingsListener(self):
        """Update cloud settings."""
        self.settingsChanged.emit(self._urlLine.text(), self._orgLine.text(), self._bucketLine.text(), self._tokenLine.text())
        self.close()
        self._logger.debug("Values updated")
        self._logger.info("Close")
