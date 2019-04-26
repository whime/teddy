%存储为cell2csv.m 调用即可
function cell2csv(fileName, cellArray, separator, excelYear, decimal)

% % Writes cell array content into a *.csv file.
% % 
% % CELL2CSV(fileName, cellArray[, separator, excelYear, decimal])
% %
% % fileName     = Name of the file to save. [ e.g. 'text.csv' ]
% % cellArray    = Name of the Cell Array where the data is in
% % 
% % optional:
% % separator    = sign separating the values (default = ',')
% % excelYear    = depending on the Excel version, the cells are put into
% %                quotes before they are written to the file. The separator
% %                is set to semicolon (;)  (default = 1997 which does not change separator to semicolon ;)
% % decimal      = defines the decimal separator (default = '.')
% %
% %         by Sylvain Fiedler, KA, 2004
% % updated by Sylvain Fiedler, Metz, 06
% % fixed the logical-bug, Kaiserslautern, 06/2008, S.Fiedler
% % added the choice of decimal separator, 11/2010, S.Fiedler
% % modfiedy and optimized by Jerry Zhu, June, 2014, jerryzhujian9@gmail.com
% % now works with empty cells, numeric, char, string, row vector, and logical cells. 
% % row vector such as [1 2 3] will be separated by two spaces, that is "1  2  3"
% % One array can contain all of them, but only one value per cell.
% % 2x times faster than Sylvain's codes (8.8s vs. 17.2s):
% % tic;C={'te','tm';5,[1,2];true,{}};C=repmat(C,[10000,1]);cell2csv([datestr(now,'MMSS') '.csv'],C);toc;

%% Checking for optional Variables

if ~exist('separator', 'var')
    separator = ',';
end

if ~exist('excelYear', 'var')
    excelYear = 1997;
end

if ~exist('decimal', 'var')
    decimal = '.';
end

%% Setting separator for newer excelYears
if excelYear > 2000
    separator = ';';
end

[nrows,] = size(cellArray);%calculate the size
lnglatMat=cell2mat(cellArray(2:nrows,[4 5]));%transform to mat,and then write down
Re=num2str(lnglatMat(:,[1 2]),9);%change the digits
% convert cell
cellArray = cellfun(@StringX, cellArray, 'UniformOutput', false);

%% Write file
datei = fopen(fileName, 'w');


fprintf(datei,[cellArray{1,1} ',' cellArray{1,2} ',' cellArray{1,3} ',' cellArray{1,4} ',' cellArray{1,5} ',' cellArray{1,6} ',' cellArray{1,7} ',' cellArray{1,8} ',' cellArray{1,9} ',' cellArray{1,10} ',' cellArray{1,11} ',' cellArray{1,12} ',' cellArray{1,13} '\n']);
for row = 2:nrows
    fprintf(datei,[cellArray{row,1} ',' cellArray{row,2} ',' cellArray{row,3} ',' sprintf('%s',Re(row-1,1:13)) ',' sprintf('%s',Re(row-1,14:size(Re(row-1,:),2))) ',' cellArray{row,6} ',' cellArray{row,7} ',' cellArray{row,8} ',' cellArray{row,9} ',' cellArray{row,10} ',' cellArray{row,11} ',' cellArray{row,12} ',' cellArray{row,13} '\n']);
end    
% Closing file
fclose(datei);

% sub-function
function x = StringX(x)
    % If zero, then empty cell
    if isempty(x)
        x = '';
    % If numeric -> String, e.g. 1, [1 2]
    elseif isnumeric(x) && isrow(x)
        x = num2str(x);
        if decimal ~= '.'
            x = strrep(x, '.', decimal);
        end
    % If logical -> 'true' or 'false'
    elseif islogical(x)
        if x == 1
            x = 'TRUE';
        else
            x = 'FALSE';
        end
    % If matrix array -> a1 a2 a3. e.g. [1 2 3]
    % also catch string or char here
    elseif isrow(x) && ~iscell(x)
        x = num2str(x);
    % everthing else, such as [1;2], {1}
    else
        x = 'NA';
    end

    % If newer version of Excel -> Quotes 4 Strings
    if excelYear > 2000
        x = ['"' x '"'];
    end
end % end sub-function
end % end function
