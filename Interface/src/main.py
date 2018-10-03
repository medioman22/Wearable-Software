# -*- coding: utf-8 -*-
"""
Wearable Software Interface

This application provides an interface to the firmware loaded on the BBB

Author: Cyrill Lippuner
Last edited: September 2018
"""

import sys
import time
import logging
from PyQt5.QtCore import (pyqtSlot, QTimer)
from PyQt5.QtWidgets import (QMainWindow, QMenu, QToolTip, QMessageBox, QAction, QDesktopWidget, QFileDialog, QApplication)
from PyQt5.QtGui import (QFont, QIcon)

from utils import Utils
from interface import InterfaceWidget
from connectionDialog import ConnectionDialog
from udpBroadcast import UDPBroadcast
from boards.board import Device
from boards.mockedBoard import MockedBoard
from boards.beagleboneBlackWirelessBoard import BeagleboneBlackWirelessBoard
from connections.connection import Message
from connections.mockedConnection import MockedConnection
from connections.tcpIpConnection import TCPIPConnection

logging.basicConfig(level=logging.DEBUG)
logging.warning('Initialize …')


# Global variables
availableBoards = [MockedBoard(), BeagleboneBlackWirelessBoard()]
availableConnections = [MockedConnection(), TCPIPConnection()]
utils = Utils()

# Settings
UDP_IP = "127.0.0.1"
UDP_PORT = 12346


class MainWindow(QMainWindow):
    """The main window of the application."""

    # The selected board
    _board = None
    # The selected boards connection
    _connection = None
    # The connection ip
    _ip = None
    # The connection port
    _port = None
    # The connection time
    _connectionIteratorTimer = None
    # The UPD broadcast
    _broadcast = None

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Setup UI
        self.initUI()

        # Create connection settings dialog
        self.connectionDialog = ConnectionDialog()
        self.connectionDialog.settingsChanged.connect(self._connectionSettingsChangedListener)

        # Load default board
        self.loadBoard(availableBoards[0].name())

        # Start the timer for the connection itarator function
        self._connectionIteratorTimer = QTimer(self)
        self._connectionIteratorTimer.setSingleShot(False)
        self._connectionIteratorTimer.timeout.connect(self.connectionIteration)
        self._connectionIteratorTimer.start(50)


    def initUI(self):
        """Initialize the ui of the main window."""
        # Initialize the window
        self.setWindowTitle('Wearable Software Interface')
        self.setWindowIcon(QIcon('assets/Face.png'))
        self.resize(960, 720)
        self.center()

        # Configure the menus
        menubar = self.menuBar()
        #menubar.setNativeMenuBar(False)

        # Board menu
        boardMenu = QMenu('&Board', self)
        boardMenu.menuAction().setStatusTip("Board Menu")

        # Board selection menu
        selectMenu = QMenu('Select Board', self)
        for availableBoard in availableBoards:
            selectMenu.addAction(QAction(availableBoard.name(), self))
        selectMenu.triggered.connect(self._selectBoardListener)
        boardMenu.addMenu(selectMenu)

        # Connection option
        connectionAct = QAction('&Connect', self)
        connectionAct.setShortcut('Ctrl+Shift+C')
        connectionAct.setStatusTip('Connect')
        connectionAct.triggered.connect(self._connectListener)
        self._connectionAct = connectionAct
        boardMenu.addAction(connectionAct)

        # Edit connection option
        configureConnectionAct = QAction('&Edit Connection …', self)
        configureConnectionAct.setShortcut('Ctrl+Alt+C')
        configureConnectionAct.setStatusTip('Edit Connection Settings (IP/Port)')
        configureConnectionAct.triggered.connect(self._showConnectionDialogListener)
        boardMenu.addAction(configureConnectionAct)

        # Stream menu
        streamMenu = QMenu('Stream', self)
        streamToFileAct = QAction('&File (.CSV)', self)
        streamToFileAct.setStatusTip('Stream Incoming Data To File')
        streamToFileAct.triggered.connect(self._onStreamToFile)
        streamMenu.addAction(streamToFileAct)
        streamToPortAct = QAction('&UDP Protocol', self)
        streamToPortAct.setStatusTip('Stream Incoming Data To UDP Service (Not Implemented)')
        streamToPortAct.triggered.connect(self._onStreamToUDP)
        streamMenu.addAction(streamToPortAct)
        self._streamMenu = streamMenu
        boardMenu.addMenu(streamMenu)
        streamStopAct = QAction('&Stop Stream', self)
        streamStopAct.setStatusTip('Stop Streaming Incoming Data')
        streamStopAct.triggered.connect(self._onStreamStop)
        streamStopAct.setVisible(False)
        self._streamStopAct = streamStopAct
        boardMenu.addAction(streamStopAct)

        # Quit option
        quitAct = QAction('&Quit Application', self)
        quitAct.setShortcut('Ctrl+Q')
        quitAct.setStatusTip('Quit Application')
        quitAct.triggered.connect(self.close)
        boardMenu.addAction(quitAct)

        self._boardMenu = boardMenu
        menubar.addMenu(boardMenu)

        # Set default font size for tooltips
        QToolTip.setFont(QFont('SansSerif', 10))

        # Configure the interface widget
        interface = InterfaceWidget()
        interface.configureConnectionClicked.connect(self._showConnectionDialogListener)
        interface.connect.connect(self._connectListener)
        self._interface = interface
        self.setCentralWidget(interface)


        # Show ready message when ui is loaded
        self._statusBar = self.statusBar();
        self._statusBar.showMessage('Ready')
        self.show()


    def updateBoardMenu(self):
        """Board menu tab."""
        if (self._connection.status() == 'Connected'):
            self._connectionAct.setText('Reconnect')
        else:
            self._connectionAct.setText('Connect')


    def loadBoard(self, name):
        """Load a board."""
        self._board = next((x for x in availableBoards if x.name() == name), None)

        # Throw for no board
        if (self._board == None):
            raise ValueError('board not found')

        # Update values from board configuration
        self._ip = self._board.defaultIp()
        self._port = self._board.defaultPort()

        # Select connection
        self.loadConnection(self._board.connectionType())

        self.updateUI()

        print("Board '{}' loaded".format(name))
        self._statusBar.showMessage('{} selected'.format(self._board.name()))


    def loadConnection(self, type):
        """Load a connection."""
        self._connection = next((x for x in availableConnections if x.type() == type), None)

        # Throw for no connection
        if (self._connection == None):
            raise ValueError('connection not found')

        # Set the ip and port
        self._connection.setIp(self._ip)
        self._connection.setPort(self._port)

        print("Connection '{}' loaded".format(type))






    def updateUI(self):
        """Update all ui elements."""
        self.updateStatusValues()
        self.updateDeviceList()
        self.updateData()

    def updateStatusValues(self):
        """Update all status values."""
        # Set static board information
        self._interface.setBoardInformation(self._board)
        # Set dynamic board information
        self._interface.setIpAndPort(self._ip, self._port)
        self._interface.setStatus(self._connection.status())

    def updateDeviceList(self):
        """Update device lists."""
        self._interface.updateDeviceList(self._board.deviceList())

    def center(self):
        """Center the main window."""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def updateData(self):
        """Update all data elements."""
        self._interface.updateData()






    def closeEvent(self, event):
        """Confirm closing application."""
        # Close for no connection
        if (self._connection.status() != 'Connected'):
            event.accept()
        # Ask for confirmation
        else:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to quit?", QMessageBox.Yes |
                QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Stop background task
                global backgroundTaskRunning
                backgroundTaskRunning = False

                # Close app
                event.accept()
            else:
                # Keep app open
                event.ignore()








    @pyqtSlot()
    def _showConnectionDialogListener(self):
        """Show connection dialog listener."""
        self.connectionDialog.setValues(self._ip, self._port)
        self.connectionDialog.show()


    @pyqtSlot(str, str)
    def _connectionSettingsChangedListener(self, ip, port):
        """Update connection settings listener."""
        self._ip = ip
        self._port = port
        self.updateStatusValues()


    @pyqtSlot()
    def _connectListener(self):
        """Try to connect listener."""
        # Do a reconnect if already connected
        if (self._connection.status() == 'Connected'):
            self._connection.disconnect()
            self._board.reset()
        try:
            self._connection.connect()
            self._statusBar.showMessage('Successfully connected to {} via {}'.format(self._board.name(), self._connection.type()))
            self.updateBoardMenu()
        except ConnectionError as e:
            print("Connection error, could not create connection: {}".format(e))
            self._statusBar.showMessage('Connection to {} via {} failed'.format(self._board.name(), self._connection.type()))

        self.updateUI()


    @pyqtSlot(QAction)
    def _selectBoardListener(self, action):
        """Select a board listener."""
        if (self._connection.status() == 'Connected'):
            self._connection.disconnect()
            self._board.reset()

        # Load selected board configuration
        self.loadBoard(action.text())

    @pyqtSlot()
    def _onStreamToFile(self):
        """Stream data to file."""
        # Get file location
        fileName = self.saveFileDialog()
        # Prepare file
        if (fileName != None):
            with open(fileName, "w") as fh:
                fh.write(','.join(['Device','Dimension','Date','Value']) + '\n')
                self._board.setFileName(fileName)
                self._streamMenu.menuAction().setVisible(False)
                self._streamStopAct.setVisible(True)

    @pyqtSlot()
    def _onStreamToUDP(self):
        """Stream data to udp service."""
        self._broadcast = UDPBroadcast(UDP_IP, UDP_PORT)
        self._streamMenu.menuAction().setVisible(False)
        self._streamStopAct.setVisible(True)

    @pyqtSlot()
    def _onStreamStop(self):
        """Stop streaming data."""
        # Stop all streaming to file and UDP
        if (self._broadcast != None):
            del self._broadcast
            self._broadcast = None
        elif (self._board.fileName() != None):
            self._board.setFileName(None)

        self._streamStopAct.setVisible(False)
        self._streamMenu.menuAction().setVisible(True)



    @pyqtSlot()
    def connectionIteration(self):
        """Next connection iteration listener."""
        # Only do something when there is a connection
        if (self._connection.status() == 'Connected'):
            # Get the new messages from the connection and unserialize them
            messages = list(map(lambda x: self._board.unserializeMessage(x), self._connection.getMessages()))

            # Flags
            data = False
            ui = False

            if (messages != None and len(messages) > 0):
                for message in messages:
                    # Message to register a device
                    if (message.type == 'Register'):
                        ui = True
                        self._board.registerDevice(Device(message.name, message.data['dir'], message.data['dim']))
                        self._statusBar.showMessage('Register Device: {}'.format(message.name))
                    # Message to deregister a device
                    elif (message.type == 'Deregister'):
                        ui = True
                        self._board.deregisterDevice(Device(message.name))
                        self._statusBar.showMessage('Deregister Device: {}'.format(message.name))
                    # Message with new data for a device (',' are escaped to '-')
                    elif (message.type == 'Data'):
                        data = True
                        self._board.updateData(message.name, message.data['values'])
                        # Stream data to file
                        if (self._board.fileName() != None):
                            with open(self._board.fileName(), "a") as fh:
                                for i in range(len(message.data['values'])):
                                    fh.write(','.join([message.name.replace(',','-'), str(i), str(time.time()), str(message.data['values'][i])]) + '\n')
                        # Stream data to UDP
                        # Using same format as for the .CSV files
                        if (self._broadcast != None):
                            for i in range(len(message.data['values'])):
                                self._broadcast.send(','.join([message.name.replace(',','-'), str(i), str(time.time()), str(message.data['values'][i])]))

                    # Message with unknown type
                    else:
                        print('Unknown message type: {}'.format(message.type))
                        pass

                # Update data and UI
                if (data):
                    self.updateData()
                if (ui):
                    self.updateUI()

            else:
                pass

            # Messages for outgoing devices
            messages = []

            # Calculate new values for all outgoing devices
            for device in self._board.deviceList():
                if (device.dir() == 'out' and device.functionRunning()):
                    data = [[] for i in range(device.dim())]
                    # Calculate next function step
                    for i in range(device.dim()):
                        f, p, s = device.function(i)
                        data[i] = utils.functionForLabel(f)(p, s)

                    # Update device
                    device.setData(data)

                    # Check if there are none-'None' values
                    if (None not in data):
                        # Create the message
                        messages.append(Message('out', device.name(), data))


            # Send and serialize messages
            if (len(messages) > 0):
                self._connection.sendMessages(list(map(lambda x: self._board.serializeMessage(x), messages)))





        # Print loop
        # print('Loop')



    def saveFileDialog(self):
        """Dialog to select location to save file."""
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Board Multi Plot For {}".format(self._board.name()),"{}/../../Plots/{} Multi Plot.csv".format(sys.path[0], self._board.name()),"Text Files (*.csv)", options=options)
        if fileName:
            print('Save multi plot to file: {}'.format(fileName))
        return fileName


# Run main app
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow()

    # Start the app
    sys.exit(app.exec_())
