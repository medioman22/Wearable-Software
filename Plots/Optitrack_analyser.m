% Author: Victor Faraut
% Date: 27.12.2018

function [Optitrack_cleaned, Optitrack_id] = Optitrack_analyser(Optitrack_file)
%UNTITLED3 Summary of this function goes here
%   Detailed explanation goes here

Optitrack_data  =   importdata(Optitrack_file);

Optitrack_cleaned = [];


for p = 1:length(Optitrack_data)
    output = strsplit(Optitrack_data{p});
    time = strsplit(output{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp =  ((h*60 + m)*60)+s;
    
    
    
    Optitrack_cleaned(1).timestamp(p,1) = timestamp; 
    sensor_id_temp = split(output{4},{'(', ','});
    %Optitrack_cleaned(1).sensor_id{p,1} =  sensor_id_temp{2};
    first_id = sensor_id_temp{2};
    Optitrack_id{1} = '1';
    
    quat_temp_x = split(output{8},{'(', ','});
    quat_temp_y = split(output{9},{'(', ','});
    quat_temp_z = split(output{10},{'(', ','});
    quat_temp_w = split(output{11},{'(', ','});
    Optitrack_cleaned(1).data(p,:) = [str2num(quat_temp_x{1}), ...
                                           str2num(quat_temp_y{1}), ...
                                           str2num(quat_temp_z{1}), ...
                                           str2num(quat_temp_w{1})];
    
    for j = 2:13
        Optitrack_cleaned(j).timestamp(p,1) = timestamp;
        sensor_id_temp = split(output{4+(8*(j-1))},{'(', ',', ')'});
        %Optitrack_cleaned(j).sensor_id{p,1} =  sensor_id_temp{1};
        Optitrack_id{j} = num2str((str2num(sensor_id_temp{1})-str2num(first_id))+1);
        
        quat_temp_x = split(output{8+(8*(j-1))},{'(', ','});
        quat_temp_y = split(output{9+(8*(j-1))},{'(', ','});
        quat_temp_z = split(output{10+(8*(j-1))},{'(', ','});
        quat_temp_w = split(output{11+(8*(j-1))},{'(', ',',')'});
        Optitrack_cleaned(j).data(p,:) = [str2num(quat_temp_x{1}), ...
                                                 str2num(quat_temp_y{1}), ...
                                                 str2num(quat_temp_z{1}), ...
                                                 str2num(quat_temp_w{1})];    
    end
    
end

end

