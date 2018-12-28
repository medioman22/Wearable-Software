function [Wearable_cleaned] = Wearable_analyser(Wearable_file)
Wearable_data   =   importdata(Wearable_file);
C_wearable = {};
index = [];

for i = 1:length(Wearable_data.textdata(:,1))
    C_wearable{i,1} = strsplit(strcat(cell2mat(Wearable_data.textdata(i,1)),",",cell2mat(Wearable_data.textdata(i,2))));
    output = strsplit(C_wearable{i}{4},'@');
    if(strfind(output{1},'BNO055'))
        index = [index i];
    end 
end
Wearable_data.data = Wearable_data.data(index,:);
C_wearable =  C_wearable(index,:);

sensor_id = {};
timestamp = [];
for i = 1:length(Wearable_data.data(:,1))
    output = strsplit(C_wearable{i}{4},'@');
    time = strsplit(C_wearable{i}{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp(i) = ((h*60 + m)*60)+s;
    sensor_id{i} = (output{3}(end-1));   
end

Wearable_data.sensor_id = sensor_id';

Wearable_data.timestamp = timestamp;
%Wearable_cleaned.timestamp = unique(timestamp)';

nb_ids = length(unique(Wearable_data.sensor_id));

index = [];
for ids = 1:nb_ids
    Wearable_cleaned(ids).timestamp = [];
    
    
    for i = 1:length(Wearable_cleaned.timestamp)-3

        timestamp_index = [];
        timestamp_index = (Wearable_data.timestamp == Wearable_cleaned.timestamp(i));
        timestamp_index = timestamp_index + (Wearable_data.timestamp == Wearable_cleaned.timestamp(i+1));
        timestamp_index = timestamp_index + (Wearable_data.timestamp == Wearable_cleaned.timestamp(i+2));
        timestamp_index = timestamp_index >= 1;
        a = [Wearable_data.data(timestamp_index,1)];
        c = [Wearable_data.data(timestamp_index,3)];
        if(sum(sum(a== [12,13,14,15])) ==4)
            first_idx = find((a==12));
            first_idx = first_idx(1);
            if a(first_idx+1)==13 && a(first_idx+2)==14 && a(first_idx+3)==15
                Wearable_cleaned.sensor_id{i} = Wearable_data.sensor_id{find(timestamp_index,1)};
                Wearable_cleaned.quat(:,i) = [c(first_idx);c(first_idx+1);c(first_idx+2);c(first_idx+3)];
                index = [index i];
            else
                Wearable_cleaned.sensor_id{i} = 0;
                Wearable_cleaned.quat(:,i) = [0; 0; 0; 0];
            end
        else
            Wearable_cleaned.sensor_id{i} = 0;
            Wearable_cleaned.quat(:,i) = [0; 0; 0; 0];
        end
    end
end

end
