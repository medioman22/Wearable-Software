% Clean opened channels
if exist('u', "var")
    fclose(u);
    delete(u);
    clear u;
end

% Clean the rests
close all; clear all; clc;

% Listen on UDP broadcast on port 12346
u = udp('', 'LocalHost', '', 'LocalPort', 12346);
fopen(u);
u.ReadAsyncMode = 'continuous';
        
while 1
    % Receive UDP packets
    message = fscanf(u);
    messageParts = strsplit(message,',');
    
    % Ignore corrupted messages
    if (length(messageParts) ~= 4)
        continue;
    end
    
    disp(message);

    % Store values
    %dataLabels(end+1,:) = [ cellstr(messageParts{1}), cellstr(messageParts{2}) ];
    %data(end+1,:) = [ uint64(str2double(messageParts{3}) * 1000) str2num(messageParts{4}) ];
    
    % Wait a bit
    pause(0.01)
end

% Clean
fclose(u);
delete(u);
clear u;


% Data stored in data & dataLabels