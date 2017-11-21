clc
clear all
close all

cart = {};
Tag = 1; x = 2; y = 3; z = 4;

fid = fopen('plotting_1005.txt');
tline = fgetl(fid);
while ischar(tline)
    %disp(tline)
    C = strsplit(tline);
    cart = [cart; C(1) str2num(C{x}) str2num(C{y}) str2num(C{z})];
    tline = fgetl(fid);
end
fclose(fid);

figure
hold on
result = {};
for i = 1:length(cart)
    TAG = cart(i,Tag);
    X = cell2mat(cart(i,x));
    Y = cell2mat(cart(i,y));
    Z = cell2mat(cart(i,z));
    plot3(X,Y,Z,'r*');
    R = sqrt(X*X + Y*Y + Z*Z);
    X = R*X;
    Y = R*Y;
    Z = R*Z;
    cylindre = 180/pi*atan2(Y,X) - 90;
    spherical = 180/pi*atan2(Z,sqrt(X*X+Y*Y)) - 90;
    if spherical < 0
        spherical = -spherical;
        cylindre = cylindre + 180;
    end
    if cylindre > 180
        cylindre = cylindre - 360;
    end
    %spherical = spherical - 90;
    result = [result ; strcat(TAG, {' '}, 'Head', {' '}, num2str(0), {' '}, num2str(cylindre), {' '}, num2str(spherical))];
end
result
fid = fopen('result.txt','w');
for i = 1:length(result)
    fprintf(fid,result{i});
    fprintf(fid,'\r\n');
end
fclose(fid);