clc
close all


first = '/AtFirstTry/';
second = '/AtSecondTry/';
flat = 'flat';
linear = 'linear';
feedback = '_feedback1.csv';
names1 = {'timot','Syrin', 'Rokalito', 'LouisDom','Benoit'};
names2 = {'Pol','Max','Marco','Ludovic','Adrien'};


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

nb_of_subjects = 10;
figure()
plot(1:nb_of_subjects, linear_means,'o')
hold on 
errorbar(1:nb_of_subjects, linear_means, linear_stds)
title('Av. error and std dev. for each subject (linear shape)', 'FontSize', 15)
xlabel('Subject','FontSize', 14)
ylabel('Average error','FontSize', 14)

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

nb_of_subjects = 10;
figure()
plot(1:nb_of_subjects, flat_means,'b-o')
hold on 
errorbar(1:nb_of_subjects, flat_means, flat_stds)
plot(1:nb_of_subjects, linear_means,'o')
hold on 
errorbar(1:nb_of_subjects, linear_means, linear_stds)
h = legend('show')
set(h,'FontSize',12); 
legend('Step signal av. err. (distance)', 'Step signal std dev.','Linear signal av. err.(distance)','Linear signal std dev.')
title('Av. error and std dev. for each subject (step shape)', 'FontSize', 15)
xlabel('Subject','FontSize', 14)
ylabel('Average error','FontSize', 14)

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


reactTimeFlat = cell2mat(reactionTimeFlat)
figure()
hold on
plot(1:32,repmat(mean(reactTimeFlat),32,1), 'LineWidth',2)
plot(1:32,repmat(mean(reactTimeFlat),32,1) + repmat(std(reactTimeFlat),32,1),'r','LineWidth',1)
plot(1:32,repmat(mean(reactTimeFlat),32,1) - repmat(std(reactTimeFlat),32,1),'r', 'LineWidth',1)
for i =1:10
    plot(1:32,reactTimeFlat((i-1)*32+(1:32)))
end

h = legend('show')
set(h,'FontSize',12); 
legend('Av. reaction time', 'Std dev.')
title('Reaction time for each subject (step shape)', 'FontSize', 15)
ylim([0,9])
xlabel('Trials','FontSize', 14)
ylabel('Reaction time [s]','FontSize', 14)
%Reaction time plotting
%%
figure()
for i=1:10
    plot(i,mean(reactionTimeFlat{1,(i-1)*32 + 1 : (i-1)*32 + 32}))
    hold on
end

%%
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
    reactionTimeLinear{i} = str2num(allDataLinear{i}{3});
end

reactTimeLin = cell2mat(reactionTimeLinear)
figure()
hold on
plot(1:32,repmat(mean(reactTimeLin),32,1), 'LineWidth',2)
plot(1:32,repmat(mean(reactTimeLin),32,1) + repmat(std(reactTimeLin),32,1),'r','LineWidth',1)
plot(1:32,repmat(mean(reactTimeLin),32,1) - repmat(std(reactTimeLin),32,1),'r', 'LineWidth',1)
for i =1:10
    plot(1:32,reactTimeLin((i-1)*32+(1:32)))
end

h = legend('show')
set(h,'FontSize',12); 
legend('Av. reaction time', 'Std dev.')
title('Reaction time for each subject (linear shape)', 'FontSize', 15)
ylim([0,9])
xlabel('Trials','FontSize', 14)
ylabel('Reaction time [s]','FontSize', 14)


%%
labels = {'N','NE','E','SE','S','SW','W','NW'}
cat_labels = categorical(labels);
figure()
c = confusionmat(referenceFlatValues,feedbackFlatValues);
c_chart = confusionchart(c,cat_labels);
c_chart.RowSummary = 'row-normalized';
c_chart.ColumnSummary = 'column-normalized';
c_chart.Title = 'Direction identification with flat signal'
c_chart.sortClasses(cat_labels);

figure()
d = confusionmat(referenceLinearValues,feedbackLinearValues);
d_chart = confusionchart(d,cat_labels);
d_chart.NormalizedValues;
d_chart.RowSummary = 'row-normalized';
d_chart.ColumnSummary = 'column-normalized';
d_chart.Title = 'Direction identification with linear signal';
d_chart.sortClasses(cat_labels);

% %%
% counter = 0;
% for i = 1:length(referenceFlatValues)
%     if(referenceFlatValues{i} == feedbackFlatValues{i})
%         counter = counter + 1;
%     end
% end
% ratio = counter/length(referenceFlatValues) *100
% firstReferenceFlatValues = referenceFlatValues(1:length(names1)*length(flatLog));
% counter = 0;
% for i = 1:length(firstReferenceFlatValues)
%     if(firstReferenceFlatValues{i} == feedbackFlatValues{i})
%         counter = counter + 1;
%     end
% end
% ratio_first = counter/length(firstReferenceFlatValues) *100
% %% 
% counter = 0;
% for i = 1:length(referenceLinearValues)
%     if(referenceLinearValues{i} == feedbackLinearValues{i})
%         counter = counter + 1;
%     end
% end
% ratio = counter/length(referenceLinearValues) *100
% firstReferenceLinearValues = referenceFlatValues(1:length(names1)*length(linearLog));
% counter = 0;
% for i = 1:length(firstReferenceLinearValues)
%     if(firstReferenceLinearValues{i} == feedbackFlatValues{i})
%         counter = counter + 1;
%     end
% end
% ratio_first = counter/length(firstReferenceLinearValues) *100
% 
% %%
% labels = {'N','NE','E','SE','S','SW','W','NW'}
% cat_labels = categorical(labels)
% figure()
% c = confusionmat(firstReferenceFlatValues,feedbackFlatValues(1:length(names1)*length(flatLog)));
% c_chart = confusionchart(c,cat_labels);
% c_chart.RowSummary = 'row-normalized';
% c_chart.ColumnSummary = 'column-normalized';
% c_chart.Title = 'Direction identification with flat signal'
% c_chart.sortClasses(cat_labels)
% 
% figure()
% d = confusionmat(firstReferenceLinearValues,feedbackLinearValues(1:length(names1)*length(linearLog)));
% d_chart = confusionchart(d,cat_labels);
% d_chart.NormalizedValues;
% d_chart.RowSummary = 'row-normalized';
% d_chart.ColumnSummary = 'column-normalized';
% d_chart.Title = 'Direction identification with linear signal'
% d_chart.sortClasses(cat_labels)
% 
