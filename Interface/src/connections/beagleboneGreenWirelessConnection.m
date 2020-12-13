classdef beagleboneGreenWirelessConnection < handle
    properties (Access = public)    
        % The IP of the remote location
        ip = '192.168.7.2'

        % The Application Port
        port = 12345
    end
    properties (Access = private)
        % tcp client
        t
    end
    
    
    methods
        function obj = beagleboneGreenWirelessConnection(ip, port)
            switch nargin
                case 0
                case 1
                    obj.ip = ip;
                case 2
                    obj.ip = ip;
                    obj.port = port;
            end
        end
        
        function obj = open(obj)
            %%% Start the background communication thread 
            obj.t = tcpip(obj.ip, obj.port);
            obj.t.InputBufferSize = 1024;
            fopen(obj.t);
        end
        
        function messages = getMessages(obj, seconds)
            warning('off', 'instrument:fscanf:unsuccessfulRead')
            remainder = '';
            messages = {};
            tic
            while toc < seconds
                data = fscanf(obj.t);
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
                        messages(end+1,:) = {jsondecode(remainder)};
                        remainder = '';                          % After the recieve reset the remainder
                                                                 % If we have no message and the list is almost empty - only '' remains
                    elseif size(mlist,1) == 1 && isempty(mlist(1))
                         mlist = mlist(2:end,:);                            % Empty it
                    else                                         % If we have no message and the list is not empty -> start a new sub-message
                        remainder = [remainder mlist{1}];
                        mlist = mlist(2:end,:);
                        if size(mlist,1) > 0
                            remainder = [remainder '}'];               % Add terminator only if the split indicates we recieved it
                        end
                    end
                end
            end
        end
        
         function sendMessages(obj, messages)
            %%% Send a data object to the remote host %%%
            while ~isempty(messages)           
                fprintf(obj.t, jsonencode(messages(1)));
                messages = messages(2:end);
            end
        end
        
        function close(obj)
            delete(obj)
        end
        
        function obj = delete(obj)
            %%% Close the connection and stop the communication thread.
            fclose(obj.t);
            delete(obj.t);
            clear obj.t
        end
    end
end
