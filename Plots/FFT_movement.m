function [] = FFT_movement(Cleaned_data)
Fs = (Cleaned_data(end).timestamp(13)-Cleaned_data(end).timestamp(2))/10;

Y = fft(Cleaned_data(end).data(:,2));
L= length(Cleaned_data(end).data(:,1));
P2 = abs(Y/L);
P1 = P2(floor(1:L/2+1));
P1(2:end-1) = 2*P1(2:end-1);
f = Fs*(0:(L/2))/L;
plot(f,P1) 
xlabel('f (Hz)')
ylabel('|P1(f)|')
end

