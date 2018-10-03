clc
clear all
close all
format short
format compact

% latitude == sphere
% longitude == cylindre
P1.lon = deg2rad(33.86);
P1.lat = deg2rad(51);

P2.lon = deg2rad(18);
P2.lat = deg2rad(72);

f = 0.5; % f = [0;1]

% great circle angle
d = acos(cos(P1.lat)*cos(P2.lat) + sin(P1.lat)*sin(P2.lat)*cos(P1.lon-P2.lon));
greatAngle = rad2deg(d)

A = sin(1-f)*d/sin(d);
B = sin(f)*d/sin(d);

% carthesian coordinates of wanted point
x = A*sin(P1.lat)*cos(P1.lon) + B*sin(P2.lat)*cos(P2.lon);
y = A*sin(P1.lat)*sin(P1.lon) + B*sin(P2.lat)*sin(P2.lon);
z = A*cos(P1.lat) + B*cos(P2.lat);

% spherical coordinates of wanted point
P.r = sqrt(x^2 + y^2 + z^2);
P.lon = rad2deg(atan2(y,x));
P.lat = rad2deg(atan2(sqrt(x^2+y^2),z));
P