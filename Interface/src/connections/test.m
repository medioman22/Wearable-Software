m1.type = 'Settings';
m1.name = 'PCA9685@I2C[1]';
m1.dutyFrequency = '50 Hz';

m2.type = 'Settings';
m2.name = 'PCA9685@I2C[2]';
m2.dutyFrequency = '100 Hz';

% Construct messages to send
m = [m1 m2];

% Initialize connection
c = beagleboneGreenWirelessConnection();
c.open();

% Sending the messages
c.sendMessages(m);

% Get values of following input/output
names = ["ADC_BASIC@ADC[P9_38]","ADC_BASIC@ADC[P9_39]","ADC_BASIC@ADC[P9_40]"];
messages = c.getMessages(20, names);

% Plot
figure
fn = fieldnames(messages);
for k = 1:numel(fn)
    plot(messages.(fn{k}).time,messages.(fn{k}).value)
hold on
end
hold off
xlabel("Time [s]")
ylabel("Volt [V]")
legend(fn,'Interpreter', 'none')
title("Results")
delete(c);
