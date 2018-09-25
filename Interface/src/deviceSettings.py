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
        informationGridLayout = QHBoxLayout()
        informationGridLayout.addWidget(QLabel('Direction: <i>{}</i>'.format(self._device.dir())))
        informationGridLayout.addWidget(QLabel('Dimension: <i>{}</i>'.format(self._device.dim())))


        # Group informations
        groupLayout = QGroupBox(self._device.name())
        groupLayout.setLayout(informationGridLayout)

        # Grid for the device settings layout
        bodyGridLayout = QGridLayout()
        bodyGridLayout.addWidget(groupLayout,                   0, 0, Qt.AlignLeft)
        bodyGridLayout.addWidget(QLabel('Values'),              1, 0, Qt.AlignLeft)

        bodyGridLayout.setRowStretch(0, 1)
        bodyGridLayout.setRowStretch(1, 10)

        self.setLayout(bodyGridLayout)


    def device(self):
        """Return the device."""
        return self._device
