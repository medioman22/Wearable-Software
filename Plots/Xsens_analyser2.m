% Author: Victor Faraut
% Date: 28.12.2018


function [Xsens_out, Xsens_id] = Xsens_analyser2(Xsens_file)
Xsens_data   =   importdata(Xsens_file);

index = [];

for i = 1:length(Xsens_data.textdata(:,1))
    Xsens_data.textdata{i,3} = strsplit(strcat(cell2mat(Xsens_data.textdata(i,1)),",",cell2mat(Xsens_data.textdata(i,2))));
end
Xsens_data.textdata = Xsens_data.textdata(:,3);

% Read the timestamp that was written by the python script (the first
% timestamp) and stores it inside a timestamp variable, read and stores the
% sensor ID also
for i = 1:length(Xsens_data.data(:,1))
    output = strsplit(Xsens_data.textdata{i}{4},'@');
    time = strsplit(Xsens_data.textdata{i}{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp(i) = ((h*60 + m)*60)+s;
    sensor_id{i} = (output{1}(7:end-1));   
end

% attributes to the all unique sensor id to a variable that will be outputed
% as well as setting the array of structures to have a structur composed of
% data and timestamp for each sensor ID instead of have all things mixed
% up.
Xsens_id = unique(sensor_id);
Xsens_cleaned = [];
for id = 1:length(Xsens_id)
    index = [];
    index = strcmp(sensor_id,Xsens_id(id));
    Xsens_cleaned(id).data = Xsens_data.data(index,:);
    Xsens_cleaned(id).timestamp = timestamp(index)';
end


% way of checking if we have complete quaternion and if the quaternion is
% not complete it gets ignored. Loops on itself until it finds no more
% first quaternion indexs.
Xsens_out = [];

for id = 1:length(Xsens_id)
    i = 1;
    while true
        % finds the index of the first part of a quaternion
        if find((Xsens_cleaned(id).data(:,1)==1))
            first_idx = find((Xsens_cleaned(id).data(:,1)==1));
            first_idx = first_idx(1);
            % checks if the 3 value after the first index are comming from
            % the same quaternion and if yes, stores it, if not, the first
            % index is set to 0 to be ignore on the following loop

            try(Xsens_cleaned(id).data(first_idx+3,1))
                if (Xsens_cleaned(id).data(first_idx+1,1)==2 && ...
                    Xsens_cleaned(id).data(first_idx+2,1)==3 && ...
                    Xsens_cleaned(id).data(first_idx+3,1)==4)

                    Xsens_out(id).data(i,:) = [Xsens_cleaned(id).data(first_idx,3),...
                                            Xsens_cleaned(id).data(first_idx+1,3),...
                                            Xsens_cleaned(id).data(first_idx+2,3),...
                                            Xsens_cleaned(id).data(first_idx+3,3)];
                    Xsens_out(id).timestamp(i,1) = Xsens_cleaned(id).timestamp(first_idx);
                    Xsens_cleaned(id).data(first_idx,1) = 0;
                    i = i+1;
                else
                    Xsens_cleaned(id).data(first_idx,1) = 0;
                end
            catch
                Xsens_cleaned(id).data(first_idx,1) = 0;
            end
                
        else
            break;
        end
    end   
end


end