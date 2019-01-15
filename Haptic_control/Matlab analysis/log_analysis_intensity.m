clc 
close all


linear = '_intensitylinear_feedback1.csv';
linear_with_length = '_intensity_and_lengthlinear_feedback1.csv';
names = {'Roc','Maxim','Matteo','Ludo','LouisDom','Hugo','Brigitte'};
dim = [0.2 0.5 0.3 0.3];


%Storing the values from the csv
for i = 1:length(names)
    filename = strcat('logs/Intensity/',names{i},linear);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     IntensityLog{j,i} = txt{2*j+1};
    end
end

for i = 1:length(names)
    filename = strcat('logs/Intensity/',names{i},linear_with_length);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     IntensityAndLengthLog{j,i} = txt{2*j+1};
    end
end

%%
counter = 0;
for j = 1:length(names)
    for i =1:length(IntensityLog)
           temp = IntensityLog{i,j};
           allDataIntensity{i+counter} = strsplit(temp,',');
    end
    counter = counter + length(IntensityLog);
end

for i = 1:length(allDataIntensity)
    referenceIntensityValues{i} = allDataIntensity{i}{2};
    feedbackIntensityValues{i} = allDataIntensity{i}{1};
    reactionTimeIntensity{i} = str2num(allDataIntensity{i}{3});
end

a = 0
b = 0
for i = 1:length(referenceIntensityValues)
    a = a + strcmp(string(referenceIntensityValues{i}),string(feedbackIntensityValues{i}));
    b = b+1;
end
identification_rate = a/b
%%
counter = 0;
for j = 1:length(names)
    for i =1:length(IntensityAndLengthLog)
           temp = IntensityAndLengthLog{i,j};
           allDataIntensityAndLength{i+counter} = strsplit(temp,',');
    end
    counter = counter + length(IntensityAndLengthLog);
end

for i = 1:length(allDataIntensityAndLength)
    referenceIntensityAndLengthValues{i} = allDataIntensityAndLength{i}{2};
    feedbackIntensityAndLengthValues{i} = allDataIntensityAndLength{i}{1};
    reactionTimeIntensityAndLength{i} = str2num(allDataIntensityAndLength{i}{3});
end

a = 0
b = 0
for i = 1:length(referenceIntensityAndLengthValues)
    a = a + strcmp(string(referenceIntensityAndLengthValues{i}),string(feedbackIntensityAndLengthValues{i}));
    b = b+1;
end
identification_rate = a/b

%%
reactIntensityLinear = cell2mat(reactionTimeIntensity)


figure()
hold on
plot(1:20,repmat(mean(reactIntensityLinear),20,1), 'LineWidth',2)
plot(1:20,repmat(mean(reactIntensityLinear),20,1) + repmat(std(reactIntensityLinear),20,1),'r','LineWidth',1)
plot(1:20,repmat(mean(reactIntensityLinear),20,1) - repmat(std(reactIntensityLinear),20,1),'r', 'LineWidth',1)
for i =1:7
    plot(1:20,reactIntensityLinear((i-1)*20+(1:20)))
end

str = strcat('Av.  = ', num2str(mean(reactIntensityLinear)), ' [s]');
annotation('textbox',dim,'String',str,'FitBoxToText', 'on','FontSize', 14)

h = legend('show')
set(h,'FontSize',12); 
legend('Av. reaction time', 'Std dev.')
title('React. time for each subj. (only intensity variation)', 'FontSize', 15)
ylim([0,8])
xlabel('Trials','FontSize', 14)
ylabel('Reaction time [s]','FontSize', 14)

%%
reactIntensityAndLengthLinear = cell2mat(reactionTimeIntensityAndLength)


figure()
hold on
plot(1:20,repmat(mean(reactIntensityAndLengthLinear),20,1), 'LineWidth',2)
plot(1:20,repmat(mean(reactIntensityAndLengthLinear),20,1) + repmat(std(reactIntensityAndLengthLinear),20,1),'r','LineWidth',1)
plot(1:20,repmat(mean(reactIntensityAndLengthLinear),20,1) - repmat(std(reactIntensityAndLengthLinear),20,1),'r', 'LineWidth',1)
for i =1:7
    plot(1:20,reactIntensityAndLengthLinear((i-1)*20+(1:20)))
end

str = strcat('Av. react.tim = ', num2str(mean(reactIntensityAndLengthLinear)), ' [s]');
annotation('textbox',dim,'String',str,'FitBoxToText', 'on','FontSize', 14)

h = legend('show')
set(h,'FontSize',12); 
legend('Av. reaction time', 'Std dev.')
title('React. time for each subj. (Int. and duration variation)', 'FontSize', 15)
ylim([0,8])
xlabel('Trials','FontSize', 14)
ylabel('Reaction time [s]','FontSize', 14)


%%
labels = {'1','2','3','4','5'};
cat_labels = categorical(labels);
figure()
d = confusionmat(referenceIntensityValues,feedbackIntensityValues);
d_chart = confusionchart(d,cat_labels);
d_chart.NormalizedValues;
%d_chart.RowSummary = 'row-normalized';
%d_chart.ColumnSummary = 'column-normalized';
d_chart.Title = 'Intensity identification with only intensity changes';
d_chart.sortClasses(cat_labels);

figure()
d = confusionmat(referenceIntensityAndLengthValues,feedbackIntensityAndLengthValues);
d_chart = confusionchart(d,cat_labels);
d_chart.NormalizedValues;
%d_chart.RowSummary = 'row-normalized';
%d_chart.ColumnSummary = 'column-normalized';
d_chart.Title = 'Intensity identification with intensity and length changes';
d_chart.sortClasses(cat_labels);
