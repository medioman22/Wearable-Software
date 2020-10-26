import paramiko
import socket
import time



class SSHClient:
    "A wrapper of paramiko.SSHClient"
    TIMEOUT = 4
    
    username = ""
    password = ""
    host = ""
    port = ""

    def __init__(self, host, port, username, password, key=None, passphrase=None):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, port, username=username, password=password, pkey=key, timeout=self.TIMEOUT)

    def close(self):
        if self.client is not None:      
            try:
                self.stdin.write('\x03')
            except socket.error as e:
                self.client.connect(self.host, self.port, username=self.username, password=self.password, pkey=None, timeout=self.TIMEOUT)
                time.sleep(0.1)
                self.KillProcess()
                
            self.stdin = None
            self.stdout = None
            self.stderr = None
            self.client.close()
            self.client = None

    def KillProcess(self):
        feed_password = True
        command = 'sudo pkill -x python'
        
        stdin, _, _ = self.client.exec_command(command,get_pty=True)
        time.sleep(0.1)
        if feed_password:
            stdin.write(self.password + "\n")
            stdin.flush()

    def execute(self, command, sudo=False):
        feed_password = False
        if sudo and self.username != "root":
            command = "sudo -S -p '' %s" % command
            feed_password = self.password is not None and len(self.password) > 0
        self.stdin, self.stdout, self.stderr = self.client.exec_command(command,get_pty=True)

        if feed_password:
            self.stdin.write(self.password + "\n")
            self.stdin.flush()

        



if __name__ == "__main__":
    SSH = SSHClient(host='192.168.7.2', port=22, username='debian', password='temppwd') 
    try:
        #ret = threading.Thread(target= client.execute,args=('python Salar/Wearable-Software/Firmware/src/Main.py [dmepf]', True))
        #ret.start()
        SSH.execute('python Salar/Wearable-Software/Firmware/src/Main.py [dmepf]', sudo=True)
        #time.sleep(1)
        SSH.close()
        
        #print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
    except KeyboardInterrupt:
        #ret._stop()
        SSH.close() 


