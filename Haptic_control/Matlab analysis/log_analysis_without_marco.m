clc
close all


first = '/AtFirstTry/';
second = '/AtSecondTry/';
flat = 'flat';
linear = 'linear';
feedback = '_feedback1.csv';
names1 = {'timot','Syrin', 'Rokalito', 'LouisDom','Benoit'};
names2 = {'Pol','Max','Ludovic','Adrien'};


%Storing the values from the csv
for i = 1:length(names1)
    filename = strcat('logs/Guidance/',flat,first,names1{i},'_','direction',flat,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     flatLog{j,i} = txt{2*j+1};
    end
end
for i = 1:length(names2)
    filename = strcat('logs/Guidance/',flat,second,names2{i},'_','direction',flat,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     flatLog{j,i+length(names1)} = txt{2*j+1};
    end
end


%%Storing the values from the csv
for i = 1:length(names2)
    filename = strcat('logs/Guidance/',linear,first,names2{i},'_','direction',linear,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     linearLog{j,i} = txt{2*j+1};
    end
end
for i = 1:length(names1)
    filename = strcat('logs/Guidance/',linear,second,names1{i},'_','direction',linear,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     linearLog{j,i+length(names2)} = txt{2*j+1};
    end
end

%%
[linearRow, linearCol] = size(linearLog);
linear_distances = zeros(linearRow, linearCol);
linear_means = zeros(1, linearCol);
linear_stds = zeros(1,linearCol);
for col = 1:linearCol

    for row = 1:linearRow
        temp = linearLog{row, col};
        temp2 = strsplit(temp,',');
        correct = temp2{1};
        given = temp2{2};
        linear_distances(row,col) = change_to_distance(correct, given);
    end
    linear_means(1,col) = mean(linear_distances(:,col));
    if any(linear_distances(:,col)) == 1
        linear_stds(1,col) = std(linear_distances(:,col));
    end
end

nb_of_subjects = 9;
figure()
plot(1:nb_of_subjects, linear_means,'o')
hold on 
errorbar(1:nb_of_subjects, linear_means, linear_stds)
title('Av. error and std dev. for each subject (linear shape)', 'FontSize', 15)
xlim([0,10])
xlabel('Subject','FontSize', 14)
ylabel('Average error','FontSize', 14)
rate = length(find(~linear_distances))/linearRow/linearCol


%%
[flatRow, flatCol] = size(flatLog);
flat_distances = zeros(flatRow, flatCol);
flat_means = zeros(1, flatCol);
flat_stds = zeros(1,flatCol);
for col = 1:flatCol

    for row = 1:flatRow
        temp = flatLog{row, col};
        temp2 = strsplit(temp,',');
        correct = temp2{1};
        given = temp2{2};
        flat_distances(row,col) = change_to_distance(correct, given);
    end
    flat_means(1,col) = mean(flat_distances(:,col));
    if any(flat_distances(:,col)) == 1
        flat_stds(1,col) = std(flat_distances(:,col));
    end
end

nb_of_subjects = 9;
figure()
plot(1:nb_of_subjects, flat_means,'b-o')
hold on 
errorbar(1:nb_of_subjects, flat_means, flat_stds)
plot(1:nb_of_subjects, linear_means,'o')
hold on 
errorbar(1:nb_of_subjects, linear_means, linear_stds)
h = legend('show')
set(h,'FontSize',12); 
legend('Step signal av. err.', 'Step signal std dev.','Linear signal av. err.','Linear signal std dev.')
title('Av. error  and std dev. for each subject', 'FontSize', 15)
xlim([0,10])
ylim([-0.6,1])
xlabel('Subject','FontSize', 14)
ylabel('Average error','FontSize', 14)

rate = length(find(~flat_distances))/flatRow/linearCol


%%

%%
counter = 0;
for j = 1:length(names1)+length(names2)
    for i =1:length(flatLog)
           temp = flatLog{i,j};
           allDataFlat{i+counter} = strsplit(temp,',');
    end
    counter = counter + length(flatLog);
end

for i = 1:length(allDataFlat)
    referenceFlatValues{i} = allDataFlat{i}{2};
    feedbackFlatValues{i} = allDataFlat{i}{1};
    reactionTimeFlat{i} = str2num(allDataFlat{i}{3});
end

counter = 0;
for j = 1:length(names1)+length(names2)
    for i =1:length(linearLog)
           temp = linearLog{i,j};
           allDataLinear{i+counter} = strsplit(temp,',');
    end
    counter = counter + length(flatLog);
end

for i = 1:length(allDataLinear)
    referenceLinearValues{i} = allDataLinear{i}{2};
    feedbackLinearValues{i} = allDataLinear{i}{1};
    reactionTimeLinear{i} = allDataLinear{i}{3};
end

%%
labels = {'N','NE','E','SE','S','SW','W','NW'}
cat_labels = categorical(labels);

figure()
c = confusionmat(referenceFlatValues,feedbackFlatValues);
c_chart = confusionchart(c,cat_labels);
%c_chart.RowSummary = 'row-normalized';
%c_chart.ColumnSummary = 'column-normalized';
c_chart.Title = 'Direction identification with flat signal'
c_chart.sortClasses(cat_labels);

figure()
d = confusionmat(referenceLinearValues,feedbackLinearValues);
d_chart = confusionchart(d,cat_labels);
d_chart.NormalizedValues;
%d_chart.RowSummary = 'row-normalized';
%d_chart.ColumnSummary = 'column-normalized';
d_chart.Title = 'Direction identification with linear signal';
d_chart.sortClasses(cat_labels);

%%
figure
set(findobj(gca,'Type','text'),'FontSize',14)
boxplot([flat_means',linear_means'],'Labels',{'step shape','linear shape'})
ylim([-0.1,0.5])
title('Av. error for step and linear shaped signals', 'FontSize', 15)

%%
figure
c = categorical({'Step','linear'});
bar(c, [2.117,2.057])
hold on
errorbar(c,[2.117,2.057], [0.754,0.490],'.','LineWidth',2)
ylabel('Reaction time [s]','FontSize', 14)
title('Reaction time for both signal shape', 'FontSize', 15)



%%
figure
bar(c, [80.02,82.30])
title('Correct identification rate', 'FontSize', 15)
ylim([50,90])
ylabel('Identification rate [ % ]','FontSize', 14)


%% 
figure
c = categorical({'intensity','intensity + duration'});
bar(c, [64.29,53.57])
title('Correct identification (for intensity)', 'FontSize', 15)
ylim([0,100])
ylabel('Identification rate [ % ]','FontSize', 14)

