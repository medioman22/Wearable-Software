# -*- coding: utf-8 -*-
"""

"""
import sys
from PyQt5 import uic, QtWidgets, QtCore
from time import sleep
import RoboCom as com
import threading 
 
form_class = uic.loadUiType("gui.ui")[0]

""" GLOBAL VARIABLES """
bacgkround_thread_running = True    # True while the inner thread has to run
button_connect = True               # True if the button connects, false if it disconnects
c = com.RoboCom('pc')               # The connection object
emg_list = []                       # List of EMG channels
last_message = ''                   # Last message rcvd from the BeagleBone
 
class MyWindowClass(QtWidgets.QMainWindow, form_class):
    def __init__(self, parent=None):        
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        """ Set-up the event functions """
        self.b_connect.clicked.connect(self.btn_go_clicked)
        self.hs_pwm1.valueChanged.connect(self.hs_pwm1_changed)
        self.hs_pwm2.valueChanged.connect(self.hs_pwm2_changed)
        self.sb_pwm1.valueChanged.connect(self.sb_pwm1_changed)
        self.sb_pwm2.valueChanged.connect(self.sb_pwm2_changed)
        self.rb_wired.toggled.connect(self.rb_wired_changed)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(100)  # every 10,000 milliseconds
        
    def btn_go_clicked(self):
        global button_connect, c
        if button_connect:
            if self.rb_wired.isChecked():
                c.target_ip = '192.168.7.2'  # The IP of the BeagleBone  
            else:
                c.target_ip = self.le_targetIP.text()
            c.start_communications()
        else:
            c.stop_and_free_resources()
            c = com.RoboCom('pc')
        
    def hs_pwm1_changed(self):
        global c
        self.sb_pwm1.setValue(self.hs_pwm1.value())
        to_send = {'type':'pwm_set', 'chn':0, 'val':self.hs_pwm1.value()}
        c.send_data(to_send)
        
    def hs_pwm2_changed(self):
        global c
        self.sb_pwm2.setValue(self.hs_pwm2.value())
        to_send = {'type':'pwm_set', 'chn':1, 'val':self.hs_pwm2.value()}
        c.send_data(to_send)
        
    def sb_pwm1_changed(self):        
        self.hs_pwm1.setValue(self.sb_pwm1.value())        
        
    def sb_pwm2_changed(self):
        self.hs_pwm2.setValue(self.sb_pwm2.value())
        
    def rb_wired_changed(self, enabled):
        if enabled:
            self.le_targetIP.setEnabled(False)
        else:
            self.le_targetIP.setEnabled(True)
        
    def closeEvent(self, event):
        self.__del__()
        
    def __del__(self):
        global bacgkround_thread_running
        bacgkround_thread_running = False
        
    def update_ui(self):
        global button_connect
        to_print = ""
        self.l_connStatus.setText(c.get_state())
        if c.get_state() == "Connected":
            button_connect = False
            self.b_connect.setText("Disconnect!")
        else:
            button_connect = True
            self.b_connect.setText("Connect!")
        self.statusbar.showMessage(last_message)
        
        """ Handle EMGs """
        to_print += "EMG Channels: " + str(len(emg_list)) + "\n"
        for elem in emg_list:
            if len(elem['sublist']) > 0:
                for sub_elem in elem['sublist']:
                    if sub_elem['actv']:
                        to_print += "Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ', value: ' + str(sub_elem['val']) + "\n"
                    else:
                        to_print += "Channel " + str(sub_elem['chn']) + ', Mux ' + str(sub_elem['subchn']) + ' - disconnected\n'
            else:
                if elem['actv']:
                    to_print += "Channel " + str(elem['chn']) + ', value: ' + str(elem['val']) + '\n'
                else:
                    to_print += "Channel " + str(elem['chn']) + ' - disconnected\n'
         
        self.tdisp_devices_emg.setPlainText(to_print)
 
def process_emg(message):
    """ Processes a new emg message """
    global emg_list
    if message['type'] == 'emg':
        emg_list = message['channels']
    emg_list = sorted(emg_list, key=lambda k: k['chn'])
    
def background_thread(GUI_window):
    global bacgkround_thread_running, c, last_message
    while bacgkround_thread_running:    # Keep working until closed
    
        recv_data = c.rcv_data()
        for message in recv_data: 
            if message['type'] == 'message':
                last_message = message['message']
            if 'emg' in message['type']:
                process_emg(message)
            elif 'imu' in message['type']:
                pass
            
        #GUI_window.update_ui()  # Call the update method
        sleep(0.1)              # Sleep for 100ms
        
    c.stop_and_free_resources() # On exit, stop communications
 
app = QtWidgets.QApplication(sys.argv)
myWindow = MyWindowClass(None)
threading.Thread(target=background_thread, args=(myWindow,)).start()
myWindow.show()
app.exec_()