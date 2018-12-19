clc
close all


first = '/AtFirstTry/';
second = '/AtSecondTry/';
flat = 'flat';
linear = 'linear';
feedback = '_feedback1.csv';
names1 = {'timot','Syrin', 'Rokalito', 'LouisDom','Benoit'};
names2 = {'Pol','Max','Marco','Ludovic','Adrien'};

for i = 1:length(names1)
    filename = strcat('logs/',flat,first,names1{i},'_','direction',flat,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     flatLog{j,i} = txt{2*j+1};
    end
end
for i = 1:length(names2)
    filename = strcat('logs/',flat,second,names2{i},'_','direction',flat,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     flatLog{j,i+length(names1)} = txt{2*j+1};
    end
end


%%
for i = 1:length(names2)
    filename = strcat('logs/',linear,first,names2{i},'_','direction',linear,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     linearLog{j,i} = txt{2*j+1};
    end
end
for i = 1:length(names1)
    filename = strcat('logs/',linear,second,names1{i},'_','direction',linear,feedback);
    [~,txt,~] = xlsread(filename);
    for j = 1:(length(txt)-1)/2;
     linearLog{j,i+length(names2)} = txt{2*j+1};
    end
end



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
    reactionTimeFlat{i} = allDataFlat{i}{3};
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
    reactionTimeLinear{i} = allDataLinear{i}{3};
end

%%
labels = {'N','NE','E','SE','S','SW','W','NW'}
cat_labels = categorical(labels)
figure()
c = confusionmat(referenceFlatValues,feedbackFlatValues);
c_chart = confusionchart(c,cat_labels);
c_chart.RowSummary = 'row-normalized';
c_chart.ColumnSummary = 'column-normalized';
c_chart.Title = 'Direction identification with flat signal'
c_chart.sortClasses(cat_labels)

figure()
d = confusionmat(referenceLinearValues,feedbackLinearValues);
d_chart = confusionchart(d,cat_labels);
d_chart.NormalizedValues;
d_chart.RowSummary = 'row-normalized';
d_chart.ColumnSummary = 'column-normalized';
d_chart.Title = 'Direction identification with linear signal'
d_chart.sortClasses(cat_labels)

%%
counter = 0;
for i = 1:length(referenceFlatValues)
    if(referenceFlatValues{i} == feedbackFlatValues{i})
        counter = counter + 1;
    end
end
ratio = counter/length(referenceFlatValues) *100
firstReferenceFlatValues = referenceFlatValues(1:length(names1)*length(flatLog));
counter = 0;
for i = 1:length(firstReferenceFlatValues)
    if(firstReferenceFlatValues{i} == feedbackFlatValues{i})
        counter = counter + 1;
    end
end
ratio_first = counter/length(firstReferenceFlatValues) *100
%% 
counter = 0;
for i = 1:length(referenceLinearValues)
    if(referenceLinearValues{i} == feedbackLinearValues{i})
        counter = counter + 1;
    end
end
ratio = counter/length(referenceLinearValues) *100
firstReferenceLinearValues = referenceFlatValues(1:length(names1)*length(linearLog));
counter = 0;
for i = 1:length(firstReferenceLinearValues)
    if(firstReferenceLinearValues{i} == feedbackFlatValues{i})
        counter = counter + 1;
    end
end
ratio_first = counter/length(firstReferenceLinearValues) *100

%%
labels = {'N','NE','E','SE','S','SW','W','NW'}
cat_labels = categorical(labels)
figure()
c = confusionmat(firstReferenceFlatValues,feedbackFlatValues(1:length(names1)*length(flatLog)));
c_chart = confusionchart(c,cat_labels);
c_chart.RowSummary = 'row-normalized';
c_chart.ColumnSummary = 'column-normalized';
c_chart.Title = 'Direction identification with flat signal'
c_chart.sortClasses(cat_labels)

figure()
d = confusionmat(firstReferenceLinearValues,feedbackLinearValues(1:length(names1)*length(linearLog)));
d_chart = confusionchart(d,cat_labels);
d_chart.NormalizedValues;
d_chart.RowSummary = 'row-normalized';
d_chart.ColumnSummary = 'column-normalized';
d_chart.Title = 'Direction identification with linear signal'
d_chart.sortClasses(cat_labels)

