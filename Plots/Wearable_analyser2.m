% Author: Victor Faraut
% Date: 28.12.2018

function [Wear_out, Wear_id] = Wearable_analyser2(Wear_file)
Wear_data   =   importdata(Wear_file);

index = [];

% read all the sensor value that is from the BNO055 and only this one,
% stores this info in a INDEX array to reduce the size of the array after
for i = 1:length(Wear_data.textdata(:,1))
    Wear_data.textdata{i,3} = strsplit(strcat(cell2mat(Wear_data.textdata(i,1)),",",cell2mat(Wear_data.textdata(i,2))));
    output = strsplit(Wear_data.textdata{i,3}{4},'@');
    if(strfind(output{1},'BNO055'))
%     if(strfind(output{1},'BNO055') && (sum(Wear_data.data(i,1) == [12,13,14,15])==1))
        index = [index i];
    end 
end

% Reduce the size of the data and timestamp to the only ones containing
% BNO055 as a sensor type
Wear_data.data = Wear_data.data(index,:);
Wear_data.textdata = Wear_data.textdata(index,3);

% Read the timestamp that was written by the python script (the first
% timestamp) and stores it inside a timestamp variable, read and stores the
% sensor ID also
for i = 1:length(Wear_data.data(:,1))
    output = strsplit(Wear_data.textdata{i}{4},'@');
    time = strsplit(Wear_data.textdata{i}{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp(i) = ((h*60 + m)*60)+s;
    sensor_id{i} = (strcat(output{1,3}(end-6),output{1,3}(end-1)));   
end

% attributes to the all unique sensor id to a variable that will be outputed
% as well as setting the array of structures to have a structur composed of
% data and timestamp for each sensor ID instead of have all things mixed
% up.
Wear_id = unique(sensor_id);
Wear_cleaned = [];
for id = 1:length(Wear_id)
    index = [];
    index = strcmp(sensor_id,Wear_id(id));
    Wear_cleaned(id).data = Wear_data.data(index,:);
    Wear_cleaned(id).timestamp = timestamp(index)';
end

Wear_out = [];


% way of checking if we have complete quaternion and if the quaternion is
% not complete it gets ignored. Loops on itself until it finds no more
% first quaternion indexs.
for id = 1:length(Wear_id)
    i = 1;
    while true
        % finds the index of the first part of a quaternion
        if find((Wear_cleaned(id).data(:,1)==12))
            first_idx = find((Wear_cleaned(id).data(:,1)==12));
            first_idx = first_idx(1);
            % checks if the 3 value after the first index are comming from
            % the same quaternion and if yes, stores it, if not, the first
            % index is set to 0 to be ignore on the following loop
            try (Wear_cleaned(id).data(first_idx+3,1))
                if (Wear_cleaned(id).data(first_idx+1,1)==13 && ...
                    Wear_cleaned(id).data(first_idx+2,1)==14 && ...
                    Wear_cleaned(id).data(first_idx+3,1)==15)

                    Wear_out(id).data(i,:) = [Wear_cleaned(id).data(first_idx,3),...
                                            Wear_cleaned(id).data(first_idx+1,3),...
                                            Wear_cleaned(id).data(first_idx+2,3),...
                                            Wear_cleaned(id).data(first_idx+3,3)];
                    Wear_out(id).timestamp(i,1) = Wear_cleaned(id).timestamp(first_idx);
                    Wear_cleaned(id).data(first_idx,1) = 0;
                    i = i+1;
                else
                    Wear_cleaned(id).data(first_idx,1) = 0;
                end
            catch
                Wear_cleaned(id).data(first_idx,1) = 0;
            end
        else
            break;
        end
    end   
end


end



