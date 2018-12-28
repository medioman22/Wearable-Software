function [Xsens_cleaned] = Xsens_analyser(Xsens_file)

Xsens_data      =   importdata(Xsens_file);

C_xsens = {};

for i = 1:length(Xsens_data.textdata(:,1))
    C_xsens{i,1} = strsplit(strcat(cell2mat(Xsens_data.textdata(i,1)),",",cell2mat(Xsens_data.textdata(i,2))));
end

sensor_id = {};
timestamp = [];
for i = 1:length(Xsens_data.data(:,1))
    output = strsplit(C_xsens{i}{4},'@');
    time = strsplit(C_xsens{i}{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp(i) = ((h*60 + m)*60)+s;
    sensor_id{i} =  output{1}(7:end-1);   
end

Xsens_data.sensor_id = sensor_id';
Xsens_data.timestamp = Xsens_data.data(:,2);
Xsens_cleaned.timestamp = unique(Xsens_data.data(:,2))';

index = [];
for i = 1:length(Xsens_cleaned.timestamp)
    timestamp_index = (Xsens_data.timestamp == Xsens_cleaned.timestamp(i));
     a = Xsens_data.data(timestamp_index,1);
     c = Xsens_data.data(timestamp_index,3);
    if(sum(sum(Xsens_data.data(timestamp_index,1)== [1,2,3,4])) ==4)
        Xsens_cleaned.sensor_id{i} = Xsens_data.sensor_id{find(timestamp_index,1)};
        Xsens_cleaned.quat(:,i) = [c(a==1);c(a==2);c(a==3);c(a==4)];
        index = [index i];
    else
        Xsens_cleaned.sensor_id{i} = 0;
        Xsens_cleaned.quat(:,i) = [0;0;0;0];
    end
end

end