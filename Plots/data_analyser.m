% Author: Victor Faraut
% Date: 09.01.2019



%% 
% Load alle the data from the files selected and stores them localy in
% a matlab array of structurs as well as a array of the IDs of the sensors

clear all;

% Change here the file path for different experiment analysis. 
Opti_file =    "Recordings\Test-5-sensors-29-12-2018-bis\1546099115_logfile_9000.log";
Wear_file =    "Recordings\Test-5-sensors-29-12-2018-bis\1546099115_logfile_12346.log";
Xsens_file =   "Recordings\Test-5-sensors-29-12-2018-bis\1546099115_logfile_12347.log";


% Define the IDs of the sensor for each body part in the order
% (optritrack, Wearable, Xsens) . NOTE: the optitrack doesn't need to have
% the accurate ID. It's the relative ID between the first ID and this one.
% E.g. 43523 => 1 and so 43527 => 5
Hand_id = {'13', '20', '00B43C3A'};
Forearm_id = {'12', '21', '00B4221D'}; 
Upperarm_id = {'11', '22', '00B42217'}; 
Shoulder_id = {'10', '23', '00B42235'}; 
Torso_id = {'3', '24', '00B43C41'}; 

ids = {Hand_id, Forearm_id, Upperarm_id, Shoulder_id, Torso_id};

%load all the file data into matlab variables for further pre processing
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
    % Select the right sensor to compare with as they all have a specific
    % ID number, it's important to compare thing that are comparable. The
    % sensor IDs must be note down before or after placing the sensor on
    % the body and the matching sensor IDs must be written at the begining
    % of this file.
    Opti_tmp_id = find(ismember(Opti_id,ids{i}{1}));
    Wear_tmp_id = find(ismember(Wear_id,ids{i}{2}));
    Xsens_tmp_id = find(ismember(Xsens_id,ids{i}{3}));
    min_size(i) = inf;
    
    
    % Match the timestamp of the first Xsens value with the other for the
    % to begin at the same time. Normally the case
    Opti_cleaned(Opti_tmp_id).timestamp = timestamp_offseter(Xsens_cleaned(Xsens_tmp_id).timestamp(1), Opti_cleaned(Opti_tmp_id).timestamp);
    Wear_cleaned(Wear_tmp_id).timestamp = timestamp_offseter(Xsens_cleaned(Xsens_tmp_id).timestamp(1), Wear_cleaned(Wear_tmp_id).timestamp);
    
    
    % find the sensor with less data and match the data of the other to
    % have the same amount of data in all of them. This is done by finding
    % the sensor with less data in and finding for each one the other
    % sensor closest values (regarding the timestamp).
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
% converts the current quaternion stored in a simple double array into a
% matlab quaternion object to do computation.
for i = 1:length(Opti_cleaned)
    Opti_cleaned(i).quat = quaternion(Opti_cleaned(i).data);
end

for i = 1:length(Wear_cleaned)
    % As the BNO055 doesn't have the same reference frame as the Optitrack,
    % a modification in orientation is performed here to convert the
    % orignial WXYZ form to the classic XYZW form.
    
    %Wear_cleaned(i).data = [Wear_cleaned(i).data(:,3), Wear_cleaned(i).data(:,4), Wear_cleaned(i).data(:,2), Wear_cleaned(i).data(:,1)];
    Wear_cleaned(i).quat = quaternion(Wear_cleaned(i).data);
end

for i = 1:length(Xsens_cleaned)
    Xsens_cleaned(i).quat = quaternion(Xsens_cleaned(i).data);
end
%%
% Creat a figure with a plot of each error percentage for the Wearable
% data and the Xsens one compare them to the Ground truth (Optitrack). It
% uses the rotation quaternion from the Optitrack to the sensor and convert
% it to euler angles. Then an addition of the angles is perform and a
% metric is juste the sum/3. Not the most relevant metric but give an idea
% of the accuracy.
Wear_error = {};
Xsens_error = {};
    
figure;
for i = 1:length(ids)
    
    % Select the right sensor to compare with as they all have a specific
    % ID number, it's important to compare thing that are comparable. The
    % sensor IDs must be note down before or after placing the sensor on
    % the body and the matching sensor IDs must be written at the begining
    % of this file.
    Opti_tmp_id = find(ismember(Opti_id,ids{i}{1}));
    Wear_tmp_id = find(ismember(Wear_id,ids{i}{2}));
    Xsens_tmp_id = find(ismember(Xsens_id,ids{i}{3}));
    
    % Rotate the uqaternion from the Xsens and the Wearable to allow them
    % to rotate in the same direction and so be comparable.
    eul = [0 -pi/2  pi/2];
    qZYX = quaternion(eul2quat(eul));
    Wear_tmp_quat = Wear_cleaned(Wear_tmp_id).quat * qZYX;
    eul = [pi/2 pi 0];
    qZYX = quaternion(eul2quat(eul));
    Xsens_tmp_quat = Xsens_cleaned(Xsens_tmp_id).quat * qZYX;
    
    
    % Compute an apply a offset to the quaternion to have the first
    % quaternion to match between all the sensing devices. 
    offset_quat_Wear = Opti_cleaned(Opti_tmp_id).quat(1)*Wear_tmp_quat(1).conj;
    offset_quat_xsens = Opti_cleaned(Opti_tmp_id).quat(1)*Xsens_tmp_quat(1).conj;
    Wear_tmp_quat = offset_quat_Wear * Wear_tmp_quat;
    Xsens_tmp_quat = offset_quat_xsens * Xsens_tmp_quat;
    
    
    % Compare the different data with the "ground truth" (optitrack). This
    % is done computing the rotation quaternion between the optitrack quat
    % and the sensor quat. Then converting this rotatation into euler
    % angles and performing a sum on all of them. This gives us a metric
    % that is dépendant one the accuracy of the sensor compared to the
    % optitrack
    % NOTE: this metric is realy dependant on the first value offset and so
    % is more indicative than a true value that we can base other
    % measurment on.
    compar_values = Opti_cleaned(Opti_tmp_id).quat;

    for p = 1:size(compar_values,1)
        Wear_error{i}(p) = 100*(sum(abs(quat2eul(compar_values(p)*Wear_tmp_quat(p).conj)/pi)))./2;
        Xsens_error{i}(p) = 100*(sum(abs(quat2eul(compar_values(p)*Xsens_tmp_quat(p).conj)/pi)))./2;
    end
    
    
    %Plot all the error data on a plot to compare the value for the
    %torso, shoulder, upper arm forearm and hand.
    subplot(3,2,i)
    first_time = Wear_cleaned(Wear_tmp_id).timestamp(1);
    plot(Wear_cleaned(Wear_tmp_id).timestamp-first_time, Wear_error{i});
    hold on;
    first_time = Xsens_cleaned(Xsens_tmp_id).timestamp(1);
    plot(Xsens_cleaned(Xsens_tmp_id).timestamp-first_time, Xsens_error{i});
    xlabel('Time[s]');
    ylabel('Error [%]');
    legend('BNO055','Xsens');
    grid on;
    switch i
        case 1
            title('Hand');
        case 2 
            title('Forearm');
        case 3
            title('Upper arm');
        case 4
            title('Shoulder');
        case 5
            title('Torso');
    end
    %axis([xlim 0 100])
end
figure;
for i = 1:length(ids)
    subplot(3,2,i);
    boxplot([Wear_error{i}',Xsens_error{i}'], {'Wear','Xsens'},'whisker',4);
    grid on;
    switch i
        case 1
            title('Hand');
        case 2 
            title('Forearm');
        case 3
            title('Upper arm');
        case 4
            title('Shoulder');
        case 5
            title('Torso');
    end
end
subplot(3,2,6);
boxplot([[Wear_error{1},Wear_error{2},Wear_error{3},Wear_error{4},Wear_error{5}]',...
    [Xsens_error{1},Xsens_error{2},Xsens_error{3},Xsens_error{4},Xsens_error{5}]'], {'Wear','Xsens'},'whisker',4);
title('All  parts together');

grid on;

%%  
% This part is to stream the content of the selected body part to a UDP
% client. This will send the fully cleaned data, timestamp matched and
% offseted to match the Optitrack quaternion at the begining.

% Udp streaming port creation. If another port is needed, please change it
% here.
u = udp('127.0.0.1',5555);
fopen(u);

% You can select which one of the body part you want to stream. You can
% also stream multiple body part one after the other by using the for loop
% here.
for i = 3
    
    % Select the right sensor to compare with as they all have a specific
    % ID number, it's important to compare thing that are comparable. The
    % sensor IDs must be note down before or after placing the sensor on
    % the body and the matching sensor IDs must be written at the begining
    % of this file.
    Opti_tmp_id = find(ismember(Opti_id,ids{i}{1}));
    Wear_tmp_id = find(ismember(Wear_id,ids{i}{2}));
    Xsens_tmp_id = find(ismember(Xsens_id,ids{i}{3}));
    
    
    % Rotate the uqaternion from the Xsens and the Wearable to allow them
    % to rotate in the same direction and so be comparable.
    eul = [0 -pi/2  pi/2];
    qZYX = quaternion(eul2quat(eul));
    Wear_tmp_quat = Wear_cleaned(Wear_tmp_id).quat * qZYX;
    eul = [pi/2 pi 0];
    qZYX = quaternion(eul2quat(eul));
    Xsens_tmp_quat = Xsens_cleaned(Xsens_tmp_id).quat * qZYX;
    
    % Compute an apply a offset to the quaternion to have the first
    % quaternion to match between all the sensing devices. 
    offset_quat_Wear = Opti_cleaned(Opti_tmp_id).quat(1)*Wear_tmp_quat(1).conj;
    offset_quat_xsens = Opti_cleaned(Opti_tmp_id).quat(1)*Xsens_tmp_quat(1).conj;
    Wear_tmp_quat = offset_quat_Wear * Wear_tmp_quat;
    Xsens_tmp_quat = offset_quat_xsens * Xsens_tmp_quat;
    
    % send to the UDP port and IP the message of all the quaternion one at
    % a time. A delay is added to simulate real data or just to better
    % understand what is going on. The delay (pause) can be change to have
    % more slow or quick data streaming.
    for p = 1:size(Wear_tmp_quat,1)
        [a,b,c,d] = parts(Opti_cleaned(Opti_tmp_id).quat(p));
        msg = strcat('Opti,', num2str(a),',', num2str(b),',', num2str(c),',', num2str(d));
        fwrite(u,msg);
        [a,b,c,d] = parts(Wear_tmp_quat(p));
        msg = strcat('Wear,', num2str(a),',', num2str(b),',', num2str(c),',', num2str(d));
        fwrite(u,msg);
        [a,b,c,d] = parts(Xsens_tmp_quat(p));
        msg = strcat('Xsens,', num2str(a),',', num2str(b),',', num2str(c),',', num2str(d));
        fwrite(u,msg);
        pause(0.005);
    end
    
end
fclose(u)