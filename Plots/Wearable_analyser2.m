function [Wear_out, Wear_id] = Wearable_analyser2(Wear_file)
Wear_data   =   importdata(Wear_file);

index = [];

for i = 1:length(Wear_data.textdata(:,1))
    Wear_data.textdata{i,3} = strsplit(strcat(cell2mat(Wear_data.textdata(i,1)),",",cell2mat(Wear_data.textdata(i,2))));
    output = strsplit(Wear_data.textdata{i,3}{4},'@');
    if(strfind(output{1},'BNO055'))
        index = [index i];
    end 
end

Wear_data.data = Wear_data.data(index,:);
Wear_data.textdata = Wear_data.textdata(index,3);

for i = 1:length(Wear_data.data(:,1))
    output = strsplit(Wear_data.textdata{i}{4},'@');
    time = strsplit(Wear_data.textdata{i}{2},{':'});
    h = str2num(time{1});
    m = str2num(time{2});
    s = str2num(strrep((time{3}),',','.'));
    timestamp(i) = ((h*60 + m)*60)+s;
    sensor_id{i} = (output{3}(end-1));   
end

Wear_id = unique(sensor_id);
Wear_cleaned = [];
for id = 1:length(Wear_id)
    index = [];
    index = strcmp(sensor_id,Wear_id(id));
    Wear_cleaned(id).data = Wear_data.data(index,:);
    Wear_cleaned(id).timestamp = timestamp(index)';
end

Wear_out = [];

for id = 1:length(Wear_id)
    i = 1;
    while true
        if find((Wear_cleaned(id).data(:,1)==12))
            first_idx = find((Wear_cleaned(id).data(:,1)==12));
            first_idx = first_idx(1);

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
        else
            break;
        end
    end   
end


end



