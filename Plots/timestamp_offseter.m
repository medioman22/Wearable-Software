function [timestamp_list] = timestamp_offseter(first_timestamp, timestamp_list)

offset = first_timestamp - timestamp_list(1);
timestamp_list = timestamp_list + offset;


end