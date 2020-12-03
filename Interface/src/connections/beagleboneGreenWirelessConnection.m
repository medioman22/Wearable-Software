classdef beagleboneGreenWirelessConnection
    properties (Access = public)    
        % The IP of the remote location
        ip = '192.168.7.2'

        % The Application Port
        port = 12345
        
        % Timeout in seconds. Affects the sending 'Sampling Period'
        timeout = 0.1
    end
    properties (Access = private)      
        % Send queue
        sendQueue = {}

        % Recv queue
        recvQueue = {}

        % Inner communications thread object
        commsThreadRun = true

        % tcp client
        t
    end
    
    
    methods
        function obj = beagleboneGreenWirelessConnection(ip, port, timeout)
            switch nargin
                case 0
                case 1
                    obj.ip = ip;
                case 2
                    obj.ip = ip;
                    obj.port = port;
                case 3
                    obj.ip = ip;
                    obj.port = port;
                    obj.timeout = timeout;
            end
        end
        
        function thread(obj)
            %%% Inner thread function, does all socket sending and recieving
            remainder = '';                                       % Remainder mechanism for TCP incomplete transmissions
            while true                                            % While loop dedicated to recieving and sending data
%                 if isempty(obj.t)                               % Check if a socket is created
%                     pause(0.5);                                 % Wait a bit
%                     continue;                                       % Retry on next loop
%                 end
                pause(0.01)
                try                                                % Socket timeout will throw an catchion
                    data = fscanf(obj.t, 1024);
                    if isempty(data)
                        break
                    end
                    mlist = split([remainder data], '}');  % Add the recieved data to the previous remainder
                    remainder = '';
                    while size(mlist,1) > 0                         % After it's split, go through all sub-messages to compose a complete message
                                                                    % If we have a message stub and it's imbalanced (more '{' than '}')
                        if ~isempty(remainder) && count(remainder, '{') > count(remainder, '}')
                            remainder = [remainder mlist{1}];              % Add the next sub-message
                            mlist = mlist(2:end,:);
                            if size(mlist,1) > 0
                                remainder = [remainder '}'];                    % Add terminator only if the split indicates we recieved it
                            end
                        elseif ~isempty(remainder)                             % If we have a message and it's balanced -> we have a complete message
                            obj.recvQueue(end+1,:) = {jsondecode(remainder)};
                            remainder = '';                          % After the recieve reset the remainder
                                                                     % If we have no message and the list is almost empty - only '' remains
                        elseif size(mlist,1) == 1 && isempty(mlist(1))
                             mlist = mlist(2:end,:);                            % Empty it
                        else                                         % If we have no message and the list is not empty -> start a new sub-message
                            remainder = remainder + mlist{1};
                            mlist = mlist(2:end,:);
                            if size(mlist,1) > 0
                                remainder = [remainder '}'];               % Add terminator only if the split indicates we recieved it
                            end
                        end
                    end
                            
                catch                                                % We expect timeouts, as we have non-blocking calls
%                 catch sock.error as exc                           % Socket error occured. Log it and mark the disconnect
%                     obj.logger.error('Socket Error occurred ' + str(exc))
%                     print('Error Occured ' + str(exc))
%                     obj.state = 'Disconnected'
%                     break
%                 catch catchion as exc                            % Log generic errors
%                     obj.logger.error('General Error occurred ' + str(exc) + ' rem ' + str(remainder))
                end
                while size(obj.sendQueue,1) > 0                     % Pop all elements from the sending queue and send them all
                    sendmessage = obj.sendQueue{1};
                    obj.sendQueue = obj.sendQueue(2:end,:);
                    obj.t.fprintf(jsonencode(sendmessage));
                end
                if ~obj.commsThreadRun                        % Terminate the background thread
                    return
                end
            end
        end
        
        function open(obj)
            %%% Start the background communication thread 
            obj.t = tcpip(obj.ip, obj.port, 'Timeout', obj.timeout);
            fopen(obj.t);
            thread(obj)
        end
        
        function close(obj)
            delete(obj)
        end
        
        function obj = delete(obj)
            %%% Close the connection and stop the communication thread.
            fclose(obj.t);
            delete(obj.t);
            clear obj.t
            obj.commsThreadRun = false;
            pause(0.5)
        end
        
        function sendMessages(obj, messages)
            %%% Send a data object to the remote host %%%
            for message = messages
                obj.sendQueue(end+1,:) = message;
            end
        end
        
        function messages = getMessages(obj) 
            %%% Get a list of all the messages that have been recieved
            %%% since the last call of this function
            messages = {};                                        % return object initialized as an empty list
            while size(obj.recvQueue, 1) > 0                      % Pop all messages from the recieve queue and add them to the return list
                messages(end + 1,:) = {jsonencode(obj.recvQueue{1})};
                obj.recvQueue = obj.recvQueue(2:end,:);
            end
        end
        
        function s = status(obj)
            %%% Returns the status of the TCP/IP client %%%
            try
                s = obj.t.Status;
            catch
                s = 'Not initialized';
            end
        end
    end
end
