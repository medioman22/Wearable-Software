function [Xsens_out, Xsens_id] = Xsens_analyser2(Xsens_file)
Xsens_data   =   importdata(Xsens_file);

index = [];

for i = 1:length(Xsens_data.textdata(:,1))
    Xsens_data.textdata{i,3} = strsplit(strcat(cell2mat(Xsens_data.textdata(i,1)),",",cell2mat(Xsens_data.textdata(i,2))));
end
Xsens_data.textdata = Xsens_data.textdata(:,3);

for i = 1:length(Xsens_data.data(:,1))
    output = strsplit(Xsens_data.textdata{i}{4},'@');
    time = strsplit(Xsens_data.textdata{i}{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp(i) = ((h*60 + m)*60)+s;
    sensor_id{i} = (output{1}(7:end-1));   
end

Xsens_id = unique(sensor_id);
Xsens_cleaned = [];
for id = 1:length(Xsens_id)
    index = [];
    index = strcmp(sensor_id,Xsens_id(id));
    Xsens_cleaned(id).data = Xsens_data.data(index,:);
    Xsens_cleaned(id).timestamp = timestamp(index)';
end

Xsens_out = [];

for id = 1:length(Xsens_id)
    i = 1;
    while true
        if find((Xsens_cleaned(id).data(:,1)==1))
            first_idx = find((Xsens_cleaned(id).data(:,1)==1));
            first_idx = first_idx(1);

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
        else
            break;
        end
    end   
end


end