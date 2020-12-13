m1.type = 'Settings';
m1.name = 'PCA9685@I2C[1]';
m1.dutyFrequency = '50 Hz';

m2.type = 'Settings';
m2.name = 'PCA9685@I2C[2]';
m2.dutyFrequency = '100 Hz';

m = [m1 m2];

c = beagleboneGreenWirelessConnection();
c.open();

c.sendMessages(m);
messages = c.getMessages(5);

delete(c);
