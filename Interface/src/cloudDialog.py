# -*- coding: utf-8 -*-
# Author: Paul Moineville
# Date: November 2020

import logging                                              # Logging package
from PyQt5.QtCore import pyqtSignal, pyqtSlot               # Core functionality from Qt
                            
from PyQt5.QtWidgets import (   QDialog,                    # Widget objects for GUI from Qt
                                QLabel,
                                QPushButton,
                                QLineEdit,
                                QVBoxLayout,
                                QGroupBox,
                                QMessageBox)

from influxdb_client import InfluxDBClient, WriteOptions
from influxdb_client.client.write_api import WriteType
import keyring

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging
   

class CloudDialog(QDialog):
    """
    Cloud Dialog to enter url, org, bucket and token
    """
    # Signal to start streaming 
    startStream = pyqtSignal()

    # InfluxDB client
    _client = None
    # API for writing to InfluxDB
    _write_api = None  
    # URL
    _url = None
    # Organization
    _org = None
    # Bucket
    _bucket = None
    # Token
    _token = None 
    # Logger module
    _logger = None

    def __init__(self):
        """Initialize the cloud dialog."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('CloudDialog')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        self._logger.info("Cloud dialog initializing …")

        # Initialize credentials if file exists
        self.read_creds_file()

        # Initialize the dialog UI
        self.setWindowTitle('Cloud Settings')
        self.resize(370, 240)
        self.setModal(True)
        self.initUI()
        self._logger.info("Cloud dialog initialized")


    def initUI(self):
        """Initialize the ui of the cloud dialog."""
        
        # Link to InfluxDB cloud sign up/login
        link = QLabel('Sign Up / Login: <a href="https://cloud2.influxdata.com/signup">cloud2.influxdata.com</a>\n')
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
        cloudSettingsLayout.addWidget(QLabel('\nURL'))
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
    
    def read_creds_file(self):
        """Initialize cloud credentials if file exists"""
        try: 
            [self._url, self._org, self._bucket, self._token] = keyring.get_password("daqlink", "cloud").split(';')
        except:
            pass

    def delete_client(self):
        """Stop cloud streaming"""
        self._client.__del__()          # Delete client
        self._client = None
        self._logger.debug("Stream off")

    # def create_write_api(self):
    #     """Create a Write API instance"""
    #     self._client = InfluxDBClient(url=self._url, token=self._token)        # Create client
    #     self._write_api = self._client.write_api(write_options=WriteOptions(write_type=WriteType.asynchronous, flush_interval=1000))    # Create writing API
    #     self._logger.debug("Write API")    

    def save_creds_dialog(self):
        """Ask to save credentials and save data if answer is yes"""
        reply = QMessageBox.question(self, 'Message',                           # Message dialog
                "Do you want to save your cloud settings?", QMessageBox.Yes |
                QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:                                            # Save credentials
            creds = ';'.join([self._url, self._org, self._bucket, self._token])
            if sum([';' in c for c in creds]) != 3:
                self.error_dialog.showMessage('Cannot save settings: invalid ; caracter')
            else:
                keyring.set_password("daqlink", "cloud", creds)
    
    def valid_creds(self):
        self._client = InfluxDBClient(url=self._urlLine.text(), token=self._tokenLine.text(), org=self._orgLine.text())
        q = 'from(bucket:"{}") |> range(start: -1m)'.format(self._bucketLine.text())
        try:
            self._client.query_api().query(q)
            self._write_api = self._client.write_api(write_options=WriteOptions(flush_interval=1000))    # Create writing API
        except:
            self._write_api = None
            self.delete_client()

    def showCloudDialogListener(self):
        """Show cloud dialog listener with last updated values."""
        self._urlLine.setText(self._url)                                # Set last credentials to dialog lines
        self._orgLine.setText(self._org)
        self._bucketLine.setText(self._bucket)
        self._tokenLine.setText(self._token)
        self.show()                                                     # Show cloud dialog
        self._logger.debug("Set values")
        self._logger.info("Show cloud settings dialog")

    @pyqtSlot()
    def _changeSettingsListener(self):
        """Save updated values, close and start streaming."""
        self.valid_creds() 
        if self._write_api == None:
            QMessageBox().warning(self, 'Information', "Could not connect to cloud")
            self._logger.debug("Wrong credentials")
        else:
            self.close()
            self.startStream.emit()
            if self._url != self._urlLine.text() or self._org != self._orgLine.text() or \
            self._bucket != self._bucketLine.text() or self._token != self._tokenLine.text():
                self._url = self._urlLine.text()                            # Update credentials
                self._org = self._orgLine.text()
                self._bucket = self._bucketLine.text()
                self._token = self._tokenLine.text()
                self.save_creds_dialog()                                    # Save new credentials to file ? 
            self._logger.debug("Save values and stream on")
            self._logger.info("Close")
