% Author: Victor Faraut
% Date: 30.12.2018



%% 
% Load alle the data from the files selected and stores them localy in
% a matlab array of structurs as well as a array of the IDs of the sensors

clear all;

Opti_file =    "Recordings\Test-5-sensors-29-12-2018-bis\1546099115_logfile_9000.log";
Wear_file =    "Recordings\Test-5-sensors-29-12-2018-bis\1546099115_logfile_12346.log";
Xsens_file =   "Recordings\Test-5-sensors-29-12-2018-bis\1546099115_logfile_12347.log";

Hand_id = {'13', '20', '00B43C3A'};
Forearm_id = {'12', '21', '00B4221D'}; 
Upperarm_id = {'11', '22', '00B42217'}; 
Shoulder_id = {'10', '23', '00B42235'}; 
Torso_id = {'3', '24', '00B43C41'}; 

ids = {Hand_id, Forearm_id, Upperarm_id, Shoulder_id, Torso_id};

[Wear_cleaned, Wear_id] = Wearable_analyser2(Wear_file);
[Xsens_cleaned, Xsens_id] = Xsens_analyser2(Xsens_file);
[Opti_cleaned, Opti_id] = Optitrack_analyser(Opti_file);

%%
% clean the data to have the same first timestamp. It then select the
% sensor with less data and data match the two other. This is done to do a
% comparasion easier and it take the timestamp closer to the one that we
% are looking for. Good for data with different refreshrates. But induce
% error. At the end convert the data into matlab quaternion form. 

min_size = [];
for i = 1:length(ids)
    Opti_tmp_id = find(ismember(Opti_id,ids{i}{1}));
    Wear_tmp_id = find(ismember(Wear_id,ids{i}{2}));
    Xsens_tmp_id = find(ismember(Xsens_id,ids{i}{3}));
    min_size(i) = inf;
    
    Opti_cleaned(Opti_tmp_id).timestamp = timestamp_offseter(Xsens_cleaned(Xsens_tmp_id).timestamp(1), Opti_cleaned(Opti_tmp_id).timestamp);
    Wear_cleaned(Wear_tmp_id).timestamp = timestamp_offseter(Xsens_cleaned(Xsens_tmp_id).timestamp(1), Wear_cleaned(Wear_tmp_id).timestamp);
    
    if (min_size(i) > length(Opti_cleaned(Opti_tmp_id).timestamp))
        min_size(i) = length(Opti_cleaned(Opti_tmp_id).timestamp);
        min_name(i) = 1;
    end
    if (min_size(i) > length(Wear_cleaned(Wear_tmp_id).timestamp))
        min_size(i) = length(Wear_cleaned(Wear_tmp_id).timestamp);
        min_name(i) = 2;
    end
    if (min_size(i) > length(Xsens_cleaned(Xsens_tmp_id).timestamp))
        min_size(i) = length(Xsens_cleaned(Xsens_tmp_id).timestamp);
        min_name(i) = 3;
    end

    switch min_name(i)
        case 1
            [Wear_cleaned(Wear_tmp_id)] = timestamp_matching(Wear_cleaned(Wear_tmp_id), Opti_cleaned(Opti_tmp_id));
            [Xsens_cleaned(Xsens_tmp_id)] = timestamp_matching(Xsens_cleaned(Xsens_tmp_id), Opti_cleaned(Opti_tmp_id));
            
        case 2
            
            [Opti_cleaned(Opti_tmp_id)] = timestamp_matching(Opti_cleaned(Opti_tmp_id), Wear_cleaned(Wear_tmp_id));
            [Xsens_cleaned(Xsens_tmp_id)] = timestamp_matching(Xsens_cleaned(Xsens_tmp_id), Wear_cleaned(Wear_tmp_id));
            
        case 3
            
            [Wear_cleaned(Wear_tmp_id)] = timestamp_matching(Wear_cleaned(Wear_tmp_id), Xsens_cleaned(Xsens_tmp_id));
            [Opti_cleaned(Opti_tmp_id)] = timestamp_matching(Opti_cleaned(Opti_tmp_id), Xsens_cleaned(Xsens_tmp_id));
            
    end
end

for i = 1:length(Opti_cleaned)
    Opti_cleaned(i).quat = quaternion(Opti_cleaned(i).data);
end

for i = 1:length(Wear_cleaned)
    Wear_cleaned(i).data = [Wear_cleaned(i).data(:,3), Wear_cleaned(i).data(:,4), Wear_cleaned(i).data(:,2), Wear_cleaned(i).data(:,1)];
    Wear_cleaned(i).quat = quaternion(Wear_cleaned(i).data);
end

for i = 1:length(Xsens_cleaned)
    Xsens_cleaned(i).quat = quaternion(Xsens_cleaned(i).data);
end
%%
% Creat a figure with a plot of each fitting percentage for the Wearable
% data and the Xsens one compare them to the Ground truth (Optitrack). It
% uses the rotation quaternion from the Optitrack to the sensor and convert
% it to euler angles. Then an addition of the angles is perform and a
% metric is juste the sum/3. Not the most relevant metric but give an idea
% of the accuracy.

figure;
for i = 1:length(ids)
    Opti_tmp_id = find(ismember(Opti_id,ids{i}{1}));
    Wear_tmp_id = find(ismember(Wear_id,ids{i}{2}));
    Xsens_tmp_id = find(ismember(Xsens_id,ids{i}{3}));
    
    
    offet_quat_Wear = Opti_cleaned(Opti_tmp_id).quat(1)*Wear_cleaned(Wear_tmp_id).quat(1).conj;
    offet_quat_xsens = Opti_cleaned(Opti_tmp_id).quat(1)*Xsens_cleaned(Xsens_tmp_id).quat(1).conj;


    Wear_cleaned(Wear_tmp_id).quat_comp = offet_quat_Wear * Wear_cleaned(Wear_tmp_id).quat;
    Xsens_cleaned(Xsens_tmp_id).quat_comp = offet_quat_xsens * Xsens_cleaned(Xsens_tmp_id).quat;

    compar_values = Opti_cleaned(Opti_tmp_id).quat;
    Wear_fitting = [];
    Xsens_fitting = [];
    for p = 1:size(compar_values,1)
        Wear_fitting(p) = sum(abs(diag(quat2rotm(compar_values(p)*Wear_cleaned(Wear_tmp_id).quat_comp(p)))))*100/3;
        Xsens_fitting(p) = sum(abs(diag(quat2rotm(compar_values(p)*Xsens_cleaned(Xsens_tmp_id).quat_comp(p)))))*100/3;
    end
    subplot(3,2,i)
    plot(Wear_cleaned(Wear_tmp_id).timestamp, Wear_fitting);
    hold on;
    plot(Xsens_cleaned(Xsens_tmp_id).timestamp, Xsens_fitting);
    xlabel('Timstamp');
    ylabel('Fitting [%]');
    legend('BNO055','Xsens');
end

%%  
% This part is to stream the content of the selected body part to a UDP
% client. This will send the fully cleaned data, timestamp matched and
% offseted to match the Optitrack quaternion at the begining.


u = udp('127.0.0.1',5555);
fopen(u);
for i = 1
    Opti_tmp_id = find(ismember(Opti_id,ids{i}{1}));
    Wear_tmp_id = find(ismember(Wear_id,ids{i}{2}));
    Xsens_tmp_id = find(ismember(Xsens_id,ids{i}{3}));
    
    
    offet_quat_Wear = Opti_cleaned(Opti_tmp_id).quat(1)*Wear_cleaned(Wear_tmp_id).quat(1).conj;
    offet_quat_xsens = Opti_cleaned(Opti_tmp_id).quat(1)*Xsens_cleaned(Xsens_tmp_id).quat(1).conj;


    Wear_cleaned(Wear_tmp_id).quat_comp = offet_quat_Wear * Wear_cleaned(Wear_tmp_id).quat;
    Xsens_cleaned(Xsens_tmp_id).quat_comp = offet_quat_xsens * Xsens_cleaned(Xsens_tmp_id).quat;
    
    for p = 1:size(Wear_cleaned(Wear_tmp_id).quat_comp,1)
%     for p = 1:1
        [a,b,c,d] = parts(Opti_cleaned(Opti_tmp_id).quat(p));
        msg = strcat('Opti,', num2str(a),',', num2str(-b),',', num2str(c),',', num2str(d));
        fwrite(u,msg);
        msg
        quat2eul(Opti_cleaned(Opti_tmp_id).quat(p))
        [a,b,c,d] = parts(Wear_cleaned(Wear_tmp_id).quat_comp(p));
%         msg = strcat('Wear,', num2str(d),',', num2str(a),',', num2str(b),',', num2str(c));
        msg = strcat('Wear,', num2str(a),',', num2str(-b),',', num2str(c),',', num2str(d));
        fwrite(u,msg);
        msg
        quat2eul(Wear_cleaned(Wear_tmp_id).quat(p))
        [a,b,c,d] = parts(Xsens_cleaned(Xsens_tmp_id).quat_comp(p));
        msg = strcat('Xsens,', num2str(a),',', num2str(b),',', num2str(c),',', num2str(d));
        fwrite(u,msg);
        pause(0.1);
    end
    
end
fclose(u)