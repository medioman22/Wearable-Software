import paramiko
import threading


class SSHClient:
    "A wrapper of paramiko.SSHClient"
    TIMEOUT = 4

    def __init__(self, host, port, username, password, key=None, passphrase=None):
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, port, username=username, password=password, pkey=key, timeout=self.TIMEOUT)

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def execute(self, command, sudo=False):
        feed_password = False
        if sudo and self.username != "root":
            command = "sudo -S -p '' %s" % command
            feed_password = self.password is not None and len(self.password) > 0
        stdin, stdout, stderr = self.client.exec_command(command)
        if feed_password:
            stdin.write(self.password + "\n")
            stdin.flush()
        return {'out': stdout.readlines(), 
                'err': stderr.readlines(),
                'retval': stdout.channel.recv_exit_status()}


if __name__ == "__main__":
    client = SSHClient(host='192.168.7.2', port=22, username='debian', password='temppwd') 
    try:
        ret = threading.Thread(target= client.execute,args=('python Salar/Wearable-Software/Firmware/src/Main.py [dmepf]', True))
        #client.execute('python Salar/Wearable-Software/Firmware/src/Main.py [dmepf]', sudo=True)
        ret.start()
        #print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
    except KeyboardInterrupt:
        ret._stop()
        client.close() 


