#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from PyQt5.QtCore import (Qt, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QWidget, QMessageBox, QPushButton, QAction, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QSplitter, QStackedWidget, QGridLayout, QGroupBox)
from PyQt5.QtGui import (QPixmap)

logging.basicConfig(level=logging.DEBUG)

class DeviceSettingsWidget(QWidget):
    """
    Device Settings Widget.

    Default device settings
    """

    # Associated device
    _device = None

    def __init__(self, device):
        """Initialize the device settings widget."""
        super().__init__()

        if (device == None):
            raise ValueError('device is invalid')
        else:
            self._device = device;

        # Initialize the device settings UI
        self.initUI()


    def initUI(self):
        """Initialize the ui of the device settings widget."""
        # Layout for information of device
        informationLayout = QHBoxLayout()
        informationLayout.addWidget(QLabel('Direction: <i>{}</i>'.format(self._device.dir())))
        informationLayout.addWidget(QLabel('Dimension: <i>{}</i>'.format(self._device.dim())))

        # Group informations
        groupInformationLayout = QGroupBox(self._device.name())
        groupInformationLayout.setLayout(informationLayout)

        # Label for device data
        dataLabel = QLabel('Data')
        self._dataLabel = dataLabel

        # Layout for device data
        dataLayout = QHBoxLayout()
        dataLayout.addWidget(dataLabel)

        # Group data
        groupDataLayout = QGroupBox("Data [{}]".format(self._device.dim()))
        groupDataLayout.setLayout(dataLayout)

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addWidget(groupInformationLayout,        0, 0, Qt.AlignLeft)
        bodyGridLayout.addWidget(groupDataLayout,               1, 0, Qt.AlignLeft | Qt.AlignTop)

        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 10)

        self.setLayout(bodyGridLayout)

    def updateData(self):
        """Update data of a device."""
        self._dataLabel.setText("<b>{}</b>".format("<br>".join('{:.4f}'.format(el) for el in self._device.data())))
        #self._dataLabel.setText("Data <i>{:f}</i>".format(self._device.data()))

    def device(self):
        """Return the device."""
        return self._device
