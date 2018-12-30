clear all;

Opti_file =    "Recordings\Test-5-sensors-29-12-2018-bis\1546099003_logfile_9000.log";
Wear_file =    "Recordings\Test-5-sensors-29-12-2018-bis\1546099003_logfile_12346.log";
Xsens_file =   "Recordings\Test-5-sensors-29-12-2018-bis\1546099003_logfile_12347.log";

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

min_size = [];
for i = 1:length(ids)
    Opti_tmp_id = find(contains(Opti_id,ids{i}{1}));
    Wear_id = find(contains(Wear_id,ids{i}{2}))
    Xsens_tmp_id = find(contains(Xsens_id,ids{i}{3}));
    min_size(i) = inf;
    
    Opti_cleaned(Opti_tmp_id).timestamp = timestamp_offseter(Xsens_cleaned(Xsens_id).timestamp(1), Opti_cleaned(Opti_tmp_id).timestamp);
    Wear_cleaned(Wear_id).timestamp = timestamp_offseter(Xsens_cleaned(Xsens_id).timestamp(1), Wear_cleaned(Wear_id).timestamp);
    
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
    Wear_cleaned(i).quat = quaternion(Wear_cleaned(i).data);
end

for i = 1:length(Xsens_cleaned)
    Xsens_cleaned(i).quat = quaternion(Xsens_cleaned(i).data);
end
% 
for i = 1:length(ids)
    Opti_tmp_id = find(contains(Opti_id,ids{i}{1}));
    Wear_id = find(contains(Wear_id,ids{i}{2}))
    Xsens_tmp_id = find(contains(Xsens_id,ids{i}{3}));
    
    
    offet_quat_Wear = Opti_cleaned(Opti_tmp_id).quat(1)*Wear_cleaned(Wear_tmp_id).quat(1).conj;
    offet_quat_xsens = Opti_cleaned(Opti_tmp_id).quat(1)*Xsens_cleaned(Xsens_tmp_id).quat(1).conj;


    Wear_cleaned(Wear_tmp_id).quat_comp = offet_quat_Wear * Wear_cleaned(Wear_tmp_id).quat;
    Xsens_cleaned(Xsens_tmp_id).quat_comp = offet_quat_xsens * Xsens_cleaned(Xsens_tmp_id).quat;

    compar_values = Opti_cleaned(Opti_tmp_id).quat;
    for i = 1:size(compar_values,1)
        Wear_fitting(i) = sum(abs(diag(quat2rotm(compar_values(i)*Wear_cleaned(Wear_tmp_id).quat_comp(i)))))/3;
        Xsens_fitting(i) = sum(abs(diag(quat2rotm(compar_values(i)*Xsens_cleaned(Xsens_tmp_id).quat_comp(i)))))/3;
    end
    figure;
    plot(Wear_cleaned(1).timestamp, Wear_fitting);
    hold on;
    plot(Xsens_cleaned(1).timestamp, Xsens_fitting);
end