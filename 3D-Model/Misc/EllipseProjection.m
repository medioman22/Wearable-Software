clc
clear all
close all

X = [[5; 5].*rand(2,100) [-5; 5].*rand(2,100) [-5; -5].*rand(2,100) [5; -5].*rand(2,100)];
E = [45 45];
C = [-1;1];

X = X-C;

theta = atan2(X(2,:),X(1,:));
theta = linspace(0,2*pi,100);
k = 1./sqrt((E(2)*cos(theta)).^2 + (E(1)*sin(theta)).^2);
Y = [k.*E(1)*E(2).*cos(theta) ; k.*E(1)*E(2).*sin(theta)];
Y = Y;

figure
hold on
grid on
%plot(X(1,:), X(2,:), 'r*')
plot(Y(1,:), Y(2,:), 'g', 'LineWidth',3)
xlim([-100 100])
ylim([-80 120])
xlabel('Swing axis y','fontsize',40)
ylabel('Swing axis z','fontsize',40)

plot([0 30], [0 15], 'm--d', 'LineWidth',2, 'MarkerSize', 15)
plot([0 30], [0 50], 'r--d', 'LineWidth',2, 'MarkerSize', 15)
theta = atan2(deg2rad(50),deg2rad(30));
k = 1./sqrt((E(2)*cos(theta)).^2 + (E(1)*sin(theta)).^2);
Y = [k.*E(1)*E(2).*cos(theta) ; k.*E(1)*E(2).*sin(theta)];

plot([0 Y(1,:)], [0 Y(2,:)], 'b--d', 'LineWidth',2, 'MarkerSize', 15)
title('Limb swing angles','fontsize',40)
legend({'Saturation', 'Admissible swing', 'Unadmissible swing', 'Saturated swing'},'fontsize',30)
plot([-45 45], [0 0], 'k--')
plot([0 0], [-45 45], 'k--')