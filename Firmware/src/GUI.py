# -*- coding: utf-8 -*-
"""
GUI demo program displaying the main features of SoftWEAR. 
It includes connect options, ADC and I2C port display capabilities and PWM
control widgets. The status bar reflects the most recent detected change in the 
hardware configuration.
"""
import sys             # Required for sys.argv
from PyQt5 import uic, QtWidgets, QtCore # Qt package required for all GUI elements
from time import sleep # Required for the background process period
import RoboCom as com  # SoftWEAR communication class. Used to communicate with the BeagleBone
import threading       # Imported for the GUI update thread

# Loads the gui Qt designer file. This replaces the need to programatically add and configure widgets 
form_class = uic.loadUiType("gui.ui")[0]

""" GLOBAL VARIABLES """
bacgkround_thread_running = True    # True while the inner thread has to run
button_connect = True               # True if the button connects, false if it disconnects
c = com.RoboCom('pc')               # The connection object
emg_list = []                       # List of EMG channels
imu_list = []                       # List of I2C channels
last_message = ''                   # Last message rcvd from the BeagleBone
 
class MyWindowClass(QtWidgets.QMainWindow, form_class):
    """ The Qt windows representing the form with all indicators and controls.
        It is reccomended to encapsulate it in a class for threading purposes."""
    def __init__(self, parent=None):        
        QtWidgets.QMainWindow.__init__(self, parent)    # these 2 operations are 
        self.setupUi(self)                              # from the example online
        
        """ Set-up the event functions """
        self.b_connect.clicked.connect(self.btn_go_clicked)
        self.hs_pwm1.valueChanged.connect(self.hs_pwm1_changed)
        self.hs_pwm2.valueChanged.connect(self.hs_pwm2_changed)
        self.sb_pwm1.valueChanged.connect(self.sb_pwm1_changed)
        self.sb_pwm2.valueChanged.connect(self.sb_pwm2_changed)
        self.rb_wired.toggled.connect(self.rb_wired_changed)
        self.timer = QtCore.QTimer()    # Create a timer for the background thread
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # every 10,000 milliseconds
        
    def btn_go_clicked(self):
        """ Event function for the connect button click. """
        global button_connect, c
        if button_connect:      # Check if the button purpose is to connect 
            if self.rb_wired.isChecked():   # Set the target IP
                c.target_ip = '192.168.7.2' # The IP of the BeagleBone  
            else:               
                c.target_ip = self.le_targetIP.text()
            c.start_communications()        # Start communications with the BBB
        else:                   # Button purpose is to disconnect
            c.stop_and_free_resources()
            c = com.RoboCom('pc')           # Reset the communications class
        
    def hs_pwm1_changed(self):
        """ Event that is triggered when the PWM1 slider bar is changed"""
        global c
        self.sb_pwm1.setValue(self.hs_pwm1.value()) # Update the PWM1 integer input
        to_send = {'type':'pwm_set', 'chn':0, 'val':self.hs_pwm1.value()}
        c.send_data(to_send)                        # Send the new PWM data
        
    def hs_pwm2_changed(self):
        """ Event that is triggered when the PWM2 slider bar is changed"""
        global c
        self.sb_pwm2.setValue(self.hs_pwm2.value()) # Update the PWM2 integer input
        to_send = {'type':'pwm_set', 'chn':1, 'val':self.hs_pwm2.value()}
        c.send_data(to_send)                        # Send the new PWM data
        
    def sb_pwm1_changed(self):        
        """ Event that is triggered when the PWM1 integer input is changed.
            We just update the slider, which in turn will send the data."""
        self.hs_pwm1.setValue(self.sb_pwm1.value())        
        
    def sb_pwm2_changed(self):
        """ Event that is triggered when the PWM2 integer input is changed.
            We just update the slider, which in turn will send the data."""
        self.hs_pwm2.setValue(self.sb_pwm2.value())
        
    def rb_wired_changed(self, enabled):
        """ Event that is triggered when the radiobox wired / wireless is changed
            This function only changes the enabled property of the target IP input """
        if enabled: 
            self.le_targetIP.setEnabled(False)
        else:
            self.le_targetIP.setEnabled(True)
        
    def closeEvent(self, event):
        """ Call the destructor on form close. This is required to stop the 
            background thread from executing."""
        self.__del__()
        
    def __del__(self):
        """ Class destructor. Stops the background thread. """
        global bacgkround_thread_running
        bacgkround_thread_running = False
        
    def update_ui(self):
        """ The UI update thread. Executed periodically and updates the devices
            lists (ADC and I2C), as well as the connection state. """
        global button_connect, emg_list, imu_list
        
        self.l_connStatus.setText(c.get_state())    # Get connection state
        # Update the connection button text and state. 
        if c.get_state() == "Connected":            
            button_connect = False
            self.b_connect.setText("Disconnect!")
        else:
            button_connect = True
            self.b_connect.setText("Connect!")
        self.statusbar.showMessage(last_message)    # Show last recieved message
        
        """ Handle EMGs """
        to_print = "EMG Channels: " + str(len(emg_list)) + "\n"
        for elem in emg_list:                       # Go through all elements in the ADC list
            if len(elem['sublist']) > 0:            # Check if there is a MUX attacjed
                for sub_elem in elem['sublist']:    # Go through all MUXed channels
                    if sub_elem['actv']:            # If active, print channels and value
                        to_print += "Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['val']) + "\n"
                    else:                           # If inactive, print the 'disconnected' status
                        to_print += "Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ' - disconnected\n'
            else:                   # No MUX attached -> we have no subchannels
                if elem['actv']:    # Check if channel active. If yes, print channel and value
                    to_print += "Channel " + str(elem['chn']) + ', value: ' + str(elem['val']) + '\n'
                else:               # Channel inactive -> print 'disconnected' status
                    to_print += "Channel " + str(elem['chn']) + ' - disconnected\n'         
        self.tdisp_devices_emg.setPlainText(to_print)
        
        """ Handle IMUs """
        to_print = "IMU Channels: " + str(len(imu_list)) + "\n"
        for elem in imu_list:                       # Go through all elements in the IMU list
            if len(elem['sublist']) > 0:            # Check if there is a MUX attacjed
                for sub_elem in elem['sublist']:    # Go through all MUXed channels
                    if sub_elem['actv']:            # If active, print channels, device and value
                        to_print += "Channel " + str(elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['vals']) + "\n"
                    else:                           # If inactive, print the 'disconnected' status
                        to_print += "Channel " + str(elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ' - disconnected\n'
            else:                   # No MUX attached -> we have no subchannels
                if elem['actv']:    # Check if channel active. If yes, print channel, device and value
                    to_print += "Channel " + str(elem['chn']) + ', type: ' + elem['device'] +', values: ' + str(elem['vals']) + '\n'
                else:               # Channel inactive -> print 'disconnected' status
                    to_print += "Channel " + str(elem['chn']) + ' - disconnected\n'         
        self.tdisp_devices_imu.setPlainText(to_print)
 
def process_emg(message):
    """ Processes a new emg message. Basically updates the emg list with the 
        elements recieved from the BeagleBone """
    global emg_list
    if message['type'] == 'emg':
        emg_list = message['channels']    
    # Sort the list in channel order
    emg_list = sorted(emg_list, key=lambda k: k['chn'])
    
def process_imu(message):
    """ Processes a new imu message. Basically updates the imu list with the 
        elements recieved from the BeagleBone """
    global imu_list
    if message['type'] == 'imu':
        imu_list = message['channels']        
    # Sort the list in channel order
    imu_list = sorted(imu_list, key=lambda k: k['chn'])
    
def background_thread():
    """ The communications thread. Periodically checks for recieved messages
        and processes them. """
    global bacgkround_thread_running, c, last_message
    while bacgkround_thread_running:    # Keep working until closed            
        recv_data = c.rcv_data()        # Get the recieved messages
        for message in recv_data:       # Process each message individually
            if message['type'] == 'message':
                last_message = message['message']
            if 'emg' in message['type']:
                process_emg(message)
            elif 'imu' in message['type']:
                process_imu(message)

        sleep(0.1)              # Sleep for 100ms
        
    c.stop_and_free_resources() # On exit, stop communications
 
app = QtWidgets.QApplication(sys.argv)  # From example project
myWindow = MyWindowClass(None)          # From example project

# Start the communication thread
threading.Thread(target=background_thread).start()

# Show the main window
myWindow.show()

app.exec_()         # From example project