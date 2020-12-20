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
            obj.t = tcpip(obj.ip, obj.port, "Timeout", 0.1, "NetworkRole","client");
            obj.t.InputBufferSize = 1024;
            fopen(obj.t);
        end
        
        function messages = getMessages(obj, seconds, names)
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
            
            % If a specific list of input/output names is given
            if nargin == 3
                % Change names because structure fields cannot contain
                % characters like @,[,]
                new_names = strings(1,length(names));
                for n = 1:length(names)
                    new_name = names(n);
                    new_name = strrep(new_name,'@','_');
                    new_name = strrep(new_name,'[','_');
                    new_name = strrep(new_name,']','');
                    new_names(n) = new_name;
                    m.(new_name).time = [];
                    m.(new_name).value = [];
                end
                % Construct strucutre of all values and time for given name
                for i = 1:length(messages)
                    if messages{i}.type == "D" % Only consider data of type D
                        for j = 1:length(messages{i}.data) % Get all messages
                            for n = 1:length(names)
                                if messages{i}.data(j).name == names(n) % if the data name corresponds to the one we want
                                    % Create new structure with names as
                                    % fields and which contains arrays of
                                    % values and time for each name (field)
                                    for k = 1:size(messages{i}.data(j).values,1)
                                        new_name = new_names(n);
                                        m.(new_name).time = [m.(new_name).time, messages{i}.data(j).values(k,1)];
                                        m.(new_name).value = [m.(new_name).value, messages{i}.data(j).values(k,2)];
                                    end
                                end
                            end
                        end
                    end
                end

                % Convert absolute time to seconds (remove offset)
                try
                    fn = fieldnames(m);
                    for k = 1:numel(fn)
                        m.(fn{k}).time = m.(fn{k}).time - m.(fn{k}).time(1);
                    end
                catch
                    warning("Some I/O names were not found")
                end
                % Return the new version of messages
                messages = m;
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
