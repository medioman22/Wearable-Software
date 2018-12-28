clear all;

Opti_file =    "Recordings\123logfile_9000.log";
Xsens_file =        "Recordings\123logfile_12347.log";
Wear_file =     "Recordings\123logfile_12346.log";
for Opti_id = 10:10
    [Wear_cleaned, Wear_id] = Wearable_analyser2(Wear_file);
    [Xsens_cleaned, Xsens_id] = Xsens_analyser2(Xsens_file);
    Opti_cleaned = Optitrack_analyser(Opti_file);

    for i = 1:length(Opti_cleaned)
        Opti_cleaned(i).timestamp = timestamp_offseter(Xsens_cleaned.timestamp(1), Opti_cleaned(i).timestamp)
    end
    for i = 1:length(Wear_cleaned)
        Wear_cleaned(i).timestamp = timestamp_offseter(Xsens_cleaned.timestamp(1), Wear_cleaned(i).timestamp)
    end



    min_size = min([length(Opti_cleaned(1).timestamp),length(Wear_cleaned.timestamp),length(Xsens_cleaned.timestamp)]);
    if length(Opti_cleaned(1).timestamp) == min_size
        [Wear_cleaned] = timestamp_matching(Wear_cleaned, Opti_cleaned)
        [Xsens_cleaned] = timestamp_matching(Xsens_cleaned, Opti_cleaned)

    elseif length(Wear_cleaned.timestamp) == min_size
        [Opti_cleaned] = timestamp_matching(Opti_cleaned, Wear_cleaned)
        [Xsens_cleaned] = timestamp_matching(Xsens_cleaned, Wear_cleaned)

    elseif length(Xsens_cleaned.timestamp) == min_size
        [Opti_cleaned] = timestamp_matching(Opti_cleaned, Xsens_cleaned)
        [Wear_cleaned] = timestamp_matching(Wear_cleaned, Xsens_cleaned)
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
% for Opti_id = 1:21
    offet_quat_Wear = Opti_cleaned(Opti_id).quat(1)*Wear_cleaned(1).quat(1).conj;
    offet_quat_xsens = Opti_cleaned(Opti_id).quat(1)*Xsens_cleaned(1).quat(1).conj;


    Wear_cleaned(1).quat_comp = offet_quat_Wear * Wear_cleaned(1).quat;
    Xsens_cleaned(1).quat_comp = offet_quat_xsens * Xsens_cleaned(1).quat;

    compar_values = Opti_cleaned(Opti_id).quat;
    for i = 1:size(compar_values,1)
        Wear_fitting(i) = sum(abs(diag(quat2rotm(compar_values(i)*Wear_cleaned(1).quat_comp(i)))))/3;
    end

    for i = 1:size(compar_values,1)
        Xsens_fitting(i) = sum(abs(diag(quat2rotm(compar_values(i)*Xsens_cleaned(1).quat_comp(i)))))/3;
    end
    figure;
    plot(Wear_cleaned(1).timestamp, Wear_fitting);
    hold on;
    plot(Xsens_cleaned(1).timestamp, Xsens_fitting);
end