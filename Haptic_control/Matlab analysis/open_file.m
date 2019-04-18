function [dist] = open_file(file_name)
fileId = fopen(file_name);
lineData = fgetl(fileId);
i = 1;
while ischar(lineData)
    disp(lineData);
    d = str2num(lineData);
    if length(d) > 0
        dist(i,:) = d;
        i = i+1;
    end
    lineData = fgetl(fileId);
end
fclose(fileId);
end