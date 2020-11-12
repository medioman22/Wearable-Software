# -*- coding: utf-8 -*-
# Author: Cyrill Lippuner
# Date: October 2018
"""
Graphical User Interface

This application provides an interface to the firmware loaded on the BBB

Author: Salar Rahimi
Last edited: November 2020
"""
import base64                                                   # for decoding json messages
from datetime import datetime
import cProfile, pstats                                         # For profiling the code
import matplotlib.pyplot as plt                                 # Showing the picture for profiller result
import matplotlib.image as mpimg                                # Same reason as above                    
import os, glob , io , getpass                                  # Operating system package
import sys                                                      # System package
import time                                                     # Time package
import logging                                                  # Logging package
from PyQt5.QtCore import (  pyqtSlot,                           # Core functionality from Qt
                            QTimer)
from PyQt5.QtWidgets import (   QMainWindow,                    # Widget objects for GUI from Qt
                                QMenu,
                                QToolTip,
                                QMessageBox,
                                QAction,
                                QDesktopWidget,
                                QFileDialog,
                                QApplication)
from PyQt5.QtGui import (   QFont,                              # Media elements from Qt
                            QIcon)
import pyqtgraph as pg                                          # Custom graphics package
import numpy as np                                              # Number utility package
from interface import InterfaceWidget                           # Custom interface widget
from connectionDialog import ConnectionDialog                   # Dialog widget for connection settings
from udpBroadcast import UDPBroadcast                           # UDP Broadcast functionality
from boards.board import Device                                 # Board base class
from boards.beagleboneGreenWirelessBoard import BeagleboneGreenWirelessBoard # BBGW implementation
from connections.connection import Message                      # Message class
from connections.beagleboneGreenWirelessConnection import BeagleboneGreenWirelessConnection # BBGWConnection implementation
from utils import standardColorSet                              # Import color set
from SSH.SSHClient import SSHClient                             # Import the SSH Client class for running the python code.

# Logging settings
LOG_LEVEL_PRINT = logging.INFO                                  # Set print level for stout logging
LOG_LEVEL_SAVE = logging.DEBUG                                  # Set print level for .log logging


# Global variables
availableBoards = [BeagleboneGreenWirelessBoard()]              # List of available boards
availableConnections = [BeagleboneGreenWirelessConnection()]    # Utility class
MAX_POINTS = 180                                                # Max point for diag plot

# Settings
UDP_IP = "127.0.0.1"                                            # Default host ip
UDP_PORT = 12346                                                # Default host port
UPDATE_LOOP = 100                                                # Update rate of the stream in [ms]

PLOT_POINTS_SET = {                                             # Available plot points
    '32 Points': 32,
    '64 Points': 64,
    '126 Points': 126,
    '256 Points': 256,
    '512 Points': 512,
    '1024 Points': 1024,
    '2048 Points': 2048,
    '4096 Points': 4096
}
PLOT_POINTS = '256 Points'                                      # Default plot points


class MainWindow(QMainWindow):
    """The main window of the application."""
    #Profiler 
    _Profiler = None
    _ProfilerState = "Initialized"
    _ProfillerSavingLocation = None
    _porfillerFileFormat = ".pstats"
    # SSH client
    _Client = None
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
    # Flag whether hidden devices should be shown or hidden
    _showHiddenDevices = False
    # Popup with multi plot
    _popupPlotWidget = None
    # Devices that should be plotted
    _popupPlotsDevices = None
    # Plots used to display multi plot data for popup
    _popupPlots = None
    # Popup with diag plot
    _popupDiagPlotWidget = None
    # Plot used to display multi plot data for popup
    _popupDiagPlot = None
    # Update loop durations
    _updateLoopDurations = None
    # Logger module
    _logger = None

    def __init__(self):
        #Place the profiler here
        self._Profiler = cProfile.Profile()
        """Initialize the main window."""
        super().__init__()

        # Configure the logger
        self._logger = logging.getLogger('Main')
        self._logger.setLevel(LOG_LEVEL_PRINT)                  # Only {LOG_LEVEL} level or above will be saved
        # fh = logging.FileHandler('../Logs/Main.log', 'w')
        # formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        # fh.setFormatter(formatter)
        # fh.setLevel(LOG_LEVEL_SAVE)                             # Only {LOG_LEVEL} level or above will be saved
        # self._logger.addHandler(fh)

        self._logger.info("Main initializing …")

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
        self._connectionIteratorTimer.start(UPDATE_LOOP)
        self._logger.debug("Start timer [{}ms] for update loop".format(UPDATE_LOOP))

        self._logger.info("Main initialized")
        
        #making a folder for storing the profilling data
        self._DirectoryProf = os.getcwd() + "\\Profiller"
        if(not os.path.isdir(self._DirectoryProf)):
            os.mkdir(self._DirectoryProf)
            self._logger.info("Proffiler folder is created")
        else:
            self._logger.info("Profiller folder is already available")

        #Check the files in the Profiling folder and show it in the combobox of the profiller
        for file in os.listdir(self._DirectoryProf):
            if file.endswith(self._porfillerFileFormat) or file.endswith('Firmware.png'):
                self._interface._ProfillerFiles.addItem(file)



    def initUI(self):
        """Initialize the ui of the main window."""
        # Initialize the window
        self.setWindowTitle('Graphical User Interface')
        self.setWindowIcon(QIcon('assets/Icon.png'))
        try:                                                    # OSX, Linux
            sys.stdout.write("\x1b]2;Graphical User Interface\x07")
        except:
            pass
        try:                                                    # Windows
            os.system("title Graphical User Interface")
        except:
            pass
        self.resize(960, 720)
        self.center()
        self._logger.debug("Main UI window created")

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

        # Hide menu
        showHideAct = QAction('&Show Hidden Devices', self)
        showHideAct.setStatusTip('Show Hidden Devices')
        showHideAct.triggered.connect(self._onShowHidden)
        showHideAct.setVisible(True)
        self._showHideAct = showHideAct
        boardMenu.addAction(showHideAct)
        hideHideAct = QAction('&Hide Hidden Devices', self)
        hideHideAct.setStatusTip('Hide Hidden Devices')
        hideHideAct.triggered.connect(self._onHideHidden)
        hideHideAct.setVisible(False)
        self._hideHideAct = hideHideAct
        boardMenu.addAction(hideHideAct)

        # Ignore devices
        ignoreAllAct = QAction('&Ignore All Devices', self)
        ignoreAllAct.setStatusTip('Ignore All Devices')
        ignoreAllAct.triggered.connect(self._onIgnoreAll)
        ignoreNoneAct = QAction('&Ignore No Devices', self)
        ignoreNoneAct.setStatusTip('Ignore No Devices')
        ignoreNoneAct.triggered.connect(self._onIgnoreNone)
        boardMenu.addAction(ignoreAllAct)
        boardMenu.addAction(ignoreNoneAct)

        # Plot points selection menu
        plotPointsSelectionMenu = QMenu('Plot Points', self)
        for plotPoints, plotPointsLabel in enumerate(PLOT_POINTS_SET):
            plotPointsSelectionMenu.addAction(QAction(plotPointsLabel, self))
        plotPointsSelectionMenu.triggered.connect(self._setPlotPointsListener)
        boardMenu.addMenu(plotPointsSelectionMenu)
        boardMenu.addSeparator()

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
        boardMenu.addSeparator()

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

        # Multi plot
        showMultiPlotAct = QAction('&Multi Plot', self)
        showMultiPlotAct.setStatusTip('Plot multiple devices')
        showMultiPlotAct.triggered.connect(self._onShowMultiPlotInPopup)
        boardMenu.addAction(showMultiPlotAct)

        # Diag plot
        showDiagPlotAct = QAction('&Diagnosis Plot', self)
        showDiagPlotAct.setStatusTip('Plot update loop duration')
        showDiagPlotAct.triggered.connect(self._onShowDiagPlotInPopup)
        boardMenu.addAction(showDiagPlotAct)
        boardMenu.addSeparator()

        # Scan menu
        scanStopAct = QAction('&Stop Scan', self)
        scanStopAct.setStatusTip('Stop Scanning For Devices')
        scanStopAct.triggered.connect(self._onScanStop)
        scanStopAct.setVisible(True)
        self._scanStopAct = scanStopAct
        boardMenu.addAction(scanStopAct)
        scanStartAct = QAction('&Start Scan', self)
        scanStartAct.setStatusTip('Start Scanning For Devices')
        scanStartAct.triggered.connect(self._onScanStart)
        scanStartAct.setVisible(False)
        self._scanStartAct = scanStartAct
        boardMenu.addAction(scanStartAct)
        boardMenu.addSeparator()

        # Quit option
        quitAct = QAction('&Quit Application', self)
        quitAct.setShortcut('Ctrl+Q')
        quitAct.setStatusTip('Quit Application')
        quitAct.triggered.connect(self.close)
        boardMenu.addAction(quitAct)

        self._boardMenu = boardMenu
        menubar.addMenu(boardMenu)
        self._logger.debug("Main UI menu created")

        # Set default font size for tooltips
        QToolTip.setFont(QFont('SansSerif', 10))
        self._logger.debug("Main UI tooltip created")

        # Configure the interface widget
        interface = InterfaceWidget()
        interface.configureConnectionClicked.connect(self._showConnectionDialogListener)
        interface.connect.connect(self._connectListener)
        interface.sendMessage.connect(self._sendMessageListener)
        interface.update.connect(self._updateInterfaceListener)
        # Add Profiller
        interface.StartProfiller.connect(self._StartProfillerListener)
        interface.StopProfiller.connect(self._StopProfillerListener)
        interface.visualizeProfiler.connect(self._VisualizeProfillerListener)
        interface.updateProfillerFile.connect(self._UpdateProfillerFileListener)
        interface._profillergrouplayout.setTitle("Profiller")

        self._interface = interface
        self.setCentralWidget(interface)
        self._logger.debug("Main UI interface created")


        # Show ready message when ui is loaded
        self._statusBar = self.statusBar();
        self._statusBar.showMessage('Ready')
        self.show()
        self._logger.debug("Main UI loaded")


    def updateBoardMenu(self):
        """Board menu tab."""
        if (self._connection.status() == 'Connected'):          # Reconnect if already connected
            self._connectionAct.setText('Reconnect')
        else:
            self._connectionAct.setText('Connect')


    def loadBoard(self, name):
        """Load a board."""
        if (self._connection != None):                          # Check for existing connection
            self._connection.disconnect()                       # Disconnect
        if (self._board != None):                               # Check for existing board
            self._board.reset();                                # Reset board
            self._onStreamStop();                               # Stop all streams

        self._board = next((x for x in availableBoards if x.name() == name), None)
        self._board.setMaxPoints(PLOT_POINTS_SET[PLOT_POINTS])  # Set plot points

        # Throw for no board
        if (self._board == None):
            raise ValueError('board not found')

        # Update values from board configuration
        self._ip = self._board.defaultIp()
        self._port = self._board.defaultPort()
        self._logger.debug("Reset IP/Port to default values {}/{} of board '{}'".format(self._board.defaultIp(), self._board.defaultPort(), name))

        # Select connection
        self.loadConnection(self._board.connectionType())

        # Refresh UI
        self.updateUI()

        self._logger.info("Board '{}' loaded".format(name))
        self._statusBar.showMessage('{} selected'.format(self._board.name()))


    def loadConnection(self, type):
        """Load a connection."""
        if (self._connection != None):                          # Check for existing connection
            self._connection.disconnect()                       # Disconnect

        self._connection = next((x for x in availableConnections if x.type() == type), None)

        # Throw for no connection
        if (self._connection == None):
            raise ValueError('connection not found')

        # Set the ip and port
        self._connection.setIp(self._ip)
        self._connection.setPort(self._port)

        # Clear diag
        self._updateLoopDurations = []

        self._logger.info("Connection '{}' loaded".format(type))

    #This function command the board to start the code
    def RunPythonScript(self):
        if (True): #self._Client == None or not self._Client.state
            self._Client = SSHClient(host=self._ip, port=22, username='debian', password='temppwd')
            self._Client.execute('python Wearable-Software/Firmware/src/Main.py [dmepf]', sudo=True)
    #This function tried to connect to the board
    def EstablishConnection(self):
        """Try to connect listener."""
        if (self._connection.status() == 'Connected'):          # Do a reconnect if already connected
            self._logger.info("Terminate existing connection before reconnecting")
            self._connection.disconnect()
            self._board.reset()
            self._onStreamStop()
            self._connection = None
        try:
            self._logger.debug("Start connection attempt …")
            self.loadConnection(self._board.connectionType())   # Create connection
            self._connection.connect()                          # Start connection attempts
            self._logger.debug("Connection successfully established") # Reaching next line means connection is established
            self._logger.info('Successfully connected to {} via {}'.format(self._board.name(), self._connection.type()))
            self._statusBar.showMessage('Successfully connected to {} via {}'.format(self._board.name(), self._connection.type()))
            time.sleep(0.1)                                     # Wait a bit
                                                                # Send a message to get a list of all devices
            self._connection.sendMessages([self._board.serializeMessage(Message('DeviceList',''))])
            self.updateBoardMenu()                              # Refresh UI
        except ConnectionError as e:                            # Error thrown during the connection attempt
            if (self._Client != None ):
                if (self._Client.state):
                    self._connection._state = "Connecting ..."
            else:
                self._connection._state = "Disconnected" 
            self._logger.error("Connection error, could not create connection: {}".format(e))
            self._statusBar.showMessage('Connection to {} via {} failed'.format(self._board.name(), self._connection.type()))


    def updateUI(self):
        """Update all ui elements."""
        self.updateStatusValues()
        self.updateProfillerStatus()
        self.updateDeviceList()
        #self.updateData()
        self._logger.debug("Main UI updated")

    def updateProfillerStatus(self):
        """Update profiller status value"""
        self._interface.setProfillerStatus(self._ProfilerState)

    def updateStatusValues(self):
        """Update all status values."""
        self._interface.setBoardInformation(self._board)        # Set static board information
        self._interface.setIpAndPort(self._ip, self._port)      # Set dynamic board information
        self._interface.setStatus(self._connection.status())    # Set current connection status
        self._interface.setScanLabel(self._connection.status() == 'Connected') # Set scan label

    def updateDeviceList(self):                                 # Filter device list by hidden devices
        """Update device lists."""
        self._interface.updateDeviceList(list(filter(lambda x: not x.hide() or self._showHiddenDevices, self._board.deviceList())))

    def center(self):
        """Center the main window."""
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().availableGeometry().center()
        # qr.moveCenter(cp)
        # self.move(qr.topLeft())
        self.showMaximized()


    def updateData(self):
        """Update all data elements."""
        self._interface.updateData()


    def closeEvent(self, event):
        """Confirm closing application."""
        # Close for no connection
        if (self._connection.status() != 'Connected'):
            self._connection.disconnect()
            self._board.reset()
            self._onStreamStop()
            event.accept()
        # Ask for confirmation
        else:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to quit?", QMessageBox.Yes |
                QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # Terminate connection and stop data streams
                self._connection.disconnect()
                self._Client.close() #closing the python code for Firmware
                self._board.reset()
                self._onStreamStop()

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
        self._logger.debug("Show connection settings dialog")


    @pyqtSlot(str, str)
    def _connectionSettingsChangedListener(self, ip, port):
        """Update connection settings listener."""
        self._ip = ip
        self._port = port
        self.updateStatusValues()
        self._logger.debug("Update connection settings")


    @pyqtSlot()
    def _connectListener(self):
        try:
            self.RunPythonScript()                              #execute the Firmware code
        except:
            self._Client = None
        
        self.EstablishConnection()                              #Connect to the board

        self.updateUI()

    @pyqtSlot()
    def _StartProfillerListener(self):
        self._Profiler.enable()
        self._ProfilerState = "Profilling ..."
        #Command board to profile
        self._connection.sendMessages([self._board.serializeMessage(Message('profile','', {'value': True}))])
        self.updateUI()

    @pyqtSlot()
    def _StopProfillerListener(self):
        self._Profiler.disable()
        TimeObject = datetime.now()
        s = io.StringIO() 
        ps = pstats.Stats(self._Profiler,stream=s).strip_dirs().sort_stats('cumulative')
        ps.dump_stats(self._DirectoryProf + "\\" + TimeObject.strftime("%d-%b-%Y_%H-%M-%S.%f")+"_Interface" + self._porfillerFileFormat)
        #self._Profiler.dump_stats(self._DirectoryProf + "\\" + TimeObject.strftime("%d-%b-%Y_%H-%M-%S.%f")+"_Interface" + self._porfillerFileFormat)
        
        #For stopping process of profilling in the board
        self._connection.sendMessages([self._board.serializeMessage(Message('profile','', {'value': False})),self._board.serializeMessage(Message('profile_FileName','', 
            {'value': TimeObject.strftime("%d-%b-%Y_%H-%M-%S.%f")+"_Firmware"}))]) 
        self._ProfilerState = "Stopped"
        self._Profiler = cProfile.Profile()
        self.updateUI()
    
    @pyqtSlot()
    def _VisualizeProfillerListener(self):
        self._interface._ProfillerFile
        #This option is for SnakeViz
        #cmd = 'cmd /c snakeviz '+"Profiller\\"+self._interface._ProfillerFile 
        #os.system('cmd /c snakeviz '+"Profiller\\"+self._interface._ProfillerFile)
        #This option is for gprof2dot
        if 'win' in sys.platform and not "-- Select" in self._interface._ProfillerFile:
            if not os.path.isfile('Profiller\\'+self._interface._ProfillerFile.replace('.pstats','.png')):
                cmd = 'cmd /c gprof2dot -f pstats Profiller\\'+ self._interface._ProfillerFile +' | dot -Tpng -o Profiller\\'+self._interface._ProfillerFile.replace('.pstats','.png')
                os.system(cmd)
            img = mpimg.imread('Profiller\\'+self._interface._ProfillerFile.replace('.pstats','.png'))
            plt.imshow(img)
            plt.show()
        elif 'linux' in sys.platform and not "-- Select" in self._interface._ProfillerFile:
            if not os.path.isfile('Profiller/'+self._interface._ProfillerFile.replace('.pstats','.png')):
                cmd = 'gprof2dot -f pstats Profiller/'+ self._interface._ProfillerFile +' | dot -Tpng -o Profiller/'+self._interface._ProfillerFile.replace('.pstats','.png')
                os.system(cmd)
            img = mpimg.imread('Profiller/'+self._interface._ProfillerFile.replace('.pstats','.png'))
            plt.imshow(img)
            plt.show()


    @pyqtSlot()
    def _UpdateProfillerFileListener(self):
        #Updating the profiller
        indexSelected = self._interface._ProfillerFiles.currentIndex()
        self._interface._ProfillerFiles.clear()
        self._interface._ProfillerFiles.addItem("-- Select The File To Visualize --")
        for file in os.listdir(self._DirectoryProf):
            if file.endswith(self._porfillerFileFormat) or file.endswith('Firmware.png'):
                self._interface._ProfillerFiles.addItem(file)
        self._interface._ProfillerFiles.setCurrentIndex(indexSelected)


    @pyqtSlot(QAction)
    def _selectBoardListener(self, action):
        """Select a board listener."""
        if (self._connection.status() == 'Connected'):          # Remove existing board, terminate connection and stop data streams
            self._logger.info("Terminate existing connection")
            self._connection.disconnect()
            self._board.reset()

        self.loadBoard(action.text())                           # Load selected board configuration

    @pyqtSlot()
    def _onStreamToFile(self):
        """Stream data to file."""
        fileName = self.saveFileDialog()                        # Get file location
        if (fileName != None):                                  # Prepare file if one is selected
            with open(fileName, "w") as fh:
                self._logger.info("Stream data to file '{}'".format(fileName))
                fh.write(','.join(['Device','Dimension','Date','Value']) + '\n')
                self._board.setFileName(fileName)
                self._streamMenu.menuAction().setVisible(False)
                self._streamStopAct.setVisible(True)
                shortFileName = (fileName[:32] and '...') + fileName[32:]
                self._interface.setStreamLabel(True, '{}'.format(shortFileName))

    @pyqtSlot()
    def _onStreamToUDP(self):
        """Stream data to udp service."""
        self._logger.info("Stream data to port '{}'".format(UDP_PORT))
        self._broadcast = UDPBroadcast(UDP_IP, UDP_PORT)        # Create UDP data stream
        self._streamMenu.menuAction().setVisible(False)
        self._streamStopAct.setVisible(True)
        self._interface.setStreamLabel(True, 'UDP {}:{}'.format(UDP_IP, UDP_PORT))

    @pyqtSlot()
    def _onStreamStop(self):
        """Stop streaming data."""
        if (self._broadcast != None):                           # Stop all streaming to UDP
            del self._broadcast
            self._broadcast = None
        elif (self._board.fileName() != None):                  # Stop all streaming to file
            self._board.setFileName(None)
        self._logger.info("Data streaming has been stopped")

        self._streamStopAct.setVisible(False)
        self._streamMenu.menuAction().setVisible(True)
        self._interface.setStreamLabel(False)

    @pyqtSlot()
    def _onScanStop(self):
        """Stop streaming data."""
        self._interface.setScanLabel(False)
        self._connection.sendMessages([self._board.serializeMessage(Message('Scan','', {'value': False}))])
        self._logger.info("Stop scanning")

        self._scanStopAct.setVisible(False)
        self._scanStartAct.setVisible(True)

    @pyqtSlot()
    def _onScanStart(self):
        """Start streaming data."""
        self._interface.setScanLabel(True)
        self._connection.sendMessages([self._board.serializeMessage(Message('Scan','', {'value': True}))])
        self._logger.info("Start scanning")

        self._scanStartAct.setVisible(False)
        self._scanStopAct.setVisible(True)

    @pyqtSlot()
    def _onShowHidden(self):
        """Show hidden devices."""
        self._showHiddenDevices = True
        self.updateDeviceList()
        self._logger.info("Show hidden devices")

        self._showHideAct.setVisible(False)
        self._hideHideAct.setVisible(True)

    @pyqtSlot()
    def _onHideHidden(self):
        """Hide hidden devices."""
        self._showHiddenDevices = False
        self.updateDeviceList()
        self._logger.info("Hide hidden devices")

        self._showHideAct.setVisible(True)
        self._hideHideAct.setVisible(False)

    @pyqtSlot()
    def _onIgnoreAll(self):
        """Ignore all devices."""
        for device in self._board.deviceList():
            device.setIgnore(True)
        self.updateDeviceList()
        self._logger.info("Ignore All devices")

    @pyqtSlot()
    def _onIgnoreNone(self):
        """Ignore no devices."""
        for device in self._board.deviceList():
            device.setIgnore(False)
        self.updateDeviceList()
        self._logger.info("Ignore No devices")

    @pyqtSlot(QAction)
    def _setPlotPointsListener(self, action):
        """Set plot points listener."""
        global PLOT_POINTS
        PLOT_POINTS = action.text()
        self._board.setMaxPoints(PLOT_POINTS_SET[PLOT_POINTS])
        self._logger.info("Set plot {}".format(action.text()))


    @pyqtSlot()
    def connectionIteration(self):
        #check the connection if SSH is created
        if(self._Client != None):
            if (self._Client.state and self._connection._state != "Connected"):
                self.EstablishConnection()
                self.updateUI()
        """Next connection iteration listener."""
        if (self._connection.status() == 'Connected'):          # Only do something when there is a connection
                                                                # Get the new messages from the connection and unserialize them
            messages = list(map(lambda x: self._board.unserializeMessage(x), self._connection.getMessages()))

            data = False                                        # Data refresh flag
            ui = False                                          # UI refresh flag
            multiPlot = False                                   # Multiplot flag

            if (messages != None and len(messages) > 0):
                for message in messages:
                    if (message.type == 'Register'):            # Message to register a device
                        ui = True                               # Raise UI refresh flag
                        self._board.registerDevice(Device(message.name, message.data)) # Register device
                        self._logger.info('Register Device: {}'.format(message.name))
                        self._statusBar.showMessage('Register Device: {}'.format(message.name))
                    elif (message.type == 'Deregister'):        # Message to deregister a device
                        ui = True                               # Raise UI refresh flag
                        self._board.deregisterDevice(Device(message.name)) # Deregister device
                        self._logger.info('Deregister Device: {}'.format(message.name))
                        self._statusBar.showMessage('Deregister Device: {}'.format(message.name))
                    elif (message.type == 'D'):
                        data = True                             # Raise data refresh flag
                                                                # Update the data
                        for messageData in message.data['data']: # Loop through all data blocks
                            name = messageData['name']          # Name of the device
                            valuesArray = messageData['values'] # New values of the device
                            for values in valuesArray:          # Loop all new values (timestamp, [values], cycleDuration)
                                self._board.updateData(name, values[1], values[0], messageData['cycle'])
                                if (self._board.fileName() != None): # Stream data to file
                                    with open(self._board.fileName(), "a") as fh: # Open the file
                                        for i in range(len(values[1])): # Loop through all dimensions
                                                                # Look for correct device
                                            for device in self._board.deviceList():
                                                                # Check if it exists and should be ignored or is hidden
                                                if (device.name() == name and not device.ignore() and not device.hide()):
                                                    fh.write(','.join([ name.replace(',','-'), # Write data entry
                                                                        str(i),
                                                                        str(values[0]),
                                                                        str(values[1][i])]) + '\n')

                                if (self._broadcast != None):   # Stream data to UDP using same format as for the CSV files
                                    for i in range(len(values[1])): # Loop through all dimensions
                                        for device in self._board.deviceList(): # Look for correct device
                                                                # Check if it exists and should be ignored or is hidden
                                            if (device.name() == name and not device.ignore() and not device.hide()):
                                                self._broadcast.send(','.join([ name.replace(',','-'), # Send data entry
                                                                                str(i),
                                                                                str(values[0]),
                                                                                str(values[1][i])]))
                                if (self._popupPlotWidget != None and self._popupPlotWidget.isVisible()): # Multiplot data in window
                                    multiPlot = True
                                    p = 0
                                    for d, device in enumerate(self._popupPlotsDevices):
                                        pastData = device.pastData()
                                        for i in range(device.dim()):
                                            if device.activeDim()[i] == True: # Check if dimension is active
                                                self._popupPlots[p].setData(y=np.asarray(pastData[i]), x=np.arange(len(pastData[i]))) # Plot values
                                                p += 1

                    elif (message.type == 'CycleDuration'):     # Cycle duration message
                        self._logger.debug('Cycle durations: {}', str(message.data['values']))
                        self._interface.setCycleDurationLabel(message.data['values'])
                        self._updateLoopDurations.append(message.data['values']['update'] * 1000) # in ms
                        while (MAX_POINTS < len(self._updateLoopDurations)): # Create overflow for past values
                            self._updateLoopDurations.pop(0)
                        if self._popupDiagPlot != None:
                            self._popupDiagPlot.setData(y=np.asarray(self._updateLoopDurations), x=np.arange(len(self._updateLoopDurations))) # Plot values
                    elif (message.type == 'PNG'):
                        Image = base64.b64decode(message.data['values'])
                        if 'win' in sys.platform:
                            Filename =self._DirectoryProf +"\\"+ message.name
                        elif 'linux' in sys.platform:
                            Filename =self._DirectoryProf +"/"+ message.name
                        f = open(Filename,'wb')
                        f.write(Image)
                        f.close()

                    elif (message.type == 'Ping'):              # Ping message
                        self._logger.debug('PING')

                    else:                                       # Message with unknown type
                        self._logger.warn('Unknown message type: {}'.format(message.type))
                        pass

                if (data and not multiPlot):                    # Update data if data flag has been raised (except multi plot is active)
                    self.updateData()
                if (ui):                                        # Update UI if UI flag has been raised
                    self.updateUI()

            else:
                pass

            messagesSend = []                                   # Messages for outgoing devices

            # for device in self._board.deviceList():             # Calculate new values for all outgoing devices
            #     if (device.dir() == 'out' and device.functionRunning()): # Check for running function
            #         values = [[] for i in range(device.dim())]  # Prepare data list with dimension
            #         for i in range(device.dim()):               # Calculate new data for device
            #             f, p, s = device.function(i)            # Get function parameter
            #             values[i] = utils.functionForLabel(f)(p, s) # Use utility class function
            #
            #         device.setData(values)                      # Update device
            #
            #         if (None not in values):                    # Check if there are none-'None' values
            #             messagesSend.append(Message('out', device.name(), {'values': values})) # Create the message


            if (len(messagesSend) > 0):                         # Send and serialize messages
                self._connection.sendMessages(list(map(lambda x: self._board.serializeMessage(x), messagesSend)))
        

            self.update()                                       # Update all GUI
            """Ping"""
            # self._connection.sendMessages([self._board.serializeMessage(Message('Ping',''))]);

    @pyqtSlot(Message)
    def _sendMessageListener(self, message):
        """Listen to send message event from the interface and pass them to the connection."""
        self._connection.sendMessages([self._board.serializeMessage(message)])

    @pyqtSlot()
    def _updateInterfaceListener(self):
        """Listen to update from the interface."""
        self.updateDeviceList()


    def _onShowMultiPlotInPopup(self):
        """Show multi plot in popup."""
        if (self._popupPlotWidget != None):                       # Clear popup
            self._popupPlotWidget.close()

        # Widget for plot data
        self._popupPlots = []
        self._popupPlotWidget = pg.PlotWidget(title='Diagnosis Plot – Update Loop Duration')
        self._popupPlotWidget.setWindowTitle(self._board.name())
        self._popupPlotWidget.showAxis('bottom', False)
        self._popupPlotsDevices = list(filter(lambda x: not x.ignore() and not x.hide(), self._board.deviceList()))
        for d, device in enumerate(self._popupPlotsDevices):
            for i in range(device.dim()):
                if device.activeDim()[i] == True:               # Check if dimension is active
                    plot = self._popupPlotWidget.plot(pen=(standardColorSet[d]), name="Plot {}({})".format(device.name(), i))
                    self._popupPlots.append(plot)
        self._logger.debug("Popup Multi Plot For {}".format(self._board.name()))
        self._popupPlotWidget.show()
        self._popupPlotWidget.activateWindow()
        self._popupPlotWidget.raise_()

    def _onShowDiagPlotInPopup(self):
        """Show diag plot in popup."""
        if (self._popupDiagPlotWidget != None):                 # Clear popup
            self._popupDiagPlotWidget.close()

        # Widget for plot data
        self._popupDiagPlotWidget = pg.PlotWidget(title='Live Data Multi Plot')
        self._popupDiagPlotWidget.setWindowTitle(self._board.name())
        self._popupDiagPlotWidget.showAxis('bottom', False)
        self._updateLoopDurations = []                          # Reset diag
        self._popupDiagPlot = self._popupDiagPlotWidget.plot(pen=(standardColorSet[0]), name="Update Loop")
        self._logger.debug("Popup Diag Plot For {}".format(self._board.name()))
        self._popupDiagPlotWidget.show()
        self._popupDiagPlotWidget.activateWindow()
        self._popupDiagPlotWidget.raise_()


    def saveFileDialog(self):
        """Dialog to select location to save file."""
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog             # Can be uncommented if there is a problem with the default menu on OSX
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Board Multi Plot For {}".format(self._board.name()),"{}/../Plots/{} Multi Plot.csv".format(sys.path[0], self._board.name()),"Text Files (*.csv)", options=options) # Select file to store data stream
        if not fileName:
            self._logger.info('No file selected')
            return
        return fileName


# Run main app
if __name__ == '__main__':

    app = QApplication(sys.argv)                                # Create app
    ex = MainWindow()                                           # Show main window

    # Start the app
    sys.exit(app.exec_())                                       # Start Qt loop
