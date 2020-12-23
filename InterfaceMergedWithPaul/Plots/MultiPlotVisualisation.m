clc; clear all; close all;

% Plot file
file = "Beaglebone Green Wireless Multi Plot.csv";
data = table2cell(readtable(file, 'Format','%s%s%f%f'));
fprintf("Read File: '%s'\n", file);

% Display node (single/multi)
displayMode = "single";
fprintf("Display Mode: '%s'\n", displayMode);

% Convert unix timestamps to milliseconds normalized to first row equal 0
timeZero = uint64(data{1,3} * 1000);
for i = 1:size(data, 1)
    data{i,3} = uint64(data{i,3} * 1000) - timeZero;
end

% Labels and legend info
labels = unique(data(:,1));
legendInfo = {};

% Loop through all devices
for labelIdx = 1:length(labels)
    % Label
    label = labels{labelIdx};
    % Label rows
    labelRows = any(strcmp(data, label), 2);
    labelSubset = data(labelRows, :);

    % Switch on mode
    if (displayMode == "single")
       figure(labelIdx)
    end

    i = 0;
    while(1)
        % Subset of one dimension
        dimensionRows = any(strcmp(labelSubset, int2str(i)), 2);
        dimensionSubset = labelSubset(dimensionRows, :);
        
        % Break if not dimension found
        if (isempty(dimensionSubset))
            break;
        end
        
        
        % Draw plot and legend
        plot([dimensionSubset{:,3}],[dimensionSubset{:,4}]); hold on;
        legendInfo{end+1} = sprintf("%s [%d]", label, i);
                
        i = i + 1;        
    end
    
    % Switch on mode
    if (displayMode == "single")
        % Cosmetics
        legend(legendInfo)
        ylabel("Measured Values") 
        xlabel("Time [milliseconds]") 
        title(sprintf("Line Plot of: '%s'", label))
               
        % Reset
        legendInfo = {};
    end
end

% Switch on mode
if (displayMode == "multi")
    % Cosmetics
    legend(legendInfo)
    ylabel("Measured Values") 
    xlabel("Time [milliseconds]") 
    title(sprintf("Multi Line Plot of: '%s'", file))
end

