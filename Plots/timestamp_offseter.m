% Author: Victor Faraut
% Date: 27.12.2018

function [timestamp_list] = timestamp_offseter(first_timestamp, timestamp_list)

offset = first_timestamp - timestamp_list(1);
timestamp_list = timestamp_list + offset;


end