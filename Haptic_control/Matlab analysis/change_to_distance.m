function [dist] = change_to_distance(correct,given)

if strcmp(correct,'N')
    if strcmp(given,'NE') || strcmp(given,'NW')
        dist = 1;
    elseif strcmp(given,'N')
        dist = 0;
    elseif strcmp(given,'E') || strcmp(given,'W')
        dist = 2;
    elseif strcmp(given,'SE') || strcmp(given,'SW')
        dist = 3;
    else 
        dist = 4;
    end
end

if strcmp(correct,'S')
    if strcmp(given,'SE') || strcmp(given,'SW')
           dist = 1;
    elseif strcmp(given,'S')
        dist = 0;
    elseif strcmp(given,'E') || strcmp(given,'W')
        dist = 2;
    elseif strcmp(given,'NE') || strcmp(given,'NW')
        dist = 3;
    else 
        dist = 4;
    end
end

if strcmp(correct,'E')
    if strcmp(given,'NE') || strcmp(given,'SE')
           dist = 1;
    elseif strcmp(given,'E')
        dist = 0;
    elseif strcmp(given,'N') || strcmp(given,'S')
        dist = 2;
    elseif strcmp(given,'SW') || strcmp(given,'NW')
        dist = 3;
    else 
        dist = 4;
    end
end

if strcmp(correct,'W')
    if strcmp(given,'NE') || strcmp(given,'SE')
           dist = 3;
    elseif strcmp(given,'W')
        dist = 0;
    elseif strcmp(given,'N') || strcmp(given,'S')
        dist = 2;
    elseif strcmp(given,'SW') || strcmp(given,'NW')
        dist = 1;
    else 
        dist = 4;
    end
end;


if strcmp(correct,'NE')
    if strcmp(given,'N') || strcmp(given,'E')
           dist = 1;
    elseif strcmp(given,'NE')
        dist = 0;
    elseif strcmp(given,'NW') || strcmp(given,'SE')
        dist = 2;
    elseif strcmp(given,'W') || strcmp(given,'S')
        dist = 3;
    else 
        dist = 4;
    end
end
if strcmp(correct,'SW')
    if strcmp(given,'NE') || strcmp(given,'NW')
           dist = 3;
    elseif strcmp(given,'SW')
        dist = 0;
    elseif strcmp(given,'E') || strcmp(given,'W')
        dist = 2;
    elseif strcmp(given,'SE') || strcmp(given,'SW')
        dist = 1;
    else 
        dist = 4;
    end
end

if strcmp(correct,'NW')
    if strcmp(given,'N') || strcmp(given,'W')
           dist = 1;
    elseif strcmp(given,'NW')
        dist = 0;
    elseif strcmp(given,'SW') || strcmp(given,'NE')
        dist = 2;
    elseif strcmp(given,'S') || strcmp(given,'E')
        dist = 3;
    else 
        dist = 4;
    end
end


if strcmp(correct,'SE')
    if strcmp(given,'N') || strcmp(given,'W')
           dist = 3;
    elseif strcmp(given,'SE')
        dist = 0;
    elseif strcmp(given,'SW') || strcmp(given,'NE')
        dist = 2;
    elseif strcmp(given,'S') || strcmp(given,'E')
        dist = 1;
    else 
        dist = 4;
    end
end
