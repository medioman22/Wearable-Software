% Author: Victor Faraut
% Date: 29.12.2018

function [out_cleaned] = timestamp_matching(in_cleaned, matching_cleaned)

    index = [];
    for i = 1:length(matching_cleaned.timestamp)
        [~, index(i)] = min(abs(in_cleaned(1).timestamp - matching_cleaned(1).timestamp(i)));
    end
    for i = 1:length(in_cleaned)
        out_cleaned(i).timestamp = in_cleaned(i).timestamp(index);
%         out_cleaned(i).quat = in_cleaned(i).quat(index);
        out_cleaned(i).data = in_cleaned(i).data(index,:);
    end

end